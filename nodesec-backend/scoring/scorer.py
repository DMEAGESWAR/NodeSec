def kill_chain_depth(chains: list[dict], scan_data: dict) -> dict:
    """
    Calculate attack chain depth — how many steps an attacker can chain together.
    Returns a dict with the depth score and a breakdown of phases.
    """
    if not chains:
        return {"depth": 0, "max_depth": 5, "phases": {"recon": 0, "access": 0, "lateral": 0, "exfil": 0},
                "label": "No chainable vulnerabilities found"}

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
        phases["access"] += 1
    phases["access"] = min(phases["access"], 3)

    # Lateral movement
    if "RULE_05" in rule_ids:
        phases["lateral"] = 1

    # Exfiltration — SMTP open + no email auth = exfil via spoofed email
    if "RULE_06" in rule_ids and ("RULE_12" in rule_ids or "RULE_13" in rule_ids):
        phases["exfil"] = 1

    depth = sum(phases.values())
    return {
        "depth": min(depth, 5),
        "max_depth": 5,
        "phases": phases,
        "label": _depth_label(depth),
    }


def _depth_label(depth: int) -> str:
    if depth >= 4:
        return "Advanced persistent threat chain possible"
    if depth >= 3:
        return "Multi-stage attack path detected"
    if depth >= 2:
        return "Moderate attack chain"
    if depth >= 1:
        return "Basic exposure only"
    return "No chainable vulnerabilities found"


def overall_score(chains: list[dict], open_ports: list[int], subdomains: list[str],
                  scan_data: dict | None = None) -> int:
    """
    Calculate overall risk score from 0 to 100.
    Incorporates chain severity, kill chain depth, port exposure, and subdomain count.
    100 = maximum risk. 0 = completely clean.
    """
    scan_data = scan_data or {}

    if not chains:
        base = 3
        depth_score = 0
    else:
        severity_weights = {"critical": 25, "high": 15, "medium": 8, "low": 3}
        chain_score = sum(severity_weights.get(c.get("severity", "low"), 3) for c in chains)
        base = min(chain_score, 70)

        depth_info = kill_chain_depth(chains, scan_data)
        depth_score = depth_info["depth"] * 6  # up to 30 points for deep chains

    port_penalty = min(len(open_ports) * 2, 15)
    subdomain_penalty = min(len(subdomains), 10) if len(subdomains) > 10 else 0

    score = min(base + depth_score + port_penalty + subdomain_penalty, 100)
    return int(score)