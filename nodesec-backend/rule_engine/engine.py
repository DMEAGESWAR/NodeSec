import logging

logger = logging.getLogger("nodesec.rule_engine")


class RuleEngine:
    """
    Deterministic IF-THEN rule engine for attack chain detection.
    All rules are explicit — no AI/LLM calls.
    """

    def evaluate(self, scan_data: dict) -> list[dict]:
        """
        scan_data must contain:
          - domain: str
          - subdomains: list[str]
          - open_ports: list[int]
          - ssl_status: dict | None
          - breach_data: dict | None
          - dns_records: dict | None
          - email_security: dict | None  (new)
          - shodan_data: dict | None      (new)
        Returns list of triggered chain dicts.
        """
        chains = []
        chains.extend(self._rule_01(scan_data))
        chains.extend(self._rule_02(scan_data))
        chains.extend(self._rule_03(scan_data))
        chains.extend(self._rule_04(scan_data))
        chains.extend(self._rule_05(scan_data))
        chains.extend(self._rule_06(scan_data))
        chains.extend(self._rule_07(scan_data))
        chains.extend(self._rule_08(scan_data))
        chains.extend(self._rule_09(scan_data))
        chains.extend(self._rule_10(scan_data))
        chains.extend(self._rule_11(scan_data))
        chains.extend(self._rule_12(scan_data))
        chains.extend(self._rule_13(scan_data))
        return chains

    # ── RULE_01: SSH open + breach found → remote credential attack ──
    def _rule_01(self, data: dict) -> list[dict]:
        open_ports = data.get("open_ports", [])
        breach = data.get("breach_data", {}) or {}
        if 22 in open_ports and breach.get("breach_found"):
            return [{
                "rule_id": "RULE_01",
                "severity": "critical",
                "title": "Remote Credential Attack",
                "explanation": (
                    "SSH (port 22) is open and credentials for accounts on this domain "
                    "have appeared in known data breaches. Attackers can attempt credential "
                    "stuffing against SSH."
                ),
                "node_ids": [],
            }]
        return []

    # ── RULE_02: Multiple exposed admin subdomains ──
    def _rule_02(self, data: dict) -> list[dict]:
        admin_names = {"admin", "portal", "login", "manage", "dashboard", "console", "control", "cms"}
        subdomains = [s.lower().split(".")[0] for s in data.get("subdomains", [])]
        admin_matches = [s for s in subdomains if s in admin_names]
        if len(admin_matches) >= 2:
            return [{
                "rule_id": "RULE_02",
                "severity": "high",
                "title": "Multiple Exposed Admin Interfaces",
                "explanation": (
                    f"Found {len(admin_matches)} admin-related subdomains: "
                    f"{', '.join(admin_matches)}. Each is a potential entry point for attackers."
                ),
                "node_ids": [],
            }]
        return []

    # ── RULE_03: SSL certificate issues ──
    def _rule_03(self, data: dict) -> list[dict]:
        ssl = data.get("ssl_status")
        if not ssl:
            return []
        if not ssl.get("is_valid"):
            return [{
                "rule_id": "RULE_03",
                "severity": "high",
                "title": "Invalid SSL Certificate",
                "explanation": (
                    f"SSL certificate for {data['domain']} is invalid: "
                    f"{ssl.get('error', 'unknown error')}. "
                    f"This can enable man-in-the-middle attacks."
                ),
                "node_ids": [],
            }]
        if ssl.get("days_left") is not None and ssl["days_left"] < 30:
            return [{
                "rule_id": "RULE_03",
                "severity": "medium",
                "title": f"SSL Certificate Expiring Soon ({ssl['days_left']} days)",
                "explanation": (
                    f"SSL certificate for {data['domain']} expires in {ssl['days_left']} days. "
                    f"Expired certs cause browser warnings and erode user trust."
                ),
                "node_ids": [],
            }]
        return []

    # ── RULE_04: RDP exposed ──
    def _rule_04(self, data: dict) -> list[dict]:
        if 3389 in data.get("open_ports", []):
            return [{
                "rule_id": "RULE_04",
                "severity": "high",
                "title": "RDP Exposed to Internet",
                "explanation": (
                    "Remote Desktop Protocol (port 3389) is open. RDP is a frequent "
                    "target for brute-force and exploit attacks (e.g., BlueKeep)."
                ),
                "node_ids": [],
            }]
        return []

    # ── RULE_05: Database ports exposed ──
    def _rule_05(self, data: dict) -> list[dict]:
        chains = []
        if 3306 in data.get("open_ports", []):
            chains.append({
                "rule_id": "RULE_05",
                "severity": "critical",
                "title": "MySQL Port Exposed",
                "explanation": (
                    "MySQL (port 3306) is exposed to the internet. Database ports "
                    "should never be publicly accessible — this invites brute-force "
                    "and data exfiltration."
                ),
                "node_ids": [],
            })
        if 5432 in data.get("open_ports", []):
            chains.append({
                "rule_id": "RULE_05",
                "severity": "critical",
                "title": "PostgreSQL Port Exposed",
                "explanation": (
                    "PostgreSQL (port 5432) is exposed to the internet. Database ports "
                    "should never be publicly accessible."
                ),
                "node_ids": [],
            })
        return chains

    # ── RULE_06: SMTP open ──
    def _rule_06(self, data: dict) -> list[dict]:
        if 25 in data.get("open_ports", []):
            return [{
                "rule_id": "RULE_06",
                "severity": "medium",
                "title": "SMTP Port Exposed",
                "explanation": (
                    "SMTP (port 25) is open. This can be abused for email spoofing "
                    "and spam if not properly secured with SPF/DKIM/DMARC."
                ),
                "node_ids": [],
            }]
        return []

    # ── RULE_07: FTP open ──
    def _rule_07(self, data: dict) -> list[dict]:
        if 21 in data.get("open_ports", []):
            return [{
                "rule_id": "RULE_07",
                "severity": "high",
                "title": "FTP Port Exposed",
                "explanation": (
                    "FTP (port 21) transmits credentials in cleartext. "
                    "Replace with SFTP or SCP."
                ),
                "node_ids": [],
            }]
        return []

    # ── RULE_08: Telnet open ──
    def _rule_08(self, data: dict) -> list[dict]:
        if 23 in data.get("open_ports", []):
            return [{
                "rule_id": "RULE_08",
                "severity": "critical",
                "title": "Telnet Port Exposed",
                "explanation": (
                    "Telnet (port 23) transmits everything in cleartext including passwords. "
                    "Disable immediately and use SSH."
                ),
                "node_ids": [],
            }]
        return []

    # ── RULE_09: Large subdomain attack surface ──
    def _rule_09(self, data: dict) -> list[dict]:
        subdomains = data.get("subdomains", [])
        if len(subdomains) > 20:
            return [{
                "rule_id": "RULE_09",
                "severity": "medium",
                "title": f"Large Attack Surface ({len(subdomains)} subdomains)",
                "explanation": (
                    f"Found {len(subdomains)} subdomains. Each represents a potential "
                    f"entry point. Review and decommission unused subdomains."
                ),
                "node_ids": [],
            }]
        return []

    # ── RULE_10: HTTP without HTTPS ──
    def _rule_10(self, data: dict) -> list[dict]:
        open_ports = data.get("open_ports", [])
        if 80 in open_ports and 443 not in open_ports:
            return [{
                "rule_id": "RULE_10",
                "severity": "high",
                "title": "HTTP Without HTTPS",
                "explanation": (
                    "Port 80 (HTTP) is open but port 443 (HTTPS) is not. "
                    "All web traffic is in cleartext — enable HTTPS immediately."
                ),
                "node_ids": [],
            }]
        return []

    # ── RULE_11: Full kill chain ──
    def _rule_11(self, data: dict) -> list[dict]:
        open_ports = data.get("open_ports", [])
        breach = data.get("breach_data", {}) or {}
        has_breach = breach.get("breach_found", False)
        has_ssh = 22 in open_ports
        has_rdp = 3389 in open_ports
        has_db = 3306 in open_ports or 5432 in open_ports

        if has_breach and has_ssh and (has_rdp or has_db):
            return [{
                "rule_id": "RULE_11",
                "severity": "critical",
                "title": "Full Kill Chain Possible",
                "explanation": (
                    "Credentials are leaked, SSH is open, and additional critical services "
                    "(RDP or database) are exposed. An attacker can chain these: "
                    "breach → credential → SSH → lateral movement → RDP/DB access."
                ),
                "node_ids": [],
            }]
        return []

    # ── RULE_12: Missing SPF → email spoofing vulnerability ──
    def _rule_12(self, data: dict) -> list[dict]:
        email_sec = data.get("email_security") or {}
        if email_sec.get("spf") is False:
            return [{
                "rule_id": "RULE_12",
                "severity": "medium",
                "title": "Missing SPF Record",
                "explanation": (
                    f"No SPF record found for {data['domain']}. Anyone can spoof email "
                    f"from this domain. Attackers use this in phishing and BEC scams — "
                    f"recipients have no way to verify the email really came from you."
                ),
                "node_ids": [],
            }]
        return []

    # ── RULE_13: Missing or weak DMARC → no domain-level email protection ──
    def _rule_13(self, data: dict) -> list[dict]:
        email_sec = data.get("email_security") or {}
        if email_sec.get("dmarc") is False:
            return [{
                "rule_id": "RULE_13",
                "severity": "high",
                "title": "Missing DMARC Policy",
                "explanation": (
                    f"No DMARC record found for {data['domain']}. This is the #1 "
                    f"defense against CEO fraud and business email compromise. Without "
                    f"DMARC, an attacker can send email appearing to come from your CEO "
                    f"and no mail server will flag it."
                ),
                "node_ids": [],
            }]
        if email_sec.get("dmarc_policy") == "none":
            return [{
                "rule_id": "RULE_13",
                "severity": "medium",
                "title": "Weak DMARC Policy (p=none)",
                "explanation": (
                    f"DMARC is configured but set to 'p=none' — this means spoofed emails "
                    f"are monitored but not blocked. Upgrade to 'p=quarantine' or 'p=reject' "
                    f"to actually stop domain impersonation attacks."
                ),
                "node_ids": [],
            }]
        return []

    def kill_chain_depth(self, chains: list[dict], scan_data: dict) -> dict:
        """
        Calculate attack chain depth — how many steps an attacker can chain together.
        Returns a dict with the depth score and a breakdown of phases.
        """
        rule_ids = {c["rule_id"] for c in chains}
        phases = {"recon": 0, "access": 0, "lateral": 0, "exfil": 0}

        # Recon phase
        if "RULE_09" in rule_ids or len(scan_data.get("subdomains", [])) > 10:
            phases["recon"] = 1
        if "RULE_02" in rule_ids:
            phases["recon"] = min(phases["recon"] + 1, 2)

        # Access phase
        if "RULE_01" in rule_ids:
            phases["access"] += 1
        if "RULE_04" in rule_ids:
            phases["access"] += 1
        if "RULE_07" in rule_ids or "RULE_08" in rule_ids:
            phases["access"] += 1
        if "RULE_12" in rule_ids and "RULE_13" in rule_ids:
            phases["access"] += 1  # Email spoofing as initial access vector
        phases["access"] = min(phases["access"], 3)

        # Lateral movement
        if "RULE_05" in rule_ids:
            phases["lateral"] = 1

        # Exfiltration
        if "RULE_06" in rule_ids and ("RULE_12" in rule_ids or "RULE_13" in rule_ids):
            phases["exfil"] = 1  # SMTP + no email auth = data can be exfiltrated via spoofed email

        depth = sum(phases.values())
        return {
            "depth": min(depth, 5),
            "max_depth": 5,
            "phases": phases,
            "label": self._depth_label(depth),
        }

    def _depth_label(self, depth: int) -> str:
        if depth >= 4:
            return "Advanced persistent threat chain possible"
        if depth >= 3:
            return "Multi-stage attack path detected"
        if depth >= 2:
            return "Moderate attack chain"
        if depth >= 1:
            return "Basic exposure only"
        return "No chainable vulnerabilities found"

    # ── Fixes ──
    FIXES = {
        "RULE_01": [
            {"step_number": 1, "command": "ufw deny 22", "description": "Block SSH from public internet"},
            {"step_number": 2, "command": "passwd -l <username>", "description": "Lock accounts found in breach data"},
            {"step_number": 3, "command": "apt install fail2ban -y", "description": "Install fail2ban to rate-limit SSH attempts"},
        ],
        "RULE_02": [
            {"step_number": 1, "command": "nmap -sV <subdomain>", "description": "Identify services on each admin subdomain"},
            {"step_number": 2, "command": "ufw allow from <trusted_ip> to any port 443", "description": "Restrict admin panel access to trusted IPs"},
        ],
        "RULE_03": [
            {"step_number": 1, "command": "certbot renew --dry-run", "description": "Test certificate renewal"},
            {"step_number": 2, "command": "certbot renew --force-renewal", "description": "Force certificate renewal"},
        ],
        "RULE_04": [
            {"step_number": 1, "command": "ufw deny 3389", "description": "Block RDP from public internet"},
            {"step_number": 2, "command": "use VPN or RD Gateway instead", "description": "Replace direct RDP with VPN-secured access"},
        ],
        "RULE_05": [
            {"step_number": 1, "command": "ufw deny 3306", "description": "Block MySQL from public internet"},
            {"step_number": 2, "command": "ufw deny 5432", "description": "Block PostgreSQL from public internet"},
            {"step_number": 3, "command": "bind-address = 127.0.0.1", "description": "Bind database to localhost only"},
        ],
        "RULE_06": [
            {"step_number": 1, "command": "ufw deny 25", "description": "Block SMTP from public internet"},
            {"step_number": 2, "command": "configure SPF/DKIM/DMARC records", "description": "Add email authentication DNS records"},
        ],
        "RULE_07": [
            {"step_number": 1, "command": "ufw deny 21", "description": "Block FTP"},
            {"step_number": 2, "command": "apt install openssh-server -y", "description": "Use SFTP/SCP instead of FTP"},
        ],
        "RULE_08": [
            {"step_number": 1, "command": "systemctl disable telnet && systemctl stop telnet", "description": "Disable Telnet service immediately"},
            {"step_number": 2, "command": "apt install openssh-server -y", "description": "Replace with SSH"},
        ],
        "RULE_09": [
            {"step_number": 1, "command": "dig AXFR <domain>", "description": "Check for zone transfer exposure"},
            {"step_number": 2, "command": "review and decommission unused subdomains", "description": "Remove DNS records for unused subdomains"},
        ],
        "RULE_10": [
            {"step_number": 1, "command": "certbot --nginx -d <domain>", "description": "Install SSL certificate via Let's Encrypt"},
            {"step_number": 2, "command": "nginx -s reload", "description": "Reload web server with HTTPS config"},
        ],
        "RULE_11": [
            {"step_number": 1, "command": "ufw default deny incoming", "description": "Block all incoming traffic by default"},
            {"step_number": 2, "command": "ufw allow 80,443/tcp", "description": "Allow only HTTP/HTTPS"},
            {"step_number": 3, "command": "reset all user passwords", "description": "Force password reset for all accounts"},
            {"step_number": 4, "command": "enable MFA for all services", "description": "Add multi-factor authentication"},
        ],
        "RULE_12": [
            {"step_number": 1, "command": "v=spf1 mx -all", "description": "Add a basic SPF TXT record to your DNS (allows only your MX servers to send)"},
            {"step_number": 2, "command": "v=spf1 include:_spf.google.com -all", "description": "If using Google Workspace, use this SPF record instead"},
            {"step_number": 3, "command": "dig TXT <domain> | grep spf", "description": "Verify SPF record is published"},
        ],
        "RULE_13": [
            {"step_number": 1, "command": "v=DMARC1; p=reject; rua=mailto:dmarc@<domain>", "description": "Add a DMARC TXT record at _dmarc.<domain> with reject policy"},
            {"step_number": 2, "command": "v=DMARC1; p=quarantine; pct=100; rua=mailto:dmarc@<domain>", "description": "Start with quarantine if unsure — upgrade to reject after monitoring"},
            {"step_number": 3, "command": "dig TXT _dmarc.<domain>", "description": "Verify DMARC record is published at _dmarc subdomain"},
        ],
    }

    def get_fixes(self, rule_id: str) -> list[dict]:
        return self.FIXES.get(rule_id, [])