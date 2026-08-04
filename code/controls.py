"""
ProofLayer - Compliance Control Dataset
Frameworks: FedRAMP, CMMC 2.0, NIST SP 800-53, SOC2, FISMA
Focus: Government and federal contractor compliance
"""

FRAMEWORKS = {
    "FedRAMP":      "Federal Risk and Authorization Management Program",
    "CMMC":         "Cybersecurity Maturity Model Certification 2.0",
    "NIST_800_53":  "NIST Special Publication 800-53 Rev 5",
    "NIST_CSF":     "NIST Cybersecurity Framework 2.0",
    "SOC2":         "SOC 2 Type II",
}

CONTROL_DATASET = [
    # ── Access Control ─────────────────────────────────────────────────────
    {
        "id": "AC-01",
        "control": "Access Control Policy & Procedures",
        "category": "Access Control",
        "keywords": ["access control policy", "access policy", "access procedures", "access management policy"],
        "frameworks": {"FedRAMP": "AC-1", "NIST_800_53": "AC-1", "CMMC": "AC.L1-3.1.1", "SOC2": "CC6.1"},
        "risk": "HIGH",
        "description": "Develop and disseminate formal access control policies covering purpose, scope, roles, and responsibilities.",
        "remediation": "Create an Access Control Policy document that defines who can access what systems and under what conditions.",
    },
    {
        "id": "AC-02",
        "control": "Account Management",
        "category": "Access Control",
        "keywords": ["account management", "user accounts", "account lifecycle", "provisioning", "deprovisioning", "user onboarding", "offboarding"],
        "frameworks": {"FedRAMP": "AC-2", "NIST_800_53": "AC-2", "CMMC": "AC.L1-3.1.1", "SOC2": "CC6.2"},
        "risk": "HIGH",
        "description": "Manage information system accounts including creation, enabling, modification, disabling, and removal.",
        "remediation": "Implement a formal account management process with documented procedures for provisioning and deprovisioning.",
    },
    {
        "id": "AC-03",
        "control": "Least Privilege / Role-Based Access",
        "category": "Access Control",
        "keywords": ["least privilege", "role-based access", "rbac", "minimum necessary", "need to know", "permissions", "roles"],
        "frameworks": {"FedRAMP": "AC-6", "NIST_800_53": "AC-6", "CMMC": "AC.L1-3.1.2", "SOC2": "CC6.3"},
        "risk": "HIGH",
        "description": "Employ the principle of least privilege, allowing only authorized accesses necessary to accomplish assigned tasks.",
        "remediation": "Audit current permissions and implement RBAC. Remove all excessive admin rights.",
    },
    {
        "id": "AC-04",
        "control": "Multi-Factor Authentication (MFA)",
        "category": "Access Control",
        "keywords": ["mfa", "multi-factor", "two-factor", "2fa", "authentication", "piv", "cac"],
        "frameworks": {"FedRAMP": "IA-2(1)", "NIST_800_53": "IA-2", "CMMC": "IA.L2-3.5.3", "SOC2": "CC6.1"},
        "risk": "HIGH",
        "description": "Implement multifactor authentication for network access to privileged and non-privileged accounts.",
        "remediation": "Enable MFA on all accounts using an authenticator app, hardware token, or PIV/CAC card.",
    },
    {
        "id": "AC-05",
        "control": "Remote Access Controls",
        "category": "Access Control",
        "keywords": ["remote access", "vpn", "remote desktop", "rdp", "ssh", "telework"],
        "frameworks": {"FedRAMP": "AC-17", "NIST_800_53": "AC-17", "CMMC": "AC.L2-3.1.12", "SOC2": "CC6.6"},
        "risk": "MEDIUM",
        "description": "Establish and document usage restrictions, configuration, and connection requirements for remote access.",
        "remediation": "Implement VPN with MFA. Document remote access policy. Disable split tunneling.",
    },
    # ── Configuration Management ────────────────────────────────────────────
    {
        "id": "CM-01",
        "control": "Configuration Management Policy",
        "category": "Configuration Management",
        "keywords": ["configuration management", "baseline configuration", "hardening", "secure configuration", "system configuration"],
        "frameworks": {"FedRAMP": "CM-1", "NIST_800_53": "CM-1", "CMMC": "CM.L2-3.4.1", "SOC2": "CC7.1"},
        "risk": "HIGH",
        "description": "Establish and maintain baseline configurations and inventories of organizational systems.",
        "remediation": "Document baseline security configurations using CIS Benchmarks or DISA STIGs.",
    },
    {
        "id": "CM-02",
        "control": "Change Management / Change Control",
        "category": "Configuration Management",
        "keywords": ["change management", "change control", "change request", "change approval", "cab"],
        "frameworks": {"FedRAMP": "CM-3", "NIST_800_53": "CM-3", "CMMC": "CM.L2-3.4.3", "SOC2": "CC8.1"},
        "risk": "MEDIUM",
        "description": "Document and control changes to the information system including configuration-level changes.",
        "remediation": "Implement a formal change management process with change requests, approval, testing, and rollback procedures.",
    },
    # ── Audit & Accountability ──────────────────────────────────────────────
    {
        "id": "AU-01",
        "control": "Audit Logging & Monitoring",
        "category": "Audit & Accountability",
        "keywords": ["audit log", "logging", "log management", "siem", "monitoring", "centralized logging", "event log"],
        "frameworks": {"FedRAMP": "AU-2", "NIST_800_53": "AU-2", "CMMC": "AU.L2-3.3.1", "SOC2": "CC7.2"},
        "risk": "HIGH",
        "description": "Create, protect, and retain system audit records to the extent needed to enable monitoring, analysis, and investigation.",
        "remediation": "Deploy a SIEM or centralized logging solution. Enable logging on all critical systems and retain logs for 90+ days.",
    },
    {
        "id": "AU-02",
        "control": "Audit Review & Alerting",
        "category": "Audit & Accountability",
        "keywords": ["audit review", "log review", "alert", "anomaly detection", "threat detection", "monitoring alerts"],
        "frameworks": {"FedRAMP": "AU-6", "NIST_800_53": "AU-6", "CMMC": "AU.L2-3.3.5", "SOC2": "CC7.3"},
        "risk": "HIGH",
        "description": "Review and analyze audit records for indications of inappropriate or unusual activity.",
        "remediation": "Configure automated alerts for suspicious events. Establish a daily log review process.",
    },
    # ── Incident Response ───────────────────────────────────────────────────
    {
        "id": "IR-01",
        "control": "Incident Response Plan",
        "category": "Incident Response",
        "keywords": ["incident response", "incident plan", "ir plan", "security incident", "breach response", "incident handling"],
        "frameworks": {"FedRAMP": "IR-1", "NIST_800_53": "IR-1", "CMMC": "IR.L2-3.6.1", "SOC2": "CC7.4"},
        "risk": "HIGH",
        "description": "Develop and implement an incident response capability including preparation, detection, analysis, containment, and recovery.",
        "remediation": "Create a formal Incident Response Plan (IRP). Conduct annual tabletop exercises. Define roles and escalation paths.",
    },
    {
        "id": "IR-02",
        "control": "Incident Reporting",
        "category": "Incident Response",
        "keywords": ["incident reporting", "report incidents", "breach notification", "us-cert", "cisa reporting"],
        "frameworks": {"FedRAMP": "IR-6", "NIST_800_53": "IR-6", "CMMC": "IR.L2-3.6.2", "SOC2": "CC7.4"},
        "risk": "HIGH",
        "description": "Report security incidents to appropriate authorities within required timeframes.",
        "remediation": "Establish incident reporting procedures. For federal systems, report to US-CERT/CISA within 1 hour of discovery.",
    },
    # ── Risk Assessment ─────────────────────────────────────────────────────
    {
        "id": "RA-01",
        "control": "Risk Assessment",
        "category": "Risk Assessment",
        "keywords": ["risk assessment", "risk analysis", "risk evaluation", "threat modeling", "vulnerability assessment", "risk register"],
        "frameworks": {"FedRAMP": "RA-3", "NIST_800_53": "RA-3", "CMMC": "RM.L2-3.11.1", "SOC2": "CC3.2"},
        "risk": "HIGH",
        "description": "Conduct risk assessments to identify threats and vulnerabilities with potential impact on operations.",
        "remediation": "Conduct annual risk assessments. Maintain a risk register. Prioritize remediation by risk level.",
    },
    {
        "id": "RA-02",
        "control": "Vulnerability Scanning",
        "category": "Risk Assessment",
        "keywords": ["vulnerability scan", "vulnerability management", "patch management", "cve", "penetration test", "pen test"],
        "frameworks": {"FedRAMP": "RA-5", "NIST_800_53": "RA-5", "CMMC": "RM.L2-3.11.2", "SOC2": "CC7.1"},
        "risk": "HIGH",
        "description": "Scan for vulnerabilities in organizational systems at least monthly and remediate identified issues.",
        "remediation": "Implement automated vulnerability scanning (Nessus, Qualys, OpenVAS). Patch critical vulns within 30 days.",
    },
    # ── System & Communication Protection ───────────────────────────────────
    {
        "id": "SC-01",
        "control": "Data Encryption in Transit",
        "category": "System & Communications",
        "keywords": ["encryption in transit", "tls", "https", "ssl", "transport encryption", "encrypted communications"],
        "frameworks": {"FedRAMP": "SC-8", "NIST_800_53": "SC-8", "CMMC": "SC.L2-3.13.8", "SOC2": "CC6.7"},
        "risk": "HIGH",
        "description": "Implement cryptographic mechanisms to protect the confidentiality and integrity of transmitted information.",
        "remediation": "Enforce TLS 1.2+ on all endpoints. Disable TLS 1.0/1.1. Use HSTS headers.",
    },
    {
        "id": "SC-02",
        "control": "Data Encryption at Rest",
        "category": "System & Communications",
        "keywords": ["encryption at rest", "disk encryption", "database encryption", "aes", "data at rest", "encrypted storage"],
        "frameworks": {"FedRAMP": "SC-28", "NIST_800_53": "SC-28", "CMMC": "SC.L2-3.13.16", "SOC2": "CC6.7"},
        "risk": "HIGH",
        "description": "Protect the confidentiality of information at rest using encryption.",
        "remediation": "Enable full-disk encryption (BitLocker, FileVault). Encrypt sensitive database columns. Use AES-256.",
    },
    {
        "id": "SC-03",
        "control": "Network Segmentation",
        "category": "System & Communications",
        "keywords": ["network segmentation", "firewall", "dmz", "vlan", "network isolation", "zero trust", "microsegmentation"],
        "frameworks": {"FedRAMP": "SC-7", "NIST_800_53": "SC-7", "CMMC": "SC.L1-3.13.1", "SOC2": "CC6.6"},
        "risk": "MEDIUM",
        "description": "Monitor and control communications at the external boundaries of the system and at key internal boundaries.",
        "remediation": "Implement network segmentation. Deploy firewalls. Use VLANs to separate sensitive systems.",
    },
    # ── Personnel Security ──────────────────────────────────────────────────
    {
        "id": "PS-01",
        "control": "Security Awareness Training",
        "category": "Personnel Security",
        "keywords": ["security training", "security awareness", "phishing training", "user training", "security education"],
        "frameworks": {"FedRAMP": "AT-2", "NIST_800_53": "AT-2", "CMMC": "AT.L2-3.2.1", "SOC2": "CC1.4"},
        "risk": "MEDIUM",
        "description": "Provide basic security awareness training to all personnel as part of initial training and annual refresher.",
        "remediation": "Implement annual security awareness training. Include phishing simulations. Track completion rates.",
    },
    {
        "id": "PS-02",
        "control": "Personnel Screening / Background Checks",
        "category": "Personnel Security",
        "keywords": ["background check", "personnel screening", "vetting", "clearance", "pre-employment screening"],
        "frameworks": {"FedRAMP": "PS-3", "NIST_800_53": "PS-3", "CMMC": "PS.L2-3.9.1", "SOC2": "CC1.4"},
        "risk": "MEDIUM",
        "description": "Screen individuals prior to authorizing access to organizational systems.",
        "remediation": "Establish pre-employment background check procedures. Re-screen personnel with significant role changes.",
    },
    # ── Contingency Planning ────────────────────────────────────────────────
    {
        "id": "CP-01",
        "control": "Backup & Recovery",
        "category": "Contingency Planning",
        "keywords": ["backup", "recovery", "disaster recovery", "business continuity", "rpo", "rto", "data backup"],
        "frameworks": {"FedRAMP": "CP-9", "NIST_800_53": "CP-9", "CMMC": "RE.L2-3.8.9", "SOC2": "A1.2"},
        "risk": "HIGH",
        "description": "Conduct backups of system-level information and protect backup information at storage locations.",
        "remediation": "Implement automated daily backups. Test recovery quarterly. Follow 3-2-1 backup rule. Store offsite/cloud.",
    },
    {
        "id": "CP-02",
        "control": "Contingency / Disaster Recovery Plan",
        "category": "Contingency Planning",
        "keywords": ["contingency plan", "disaster recovery plan", "drp", "bcp", "business continuity plan"],
        "frameworks": {"FedRAMP": "CP-2", "NIST_800_53": "CP-2", "CMMC": "RE.L2-3.8.9", "SOC2": "A1.3"},
        "risk": "HIGH",
        "description": "Develop and implement contingency plans addressing contingency goals, recovery priorities, and metrics.",
        "remediation": "Develop a documented Disaster Recovery Plan (DRP). Define RTOs and RPOs. Test annually.",
    },
    # ── Supply Chain / Third-Party ───────────────────────────────────────────
    {
        "id": "SR-01",
        "control": "Third-Party / Vendor Risk Management",
        "category": "Supply Chain",
        "keywords": ["vendor risk", "third-party risk", "supply chain", "vendor assessment", "contractor risk", "third party"],
        "frameworks": {"FedRAMP": "SA-9", "NIST_800_53": "SR-1", "CMMC": "CM.L2-3.4.6", "SOC2": "CC9.2"},
        "risk": "MEDIUM",
        "description": "Employ supply chain controls and countermeasures to protect organizational systems.",
        "remediation": "Conduct annual vendor risk assessments. Include security requirements in contracts. Review SOC2 reports from vendors.",
    },
    # ── Media Protection ────────────────────────────────────────────────────
    {
        "id": "MP-01",
        "control": "Media Sanitization",
        "category": "Media Protection",
        "keywords": ["media sanitization", "data destruction", "secure disposal", "disk wiping", "degaussing"],
        "frameworks": {"FedRAMP": "MP-6", "NIST_800_53": "MP-6", "CMMC": "MP.L1-3.8.3", "SOC2": "CC6.5"},
        "risk": "MEDIUM",
        "description": "Sanitize information system media prior to disposal, release out of organizational control, or reuse.",
        "remediation": "Implement media sanitization procedures using NIST 800-88 guidelines. Document all disposals.",
    },
]

# Index by keyword for fast lookup
KEYWORD_INDEX: dict[str, list[int]] = {}
for idx, ctrl in enumerate(CONTROL_DATASET):
    for kw in ctrl["keywords"]:
        if kw not in KEYWORD_INDEX:
            KEYWORD_INDEX[kw] = []
        KEYWORD_INDEX[kw].append(idx)
