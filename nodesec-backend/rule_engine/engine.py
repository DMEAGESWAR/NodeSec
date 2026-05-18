import logging

logger = logging.getLogger("nodesec.rule_engine")


class RuleEngine:

    def evaluate(self, scan_data: dict) -> list[dict]:

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

    FIXES = {
        "RULE_01": [{"step_number": 1, "command": "ufw deny 22", "description": "Close port 22 to the public internet."}],
        "RULE_02": [{"step_number": 1, "command": "N/A", "description": "Restrict admin subdomains to internal IP ranges."}],
        "RULE_03": [
            {"step_number": 1, "command": "N/A", "description": "Renew SSL certificate immediately"},
            {"step_number": 2, "command": "N/A", "description": "Use trusted Certificate Authority"},
            {"step_number": 3, "command": "N/A", "description": "Enable auto-renewal"}
        ],
        "RULE_04": [{"step_number": 1, "command": "ufw deny 3389", "description": "Close port 3389 (RDP) to the public internet."}],
        "RULE_05": [{"step_number": 1, "command": "ufw deny 3306", "description": "Close port 3306 (MySQL) to the public internet."}],
        "RULE_06": [{"step_number": 1, "command": "N/A", "description": "Secure the SMTP server and restrict relaying."}],
        "RULE_07": [{"step_number": 1, "command": "N/A", "description": "Disable FTP and migrate to SFTP (port 22)."}],
        "RULE_08": [{"step_number": 1, "command": "systemctl stop telnet", "description": "Disable the Telnet service immediately."}],
        "RULE_09": [{"step_number": 1, "command": "N/A", "description": "Audit subdomains and decommission unused ones."}],
        "RULE_10": [{"step_number": 1, "command": "N/A", "description": "Install an SSL/TLS certificate for HTTPS."}],
        "RULE_11": [{"step_number": 1, "command": "N/A", "description": "Prioritize patching SSH and Database exposures."}],
        "RULE_12": [
            {"step_number": 1, "command": "N/A", "description": "Add SPF TXT record to DNS"},
            {"step_number": 2, "command": "N/A", "description": "Allow only trusted mail servers"},
            {"step_number": 3, "command": "N/A", "description": "Enable SPF protection for email security"}
        ],
        "RULE_13": [
            {"step_number": 1, "command": "N/A", "description": "Add DMARC TXT record"},
            {"step_number": 2, "command": "N/A", "description": "Use quarantine or reject policy"},
            {"step_number": 3, "command": "N/A", "description": "Monitor spoofing reports"}
        ]
    }

    # =========================================================
    # RULE 01
    # =========================================================

    def _rule_01(self, data: dict) -> list[dict]:

        open_ports = data.get("open_ports", [])
        breach = data.get("breach_data", {}) or {}
        domain = data.get("domain", "target domain")

        if 22 in open_ports and breach.get("breach_found"):

            return [{
                "rule_id": "RULE_01",

                "severity": "critical",
                "risk_score": 9.4,

                "title": "SSH Credential Attack Risk",

                "detected_from": [
                    "port_scan",
                    "breach_database"
                ],

                "explanation": (
                    f"SSH service is publicly accessible on {domain}.\n\n"

                    "Leaked credentials related to this domain "
                    "were also found in public breach data.\n\n"

                    "Attackers may use these leaked passwords "
                    "to gain unauthorized server access."
                ),

                "impact": (
                    "Attackers may access the server, steal data, "
                    "or install ransomware."
                ),

                "attack_path": [
                    "Leaked credentials discovered",
                    "SSH service detected",
                    "Login attack launched",
                    "Server access gained"
                ],

                "node_ids": [],
            }]

        return []

    # =========================================================
    # RULE 02
    # =========================================================

    def _rule_02(self, data: dict) -> list[dict]:

        admin_names = {
            "admin",
            "portal",
            "dashboard",
            "manage",
            "console",
            "login",
            "cms"
        }

        subdomains = [
            s.lower().split(".")[0]
            for s in data.get("subdomains", [])
        ]

        matches = [
            s for s in subdomains
            if s in admin_names
        ]

        if len(matches) >= 2:

            return [{
                "rule_id": "RULE_02",

                "severity": "high",
                "risk_score": 8.1,

                "title": "Multiple Admin Panels Exposed",

                "detected_from": [
                    "subdomain_enumeration"
                ],

                "explanation": (
                    f"{len(matches)} admin-related subdomains were discovered.\n\n"

                    "Admin panels are common targets for attackers."
                ),

                "impact": (
                    "Attackers may attempt password attacks "
                    "or take control of admin accounts."
                ),

                "attack_path": [
                    "Admin panel discovered",
                    "Password attack attempted",
                    "Unauthorized admin access gained"
                ],

                "node_ids": [],
            }]

        return []

    # =========================================================
    # RULE 03
    # =========================================================

    def _rule_03(self, data: dict) -> list[dict]:

        ssl = data.get("ssl_status")
        domain = data.get("domain", "target domain")

        if not ssl:
            return []

        if not ssl.get("is_valid"):

            return [{
                "rule_id": "RULE_03",

                "severity": "high",
                "risk_score": 8.5,

                "title": "Invalid SSL Certificate",

                "detected_from": [
                    "ssl_scan"
                ],

                "explanation": (
                    f"The SSL certificate for {domain} is invalid.\n\n"

                    "Secure communication cannot be fully trusted.\n\n"

                    "Attackers may intercept traffic between "
                    "users and the website."
                ),

                "impact": (
                    "Sensitive information such as passwords "
                    "may be exposed."
                ),

                "attack_path": [
                    "User visits website",
                    "SSL validation fails",
                    "Connection becomes unsafe",
                    "Data intercepted"
                ],

                "node_ids": [],
            }]

        if ssl.get("days_left") is not None and ssl["days_left"] < 30:

            return [{
                "rule_id": "RULE_03",

                "severity": "medium",
                "risk_score": 5.9,

                "title": "SSL Certificate Expiring Soon",

                "detected_from": [
                    "ssl_scan"
                ],

                "explanation": (
                    f"The SSL certificate for {domain} "
                    f"will expire in {ssl['days_left']} days."
                ),

                "impact": (
                    "Users may start receiving browser security warnings."
                ),

                "attack_path": [
                    "Certificate expires",
                    "Browser warning displayed",
                    "Users lose trust"
                ],

                "node_ids": [],
            }]

        return []

    # =========================================================
    # RULE 04
    # =========================================================

    def _rule_04(self, data: dict) -> list[dict]:

        if 3389 in data.get("open_ports", []):

            return [{
                "rule_id": "RULE_04",

                "severity": "high",
                "risk_score": 8.4,

                "title": "RDP Exposed to Internet",

                "detected_from": [
                    "port_scan"
                ],

                "explanation": (
                    "Remote Desktop service is publicly accessible.\n\n"

                    "Attackers commonly target RDP services "
                    "using brute-force attacks."
                ),

                "impact": (
                    "Remote system compromise may occur."
                ),

                "attack_path": [
                    "RDP service detected",
                    "Password attack launched",
                    "Remote access gained"
                ],

                "node_ids": [],
            }]

        return []

    # =========================================================
    # RULE 05
    # =========================================================

    def _rule_05(self, data: dict) -> list[dict]:

        if 3306 in data.get("open_ports", []):

            return [{
                "rule_id": "RULE_05",

                "severity": "critical",
                "risk_score": 9.5,

                "title": "MySQL Database Exposed",

                "detected_from": [
                    "port_scan"
                ],

                "explanation": (
                    "The MySQL database is directly accessible "
                    "from the internet."
                ),

                "impact": (
                    "Attackers may steal or modify database information."
                ),

                "attack_path": [
                    "Database detected",
                    "Weak credentials targeted",
                    "Database compromised"
                ],

                "node_ids": [],
            }]

        return []

    # =========================================================
    # RULE 06
    # =========================================================

    def _rule_06(self, data: dict) -> list[dict]:

        if 25 in data.get("open_ports", []):

            return [{
                "rule_id": "RULE_06",

                "severity": "medium",
                "risk_score": 6.0,

                "title": "SMTP Service Exposed",

                "detected_from": [
                    "port_scan"
                ],

                "explanation": (
                    "SMTP service is publicly accessible.\n\n"

                    "Improper email configuration may allow spoofing."
                ),

                "impact": (
                    "Spam and phishing emails may be sent."
                ),

                "attack_path": [
                    "SMTP detected",
                    "Fake emails created",
                    "Victims targeted"
                ],

                "node_ids": [],
            }]

        return []

    # =========================================================
    # RULE 07
    # =========================================================

    def _rule_07(self, data: dict) -> list[dict]:

        if 21 in data.get("open_ports", []):

            return [{
                "rule_id": "RULE_07",

                "severity": "high",
                "risk_score": 7.9,

                "title": "FTP Service Exposed",

                "detected_from": [
                    "port_scan"
                ],

                "explanation": (
                    "FTP sends usernames and passwords "
                    "without encryption."
                ),

                "impact": (
                    "Attackers may steal login credentials."
                ),

                "attack_path": [
                    "FTP detected",
                    "Traffic monitored",
                    "Credentials stolen"
                ],

                "node_ids": [],
            }]

        return []

    # =========================================================
    # RULE 08
    # =========================================================

    def _rule_08(self, data: dict) -> list[dict]:

        if 23 in data.get("open_ports", []):

            return [{
                "rule_id": "RULE_08",

                "severity": "critical",
                "risk_score": 9.1,

                "title": "Telnet Service Exposed",

                "detected_from": [
                    "port_scan"
                ],

                "explanation": (
                    "Telnet communication is not encrypted.\n\n"

                    "Usernames and passwords can be easily captured."
                ),

                "impact": (
                    "Attackers may gain full system access."
                ),

                "attack_path": [
                    "Telnet detected",
                    "Credentials captured",
                    "System compromised"
                ],

                "node_ids": [],
            }]

        return []

    # =========================================================
    # RULE 09
    # =========================================================

    def _rule_09(self, data: dict) -> list[dict]:

        subdomains = data.get("subdomains", [])

        if len(subdomains) > 20:

            return [{
                "rule_id": "RULE_09",

                "severity": "medium",
                "risk_score": 5.8,

                "title": "Large Attack Surface",

                "detected_from": [
                    "subdomain_enumeration"
                ],

                "explanation": (
                    f"{len(subdomains)} subdomains were discovered.\n\n"

                    "Unused or forgotten systems may contain vulnerabilities."
                ),

                "impact": (
                    "More systems increase the chance of attack."
                ),

                "attack_path": [
                    "Subdomains discovered",
                    "Weak system identified",
                    "Vulnerability exploited"
                ],

                "node_ids": [],
            }]

        return []

    # =========================================================
    # RULE 10
    # =========================================================

    def _rule_10(self, data: dict) -> list[dict]:

        ports = data.get("open_ports", [])

        if 80 in ports and 443 not in ports:

            return [{
                "rule_id": "RULE_10",

                "severity": "high",
                "risk_score": 7.8,

                "title": "HTTP Without HTTPS",

                "detected_from": [
                    "port_scan"
                ],

                "explanation": (
                    "Website traffic is not encrypted.\n\n"

                    "Sensitive information may be intercepted."
                ),

                "impact": (
                    "Passwords and session data may be exposed."
                ),

                "attack_path": [
                    "User visits website",
                    "Traffic intercepted",
                    "Sensitive data stolen"
                ],

                "node_ids": [],
            }]

        return []

    # =========================================================
    # RULE 11
    # =========================================================

    def _rule_11(self, data: dict) -> list[dict]:

        ports = data.get("open_ports", [])
        breach = data.get("breach_data", {}) or {}

        if (
            breach.get("breach_found")
            and 22 in ports
            and (3389 in ports or 3306 in ports)
        ):

            return [{
                "rule_id": "RULE_11",

                "severity": "critical",
                "risk_score": 9.8,

                "title": "Multi-Stage Attack Chain Possible",

                "detected_from": [
                    "breach_database",
                    "port_scan"
                ],

                "explanation": (
                    "Multiple critical security weaknesses were detected.\n\n"

                    "Attackers may combine these weaknesses "
                    "to fully compromise systems."
                ),

                "impact": (
                    "Complete infrastructure compromise may occur."
                ),

                "attack_path": [
                    "Leaked credentials found",
                    "SSH access gained",
                    "Database or RDP accessed",
                    "System fully compromised"
                ],

                "node_ids": [],
            }]

        return []

    # =========================================================
    # RULE 12
    # =========================================================

    def _rule_12(self, data: dict) -> list[dict]:

        email_sec = data.get("email_security") or {}
        domain = data.get("domain", "target domain")

        if email_sec.get("spf") is False:

            return [{
                "rule_id": "RULE_12",

                "severity": "medium",
                "risk_score": 6.5,

                "title": "Missing SPF Email Protection",

                "detected_from": [
                    "dns_analysis"
                ],

                "explanation": (
                    f"The domain {domain} does not have SPF protection enabled.\n\n"

                    "SPF helps verify whether emails are "
                    "actually sent from your domain.\n\n"

                    "Without SPF protection, attackers can create "
                    "fake emails using your company name."
                ),

                "impact": (
                    "Users may trust fake emails and share passwords, "
                    "bank details, or confidential information."
                ),

                "attack_path": [
                    "SPF protection missing",
                    "Fake company email created",
                    "Victim receives trusted-looking email",
                    "Sensitive information stolen"
                ],

                "node_ids": [],
            }]

        return []

    # =========================================================
    # RULE 13
    # =========================================================

    def _rule_13(self, data: dict) -> list[dict]:

        email_sec = data.get("email_security") or {}
        domain = data.get("domain", "target domain")

        if email_sec.get("dmarc") is False:

            return [{
                "rule_id": "RULE_13",

                "severity": "high",
                "risk_score": 8.8,

                "title": "Missing DMARC Protection",

                "detected_from": [
                    "dns_analysis"
                ],

                "explanation": (
                    f"The domain {domain} does not have DMARC protection enabled.\n\n"

                    "DMARC helps prevent fake emails from reaching users.\n\n"

                    "Without DMARC, attackers can impersonate "
                    "employees or support teams."
                ),

                "impact": (
                    "Fake emails may be used for phishing, scams, "
                    "and financial fraud."
                ),

                "attack_path": [
                    "DMARC protection missing",
                    "Fake email created",
                    "Victim trusts attacker",
                    "Sensitive data stolen"
                ],

                "node_ids": [],
            }]

        return []

    # =========================================================
    # FIXES
    # =========================================================