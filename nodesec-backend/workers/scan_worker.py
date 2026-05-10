import asyncio
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from osint.pipeline import (
    subdomain_discovery, dns_records, passive_port_discovery,
    ssl_check, check_domain_breach, email_security_checks, shodan_internetdb_lookup,
)
from rule_engine.engine import RuleEngine
from scoring.scorer import overall_score, kill_chain_depth
from services.scan_service import ScanRepository, GraphRepository, FindingRepository
from config import settings

logger = logging.getLogger("nodesec.worker")

_event_queues: dict[UUID, asyncio.Queue] = {}


def get_event_queue(scan_id: UUID) -> asyncio.Queue | None:
    return _event_queues.get(scan_id)


def create_event_queue(scan_id: UUID) -> asyncio.Queue:
    q = asyncio.Queue()
    _event_queues[scan_id] = q
    return q


def _push_event(scan_id: UUID, event: str, data: dict):
    q = _event_queues.get(scan_id)
    if q:
        try:
            q.put_nowait({"event": event, "data": data})
        except asyncio.QueueFull:
            pass


async def run_full_scan(
    scan_id: UUID, domain: str, is_demo: bool, db: AsyncSession
):
    """Orchestrates the full OSINT pipeline and rule engine evaluation."""
    queue = create_event_queue(scan_id)

    try:
        if is_demo:
            from demo.demo_data import DEMO_SCAN
            await _run_demo_scan(scan_id, db, DEMO_SCAN)
        else:
            await _run_live_scan(scan_id, domain, db)
    except Exception as e:
        logger.error(f"Scan {scan_id} failed: {e}", exc_info=True)
        _push_event(scan_id, "error", {"message": str(e)})
        await ScanRepository.finalize_scan(scan_id, 0, "failed", db)
    finally:
        if scan_id in _event_queues:
            del _event_queues[scan_id]


async def _run_live_scan(scan_id: UUID, domain: str, db: AsyncSession):
    import dns.resolver

    # ── Phase 1: Subdomain Discovery (multi-source) ──
    _push_event(scan_id, "progress", {"phase": "subdomain_discovery", "message": "Discovering subdomains (crt.sh + CertSpotter + OTX)..."})
    subdomains = await subdomain_discovery(domain)
    _push_event(scan_id, "progress", {"phase": "subdomain_discovery", "subdomains": subdomains})

    # ── Phase 2: DNS Records ──
    _push_event(scan_id, "progress", {"phase": "dns", "message": "Resolving DNS records..."})
    dns = await dns_records(domain)

    # ── Phase 3: Email Security Checks (SPF/DKIM/DMARC) ──
    _push_event(scan_id, "progress", {"phase": "email_security", "message": "Checking email security posture..."})
    email_sec = await email_security_checks(domain)
    _push_event(scan_id, "progress", {"phase": "email_security", "email_security": email_sec})

    # ── Phase 4: Port Discovery (Shodan InternetDB + lightweight fallback) ──
    _push_event(scan_id, "progress", {"phase": "ports", "message": "Discovering open ports (Shodan InternetDB)..."})

    ips = set()
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        answers = resolver.resolve(domain, "A")
        for a in answers:
            ips.add(str(a))
    except Exception:
        ips.add(domain)

    all_open_ports = []
    shodan_data = {}
    for ip in ips:
        ports = await passive_port_discovery(ip)
        all_open_ports.extend(ports)
        shodan_data[ip] = await shodan_internetdb_lookup(ip)
        _push_event(scan_id, "progress", {
            "phase": "ports", "host": ip, "open_ports": ports,
            "source": "Shodan InternetDB",
        })

    all_open_ports = sorted(set(all_open_ports))
    shodan_vulns = []
    for ip_data in shodan_data.values():
        shodan_vulns.extend(ip_data.get("vulns", []))

    # ── Phase 5: SSL Check ──
    _push_event(scan_id, "progress", {"phase": "ssl", "message": "Checking SSL certificate..."})
    ssl_status = await ssl_check(domain)

    # ── Phase 6: Breach Check ──
    _push_event(scan_id, "progress", {"phase": "breach", "message": "Checking data breaches..."})
    breach_data = await check_domain_breach(domain, settings.hibp_api_key or None)

    # ── Build Graph Nodes ──
    nodes_data = _build_nodes(domain, subdomains, all_open_ports, ssl_status, breach_data,
                              ips, email_sec, shodan_vulns)
    _push_event(scan_id, "nodes", {"nodes": nodes_data})

    # ── Rule Engine ──
    _push_event(scan_id, "progress", {"phase": "analysis", "message": "Running attack chain analysis..."})
    engine = RuleEngine()
    scan_data = {
        "domain": domain,
        "subdomains": subdomains,
        "open_ports": all_open_ports,
        "ssl_status": ssl_status,
        "breach_data": breach_data,
        "dns_records": dns,
        "email_security": email_sec,
        "shodan_data": shodan_data,
        "shodan_vulns": shodan_vulns,
    }
    chains = engine.evaluate(scan_data)
    chain_depth = kill_chain_depth(chains, scan_data)
    score = overall_score(chains, all_open_ports, subdomains, scan_data)

    # ── Save Nodes to DB ──
    nodes = await GraphRepository.save_nodes(scan_id, nodes_data, db)
    for i, nd in enumerate(nodes_data):
        nd["id"] = str(nodes[i].id)

    # ── Wire Edges Using Saved Node IDs ──
    edges_data = _build_edges(nodes_data)
    edges_data_with_ids = []
    for ed in edges_data:
        edges_data_with_ids.append({
            "source_node_id": ed["source_id"],
            "target_node_id": ed["target_id"],
            "relationship_type": ed["relationship_type"],
        })
    saved_edges = await GraphRepository.save_edges(scan_id, edges_data_with_ids, db)

    # ── Save Chains & Findings ──
    saved_chains = await GraphRepository.save_chains(scan_id, chains, engine.FIXES, db)
    await FindingRepository.create_findings(scan_id, chains, db)
    await ScanRepository.finalize_scan(scan_id, score, "completed", db)

    # ── Push Final Results ──
    chain_dicts = []
    for i, c in enumerate(saved_chains):
        chain_dicts.append({
            "id": str(c.id),
            "rule_id": c.rule_id,
            "severity": c.severity,
            "title": c.title,
            "explanation": c.explanation,
            "node_ids": c.node_ids,
        })

    _push_event(scan_id, "chains", {
        "chains": chain_dicts,
        "overall_score": score,
        "kill_chain_depth": chain_depth,
    })
    _push_event(scan_id, "complete", {"overall_score": score, "kill_chain_depth": chain_depth})


async def _run_demo_scan(scan_id: UUID, db: AsyncSession, demo: dict):
    """Run demo scan with pre-loaded data. Edges are wired by label resolution."""
    nodes_data = demo["nodes"]
    edges_template = demo["edges"]
    chains = demo["chains"]
    score = demo["overall_score"]

    # Push SSE events for frontend animation
    for node in nodes_data:
        _push_event(scan_id, "node", node)
        await asyncio.sleep(0.15)

    # Save nodes first to get real UUIDs
    nodes = await GraphRepository.save_nodes(scan_id, nodes_data, db)

    # Build label → real UUID mapping
    label_to_id = {}
    for i, node in enumerate(nodes_data):
        label_to_id[node["label"]] = str(nodes[i].id)

    # Wire edges using label-based references from template
    edges_data_with_ids = []
    for i, ed in enumerate(edges_template):
        source_label = ed.get("source_label", "")
        target_label = ed.get("target_label", "")
        source_id = label_to_id.get(source_label, "")
        target_id = label_to_id.get(target_label, "")

        if source_id and target_id:
            edges_data_with_ids.append({
                "source_node_id": source_id,
                "target_node_id": target_id,
                "relationship_type": ed["relationship_type"],
            })
            _push_event(scan_id, "edge", {
                "source_node_id": source_id,
                "target_node_id": target_id,
                "relationship_type": ed["relationship_type"],
            })
            await asyncio.sleep(0.05)

    await GraphRepository.save_edges(scan_id, edges_data_with_ids, db)

    for chain in chains:
        _push_event(scan_id, "chain", chain)
        await asyncio.sleep(0.1)

    engine = RuleEngine()
    await GraphRepository.save_chains(scan_id, chains, engine.FIXES, db)
    await FindingRepository.create_findings(scan_id, chains, db)

    chain_depth = {"depth": 3, "max_depth": 5, "phases": {"recon": 1, "access": 1, "lateral": 1, "exfil": 0},
                   "label": "Multi-stage attack path detected"}

    await ScanRepository.finalize_scan(scan_id, score, "completed", db)
    _push_event(scan_id, "complete", {"overall_score": score, "kill_chain_depth": chain_depth})


def _build_nodes(domain: str, subdomains: list[str], open_ports: list[int],
                 ssl_status: dict | None, breach_data: dict | None, ips: set,
                 email_sec: dict | None = None, shodan_vulns: list[str] | None = None) -> list[dict]:
    nodes = []

    # Domain node (center)
    nodes.append({
        "node_type": "domain", "label": domain, "ip": list(ips)[0] if ips else None,
        "severity": "low", "raw_data": {},
    })

    # Subdomain nodes
    for sd in subdomains:
        nodes.append({
            "node_type": "subdomain", "label": sd, "severity": "low", "raw_data": {},
        })

    # Port nodes
    for port in open_ports:
        nodes.append({
            "node_type": "port", "label": f"{list(ips)[0] if ips else domain}:{port}",
            "ip": list(ips)[0] if ips else None, "port": port,
            "severity": "high" if port in [22, 3389, 3306, 5432, 23, 21] else "medium",
            "raw_data": {},
        })

    # Breach node
    if breach_data and breach_data.get("breach_found"):
        nodes.append({
            "node_type": "breach", "label": f"Breach: {domain}",
            "severity": "critical",
            "raw_data": {"breaches": breach_data.get("breaches", [])},
        })

    # SSL issue node
    if ssl_status and not ssl_status.get("is_valid"):
        nodes.append({
            "node_type": "ssl_issue", "label": f"SSL Issue: {domain}",
            "severity": "high",
            "raw_data": {"ssl_error": ssl_status.get("error", "")},
        })

    # Email security nodes
    if email_sec:
        if not email_sec.get("spf"):
            nodes.append({
                "node_type": "ssl_issue", "label": f"Missing SPF: {domain}",
                "severity": "medium",
                "raw_data": {"issue": "No SPF record — email can be spoofed"},
            })
        if not email_sec.get("dmarc"):
            nodes.append({
                "node_type": "ssl_issue", "label": f"Missing DMARC: {domain}",
                "severity": "high",
                "raw_data": {"issue": "No DMARC record — no email authentication"},
            })
        elif email_sec.get("dmarc_policy") == "none":
            nodes.append({
                "node_type": "ssl_issue", "label": f"Weak DMARC: {domain}",
                "severity": "medium",
                "raw_data": {"issue": "DMARC p=none — spoofed emails not blocked"},
            })

    # Shodan CVE nodes
    if shodan_vulns:
        for vuln in shodan_vulns[:5]:
            nodes.append({
                "node_type": "ssl_issue", "label": f"CVE: {vuln}",
                "severity": "critical" if any(
                    cve in str(vuln) for cve in ["CVE-2021", "CVE-2022", "CVE-2023"]
                ) else "high",
                "raw_data": {"cve": vuln},
            })

    return nodes


def _build_edges(nodes_data: list[dict]) -> list[dict]:
    """Build edges from node data using node IDs. Node IDs must be set before calling."""
    edges = []
    domain_nodes = [n for n in nodes_data if n["node_type"] == "domain"]
    subdomain_nodes = [n for n in nodes_data if n["node_type"] == "subdomain"]

    for d in domain_nodes:
        for sd in subdomain_nodes:
            if d.get("id") and sd.get("id"):
                edges.append({"source_id": d["id"], "target_id": sd["id"], "relationship_type": "has_subdomain"})

    for n in domain_nodes:
        did = n.get("id")
        if not did:
            continue
        for other in nodes_data:
            oid = other.get("id")
            if not oid or oid == did:
                continue
            if other["node_type"] == "port":
                edges.append({"source_id": did, "target_id": oid, "relationship_type": "has_port"})
            elif other["node_type"] == "breach":
                edges.append({"source_id": did, "target_id": oid, "relationship_type": "has_breach"})
            elif other["node_type"] == "ssl_issue":
                edges.append({"source_id": did, "target_id": oid, "relationship_type": "has_ssl_issue"})

    return edges