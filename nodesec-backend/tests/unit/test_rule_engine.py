import pytest
from rule_engine.engine import RuleEngine


def _base_scan(domain="test.com", **overrides):
    data = {
        "domain": domain,
        "subdomains": [],
        "open_ports": [],
        "ssl_status": None,
        "breach_data": {},
        "dns_records": {},
        "email_security": {},
        "shodan_data": {},
    }
    data.update(overrides)
    return data


class TestRuleEngine:

    def test_evaluate_returns_list(self, rule_engine):
        result = rule_engine.evaluate(_base_scan())
        assert isinstance(result, list)

    # ── RULE_01 ──
    def test_rule_01_triggers_on_ssh_and_breach(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(
            open_ports=[22], breach_data={"breach_found": True, "breaches": ["Collection1"]}
        ))
        assert any(c["rule_id"] == "RULE_01" for c in result)

    def test_rule_01_no_trigger_without_breach(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(
            open_ports=[22], breach_data={"breach_found": False}
        ))
        assert not any(c["rule_id"] == "RULE_01" for c in result)

    def test_rule_01_no_trigger_without_ssh(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(
            open_ports=[80], breach_data={"breach_found": True}
        ))
        assert not any(c["rule_id"] == "RULE_01" for c in result)

    # ── RULE_02 ──
    def test_rule_02_triggers_on_multiple_admin_subdomains(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(
            subdomains=["admin.test.com", "portal.test.com"]
        ))
        assert any(c["rule_id"] == "RULE_02" for c in result)

    def test_rule_02_no_trigger_on_single_admin(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(
            subdomains=["admin.test.com"]
        ))
        assert not any(c["rule_id"] == "RULE_02" for c in result)

    # ── RULE_04 ──
    def test_rule_04_triggers_on_rdp(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(open_ports=[3389]))
        assert any(c["rule_id"] == "RULE_04" for c in result)

    # ── RULE_05 ──
    def test_rule_05_triggers_on_mysql(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(open_ports=[3306]))
        assert any(c["rule_id"] == "RULE_05" for c in result)

    def test_rule_05_triggers_on_postgres(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(open_ports=[5432]))
        assert any(c["rule_id"] == "RULE_05" for c in result)

    # ── RULE_08 ──
    def test_rule_08_triggers_on_telnet(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(open_ports=[23]))
        assert any(c["rule_id"] == "RULE_08" for c in result)

    # ── RULE_11 ──
    def test_rule_11_full_kill_chain(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(
            open_ports=[22, 3389], breach_data={"breach_found": True}
        ))
        assert any(c["rule_id"] == "RULE_11" for c in result)

    def test_rule_11_no_trigger_without_breach(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(
            open_ports=[22, 3389], breach_data={"breach_found": False}
        ))
        assert not any(c["rule_id"] == "RULE_11" for c in result)

    # ── RULE_12: Missing SPF ──
    def test_rule_12_triggers_when_spf_missing(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(
            email_security={"spf": False, "dmarc": True}
        ))
        assert any(c["rule_id"] == "RULE_12" for c in result)

    def test_rule_12_no_trigger_when_spf_present(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(
            email_security={"spf": True, "spf_record": "v=spf1 mx -all", "dmarc": True}
        ))
        assert not any(c["rule_id"] == "RULE_12" for c in result)

    # ── RULE_13: Missing/Weak DMARC ──
    def test_rule_13_triggers_when_dmarc_missing(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(
            email_security={"dmarc": False, "spf": True}
        ))
        assert any(c["rule_id"] == "RULE_13" for c in result)

    def test_rule_13_triggers_on_p_none(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(
            email_security={"dmarc": True, "dmarc_policy": "none", "spf": True}
        ))
        dmarc_chains = [c for c in result if c["rule_id"] == "RULE_13"]
        assert len(dmarc_chains) == 1
        assert "p=none" in dmarc_chains[0]["title"]

    def test_rule_13_no_trigger_on_p_reject(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(
            email_security={"dmarc": True, "dmarc_policy": "reject", "spf": True}
        ))
        assert not any(c["rule_id"] == "RULE_13" for c in result)

    # ── Clean domain ──
    def test_clean_domain_no_chains(self, rule_engine):
        result = rule_engine.evaluate(_base_scan(
            subdomains=["www.test.com"],
            open_ports=[80, 443],
            ssl_status={"is_valid": True, "days_left": 180},
            breach_data={"breach_found": False},
            email_security={"spf": True, "dmarc": True, "dmarc_policy": "reject"},
        ))
        assert len(result) == 0

    # ── Fixes ──
    def test_all_active_rules_have_fixes(self, rule_engine):
        for rule_id in [f"RULE_{i:02d}" for i in range(1, 14)]:
            fixes = rule_engine.get_fixes(rule_id)
            assert isinstance(fixes, list), f"{rule_id} has no fixes"

    def test_rule_12_fixes_include_spf_command(self, rule_engine):
        fixes = rule_engine.get_fixes("RULE_12")
        assert any("spf" in str(f).lower() for f in fixes)

    def test_rule_13_fixes_include_dmarc_command(self, rule_engine):
        fixes = rule_engine.get_fixes("RULE_13")
        assert any("dmarc" in str(f).lower() for f in fixes)

    # ── Kill Chain Depth ──
    def test_kill_chain_depth_zero_for_clean(self, rule_engine):
        result = rule_engine.kill_chain_depth([], _base_scan())
        assert result["depth"] == 0

    def test_kill_chain_depth_with_critical_chain(self, rule_engine):
        chains = [
            {"rule_id": "RULE_01", "severity": "critical"},
            {"rule_id": "RULE_05", "severity": "critical"},
            {"rule_id": "RULE_04", "severity": "high"},
        ]
        result = rule_engine.kill_chain_depth(chains, _base_scan(
            subdomains=["a.test.com"] * 11, open_ports=[22, 3389, 3306]
        ))
        assert result["depth"] >= 3
        assert result["phases"]["access"] >= 2
        assert result["phases"]["lateral"] >= 1


class TestScorer:
    def test_clean_returns_low_score(self):
        from scoring.scorer import overall_score
        score = overall_score([], [80, 443], ["www.test.com"])
        assert score < 30

    def test_critical_returns_high_score(self):
        from scoring.scorer import overall_score
        chains = [
            {"severity": "critical"},
            {"severity": "high"},
            {"severity": "medium"},
        ]
        score = overall_score(chains, [22, 3306], ["admin.test.com"] * 5)
        assert score >= 50

    def test_kill_chain_depth_increases_score(self):
        from scoring.scorer import overall_score
        from scoring.scorer import kill_chain_depth

        # Many critical chains → higher score with depth
        chains = [
            {"rule_id": "RULE_01", "severity": "critical"},
            {"rule_id": "RULE_04", "severity": "high"},
            {"rule_id": "RULE_05", "severity": "critical"},
            {"rule_id": "RULE_11", "severity": "critical"},
        ]
        scan_data = {
            "subdomains": ["admin.test.com"] * 15,
            "open_ports": [22, 3389, 3306, 25],
        }
        score = overall_score(chains, [22, 3389, 3306, 25], ["admin.test.com"] * 15, scan_data)
        assert score >= 70  # Deep chain with many critical findings

    def test_kill_chain_depth_calculates_phases(self):
        from scoring.scorer import kill_chain_depth
        chains = [
            {"rule_id": "RULE_09", "severity": "medium"},
            {"rule_id": "RULE_01", "severity": "critical"},
            {"rule_id": "RULE_05", "severity": "critical"},
        ]
        scan_data = {"subdomains": ["a.test.com"] * 25, "open_ports": [22, 3306]}
        result = kill_chain_depth(chains, scan_data)
        assert result["phases"]["recon"] >= 1
        assert result["phases"]["access"] >= 1
        assert result["phases"]["lateral"] >= 1