import asyncio
import ssl
import logging
import dns.resolver
import httpx
import shodan

logger = logging.getLogger("nodesec.osint")

CRTSH_URL = "https://crt.sh/?q=%25.{}&output=json"
CERTSPOTTER_URL = "https://api.certspotter.com/v1/issuances?domain={}&include_subdomains=true&expand=dns_names"
OTX_URL = "https://otx.alienvault.com/api/v1/indicators/domain/{}/passive_dns"
SHODAN_INTERNETDB_URL = "https://internetdb.shodan.io/{}"

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3306, 3389, 5432, 8080, 8443]


def _make_client(timeout: float = 15.0) -> httpx.AsyncClient:
    """
    Create an httpx client that forces IPv4.
    Docker on Windows only routes IPv4 correctly — IPv6 connections fail silently.
    """
    transport = httpx.AsyncHTTPTransport(local_address="0.0.0.0")
    return httpx.AsyncClient(timeout=timeout, transport=transport)


# ── Subdomain Discovery (multi-source) ──

async def subdomain_discovery(domain: str) -> list[str]:
    """Passive subdomain discovery from multiple free sources. No requests to target."""
    results = await asyncio.gather(
        _crt_sh_subdomains(domain),
        _certspotter_subdomains(domain),
        _otx_subdomains(domain),
        return_exceptions=True,
    )
    combined = set()
    for result in results:
        if isinstance(result, list):
            combined.update(result)
    combined.discard(domain)
    return sorted(combined)[:100]


async def _crt_sh_subdomains(domain: str) -> list[str]:
    """crt.sh certificate transparency logs."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(CRTSH_URL.format(domain))
            if resp.status_code != 200:
                logger.warning(f"crt.sh returned {resp.status_code} for {domain}")
                return []
            entries = resp.json()
            subdomains = set()
            for entry in entries:
                name = entry.get("name_value", "").lower().strip()
                for n in name.split("\n"):
                    n = n.strip()
                    if n.startswith("*."):
                        n = n[2:]
                    if n and n.endswith(domain):
                        subdomains.add(n)
            return list(subdomains)
    except Exception as e:
        logger.warning(f"crt.sh failed for {domain}: {e}")
        return []


async def _certspotter_subdomains(domain: str) -> list[str]:
    """CertSpotter API — free, no API key needed."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(CERTSPOTTER_URL.format(domain))
            if resp.status_code != 200:
                return []
            subdomains = set()
            for issuance in resp.json():
                for name in issuance.get("dns_names", []):
                    name = name.lower().strip()
                    if name.endswith(domain):
                        subdomains.add(name)
            return list(subdomains)
    except Exception as e:
        logger.warning(f"CertSpotter failed for {domain}: {e}")
        return []


async def _otx_subdomains(domain: str) -> list[str]:
    """AlienVault OTX passive DNS — free, no API key needed for basic lookups."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(OTX_URL.format(domain))
            if resp.status_code != 200:
                return []
            entries = resp.json().get("passive_dns", [])
            subdomains = set()
            for entry in entries:
                hostname = entry.get("hostname", "").lower().strip()
                if hostname.endswith(domain) and hostname != domain:
                    subdomains.add(hostname)
            return list(subdomains)
    except Exception as e:
        logger.warning(f"OTX failed for {domain}: {e}")
        return []


# ── DNS Records ──

async def dns_records(domain: str) -> dict:
    """Passive DNS record lookup via dnspython. No requests to target domain."""
    result = {"A": [], "MX": [], "NS": [], "TXT": [], "CNAME": []}
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        for rtype in ["A", "MX", "NS", "TXT", "CNAME"]:
            try:
                answers = resolver.resolve(domain, rtype)
                result[rtype] = [str(a) for a in answers][:10]
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"dns_records failed for {domain}: {e}")
    return result


# ── Email Security Checks ──

async def email_security_checks(domain: str) -> dict:
    """
    Check SPF, DKIM, DMARC, and MX configuration.
    These are truly passive — DNS queries only.
    """
    checks = {
        "spf": False,
        "spf_record": None,
        "dkim": False,
        "dmarc": False,
        "dmarc_policy": None,
        "dmarc_record": None,
        "mx_count": 0,
        "mx_hosts": [],
        "has_recommendations": False,
    }

    # SPF check
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        answers = resolver.resolve(domain, "TXT")
        for a in answers:
            txt = str(a).strip('"').strip("'")
            if txt.startswith("v=spf1"):
                checks["spf"] = True
                checks["spf_record"] = txt
                break
    except Exception:
        pass

    # DMARC check
    try:
        answers = resolver.resolve(f"_dmarc.{domain}", "TXT")
        for a in answers:
            txt = str(a).strip('"').strip("'")
            if txt.startswith("v=DMARC1"):
                checks["dmarc"] = True
                checks["dmarc_record"] = txt
                txt_lower = txt.lower()
                if "p=reject" in txt_lower:
                    checks["dmarc_policy"] = "reject"
                elif "p=quarantine" in txt_lower:
                    checks["dmarc_policy"] = "quarantine"
                elif "p=none" in txt_lower:
                    checks["dmarc_policy"] = "none"
                break
    except Exception:
        pass

    # DKIM check — look for common selector patterns
    common_selectors = ["default", "google", "selector1", "selector2", "dkim", "mail", "key1"]
    for selector in common_selectors:
        try:
            answers = resolver.resolve(f"{selector}._domainkey.{domain}", "TXT")
            for a in answers:
                txt = str(a).strip('"').strip("'")
                if "v=DKIM1" in txt or "k=rsa" in txt:
                    checks["dkim"] = True
                    break
            if checks["dkim"]:
                break
        except Exception:
            continue

    # MX count
    try:
        answers = resolver.resolve(domain, "MX")
        mx_list = sorted([(a.preference, str(a.exchange).rstrip(".")) for a in answers])
        checks["mx_count"] = len(mx_list)
        checks["mx_hosts"] = [host for _, host in mx_list]
    except Exception:
        pass

    checks["has_recommendations"] = not (checks["spf"] and checks["dmarc"] and checks["dmarc_policy"] == "reject")
    return checks


# ── Shodan API & InternetDB (fallback) ──

async def shodan_lookup(host: str, api_key: str | None = None) -> dict:
    """
    Query Shodan for open ports, CVEs, and tags.
    If api_key is provided, uses the authenticated Shodan API.
    Falls back to the free InternetDB API if no key is provided or if the authenticated API fails.
    """
    if api_key:
        try:
            api = shodan.Shodan(api_key)
            # api.host() is synchronous, so we run it in a thread
            data = await asyncio.to_thread(api.host, host)
            return {
                "open_ports": data.get("ports", []),
                "vulns": data.get("vulns", []),
                "tags": data.get("tags", []),
                "hostnames": data.get("hostnames", []),
                "source": "Shodan API",
            }
        except shodan.APIError as e:
            logger.warning(f"Shodan API lookup failed for {host}: {e}. Falling back to InternetDB.")
        except Exception as e:
            logger.warning(f"Unexpected error with Shodan API for {host}: {e}. Falling back to InternetDB.")

    # Fallback to InternetDB
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(SHODAN_INTERNETDB_URL.format(host))
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "open_ports": data.get("ports", []),
                    "vulns": data.get("vulns", []),
                    "tags": data.get("tags", []),
                    "hostnames": data.get("hostnames", []),
                    "source": "Shodan InternetDB",
                }
            if resp.status_code == 404:
                return {"open_ports": [], "vulns": [], "tags": [], "hostnames": [], "note": "No Shodan data for this host", "source": "Shodan InternetDB"}
            logger.warning(f"Shodan InternetDB returned {resp.status_code} for {host}")
            return {"open_ports": [], "vulns": [], "tags": [], "hostnames": [], "source": "Shodan InternetDB"}
    except Exception as e:
        logger.warning(f"Shodan InternetDB lookup failed for {host}: {e}")
        return {"open_ports": [], "vulns": [], "tags": [], "hostnames": [], "source": "Error"}


async def passive_port_discovery(host: str, shodan_api_key: str | None = None) -> list[int]:
    """
    Discover open ports using Shodan API or InternetDB (passive).
    Falls back to a lightweight socket check on well-known ports if Shodan has no data.
    """
    shodan_data = await shodan_lookup(host, shodan_api_key)
    ports = shodan_data.get("open_ports", [])

    if not ports:
        # Fallback: lightweight single-port check on just 80 and 443
        ports = []
        for port in [80, 443]:
            try:
                _, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port), timeout=2.0
                )
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception:
                    pass
                ports.append(port)
            except (asyncio.TimeoutError, TimeoutError, OSError, ConnectionRefusedError, Exception):
                pass

    return sorted(set(ports))


# ── SSL Check ──

async def ssl_check(host: str, port: int = 443) -> dict:
    """
    Check SSL certificate validity using asyncio (non-blocking).
    """
    try:
        ctx = ssl.create_default_context()

        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port, ssl=ctx, server_hostname=host),
            timeout=8.0
        )
        ssl_obj = writer.get_extra_info('ssl_object')
        cert = ssl_obj.getpeercert() if ssl_obj else {}
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass

        not_after = cert.get("notAfter", "")
        issuer = dict(x[0] for x in cert.get("issuer", []))
        subject = dict(x[0] for x in cert.get("subject", []))

        from datetime import datetime
        try:
            expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
            days_left = (expiry - datetime.utcnow()).days
        except Exception:
            days_left = None

        return {
            "is_valid": True,
            "issuer_cn": issuer.get("commonName", "unknown"),
            "subject_cn": subject.get("commonName", host),
            "days_left": days_left,
            "expiry": not_after,
        }
    except (ssl.SSLCertVerificationError, ssl.SSLError) as e:
        return {"is_valid": False, "error": str(e)}
    except Exception as e:
        return {"is_valid": False, "error": str(e)}


# ── HIBP Breach Check ──

async def check_domain_breach(domain: str, hibp_api_key: str | None) -> dict:
    """
    Check HIBP for domain breaches. Optional — requires API key.
    The API key is free at https://haveibeenpwned.com/API/Key
    """
    if not hibp_api_key:
        return {"breach_found": False, "breaches": [], "note": "HIBP API key not configured"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"https://haveibeenpwned.com/api/v3/breaches?domain={domain}",
                headers={"hibp-api-key": hibp_api_key},
            )
            if resp.status_code == 200:
                breaches = resp.json()
                return {
                    "breach_found": len(breaches) > 0,
                    "breaches": [b.get("Name", "") for b in breaches][:20],
                    "count": len(breaches),
                }
            return {"breach_found": False, "breaches": []}
    except Exception as e:
        logger.warning(f"HIBP check failed for {domain}: {e}")
        return {"breach_found": False, "breaches": []}