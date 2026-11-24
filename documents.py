from typing import List, Optional
from pydantic import BaseModel


class Document(BaseModel):
    doc_id: str
    title: str
    content: str
    allowed_roles: List[str]
    embedding: Optional[List[float]] = None


SEED_DOCUMENTS: List[Document] = [
    # HR & People Operations (10 docs)
    Document(
        doc_id="DOC-ALL-01",
        title="2026 Company Holiday & PTO Policy",
        content=(
            "Company offices are closed on New Year's Day, Memorial Day, July 4th, Labor Day, "
            "Thanksgiving (Thu-Fri), and Dec 24-25. Full-time employees accrue 20 days of PTO per year "
            "and may carry over up to 5 unused days into the next calendar year. PTO requests over 5 "
            "consecutive days require manager approval at least 2 weeks in advance."
        ),
        allowed_roles=["employee", "engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-HR-01",
        title="2026 Engineering Compensation Bands (Confidential)",
        content=(
            "L4 Software Engineer base salary band is $145,000-$170,000. "
            "L5 Senior Engineer base salary band is $175,000-$210,000. "
            "L6 Staff Engineer base salary band is $215,000-$255,000. "
            "Annual performance bonus target is 15% across all engineering levels. "
            "Merit reviews occur every March."
        ),
        allowed_roles=["hr", "executive"],
    ),
    Document(
        doc_id="DOC-HR-02",
        title="Health & Benefits Plan Summary 2026",
        content=(
            "Medical plans include PPO, HMO, and HDHP options with employee contributions ranging 5-15%. "
            "Dental and vision coverage are included at no additional cost. 401(k) matching is 100% up to 6% of salary. "
            "Life insurance covers 2x base salary. Employees are eligible for health benefits on day 1."
        ),
        allowed_roles=["employee", "engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-HR-03",
        title="Parental Leave & Family Planning",
        content=(
            "Birth parent leave: 16 weeks paid. Non-birth parent leave: 10 weeks paid. Adoption: 10 weeks paid. "
            "Fertility treatments are covered up to $25,000 lifetime. Emergency childcare assistance available 24/7."
        ),
        allowed_roles=["employee", "engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-HR-04",
        title="Performance Review & Career Development Framework",
        content=(
            "Annual performance reviews occur in March. Ratings: Exceeds (top 10%), Meets (core performers), Developing (improvement needed). "
            "Internal transfer eligibility after 1 year. Tuition reimbursement up to $5,000/year for work-related education."
        ),
        allowed_roles=["employee", "engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-HR-05",
        title="DEI & Anti-Discrimination Policy",
        content=(
            "Company is committed to equal opportunity employment. Zero-tolerance for discrimination based on protected characteristics. "
            "Retaliation against employees reporting discrimination is strictly prohibited and subject to termination."
        ),
        allowed_roles=["employee", "engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-HR-06",
        title="Expense & Travel Policy",
        content=(
            "Flights: economy class unless >6 hours. Hotels: $200/night limit in major cities, $120 in rural. "
            "Meals: $50/day for self, $200 for client entertainment. All expenses require manager approval and must have receipts."
        ),
        allowed_roles=["employee", "engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-HR-07",
        title="Flexible Work & WFH Policy",
        content=(
            "Employees may work fully remote or hybrid (3 days in-office minimum). Core hours are 10am-3pm PT. "
            "Manager approval required for permanent remote status. Home office equipment stipend: $1,500 one-time."
        ),
        allowed_roles=["employee", "engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-HR-08",
        title="Referral Bonus Program",
        content=(
            "Employee referral bonus: $3,000 for engineering hires, $1,500 for other roles. "
            "Referral hired employee must stay 6 months for bonus payout. Unlimited referrals per employee."
        ),
        allowed_roles=["employee", "engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-HR-09",
        title="Sabbatical & Long-Term Leave Options",
        content=(
            "After 5 years of service: 4-week paid sabbatical option (once per 5-year cycle). "
            "Unpaid leave up to 3 months available with manager approval. Healthcare continues during sabbatical."
        ),
        allowed_roles=["hr", "executive"],
    ),

    # Engineering & Technical (12 docs)
    Document(
        doc_id="DOC-ENG-01",
        title="Production Incident Runbook (SEV-1)",
        content=(
            "For SEV-1 production outages, page the on-call SRE via PagerDuty within 5 minutes, "
            "open #inc-war-room in Slack, assign an Incident Commander, and freeze all CI/CD deploys "
            "until root cause is mitigated. Post-incident blameless postmortems are due within 48 hours "
            "and must include a corrective action Jira ticket."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-ENG-02",
        title="Git Workflow & Code Review Standards",
        content=(
            "All PRs require 2 approvals (1 from team lead). Commit messages must reference a Jira ticket. "
            "Max branch age: 2 weeks. No direct pushes to main. All CI checks must pass. Rebase squashing required for >3 commits."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-ENG-03",
        title="Kubernetes Deployment Best Practices",
        content=(
            "All services must run in Kubernetes. Resource requests/limits are mandatory. PodDisruptionBudgets required. "
            "Horizontal Pod Autoscaler (HPA) with min 2, max 10 replicas. Health checks: liveness & readiness required."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-ENG-04",
        title="API Design & OpenAPI Specification",
        content=(
            "All APIs must follow REST conventions. OpenAPI 3.0 spec required. Semantic versioning for endpoints (v1, v2). "
            "Response codes: 200 (success), 400 (client error), 500 (server error). Rate limiting: 1000 req/min per API key."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-ENG-05",
        title="Database Migration & Schema Changes",
        content=(
            "All migrations require DBA review. Zero-downtime migrations mandatory for prod. Rollback plan must be documented. "
            "New columns must be nullable or have defaults. No foreign key cascades on delete. Max migration time: 2 hours."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-ENG-06",
        title="Logging & Observability Standards",
        content=(
            "Structured JSON logging required. Fields: timestamp, level (DEBUG/INFO/WARN/ERROR), service, message, trace_id. "
            "PII must never be logged. Log retention: 30 days hot storage, 90 days cold. All exceptions must be logged with stack trace."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-ENG-07",
        title="Container Registry & Image Management",
        content=(
            "All images pushed to private ECR. Image names: registry.company.com/team/service:tag. "
            "Tags: immutable (use SHA). Max image size: 500MB. Image scanning for CVEs via Trivy before push. No latest tag in prod."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-ENG-08",
        title="API Testing & Quality Standards",
        content=(
            "Minimum code coverage: 80% for new code. Integration tests required for all endpoints. "
            "Load testing for critical APIs (>100 RPS). Chaos engineering tests quarterly. Contract testing with consumers."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-ENG-09",
        title="On-Call Rotation & On-Call Handoff",
        content=(
            "On-call rotation: 1 week per engineer per 5-week cycle. Handoff meeting: 15 mins at rotation boundary. "
            "Max on-call incidents: 5 per week. If exceeded, automated page suppression. Compensation: $50/week on-call rate."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-ENG-10",
        title="Feature Flag & Gradual Rollout Strategy",
        content=(
            "All feature flags go through LaunchDarkly. Canary deployment: 5% → 25% → 50% → 100%. "
            "Min rollout duration: 2 hours between stages. Automated rollback if error rate >0.1%. Feature flags sunset in 2 weeks."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-ENG-11",
        title="Python & Backend Development Guide",
        content=(
            "Python 3.11+. Type hints required (mypy strict mode). No star imports. Max line length: 100. "
            "Use FastAPI for new services. Async preferred for I/O-bound code. Dataclass/Pydantic for models."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-ENG-12",
        title="Monitoring, Alerting & SLA",
        content=(
            "P99 latency SLA: <500ms for user-facing APIs. Availability SLA: 99.95% (4.5 hours downtime/month). "
            "Alert on: error rate >1%, latency P99 >2s, pod restarts >3/hour. Pagerduty alert if SLA breach imminent."
        ),
        allowed_roles=["engineering", "executive"],
    ),

    # Security & Compliance (12 docs)
    Document(
        doc_id="DOC-SEC-01",
        title="Enterprise Data Security, PII & Remote Work Policy",
        content=(
            "All corporate laptops must enforce FileVault or BitLocker full-disk encryption and hardware MFA. "
            "Employees working remotely must connect through the corporate WireGuard VPN before accessing "
            "internal staging or production networks. Customer PII (SSNs, emails, medical or financial records) "
            "must NEVER be pasted into unapproved public AI tools. Suspected data breaches or lost devices "
            "must be reported to security@company.internal within 2 hours."
        ),
        allowed_roles=["employee", "engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-SEC-02",
        title="Authentication & Authorization Framework",
        content=(
            "All APIs require OAuth 2.0 or JWT. Session timeout: 24 hours for web, 90 days for mobile. "
            "MFA mandatory for access to production systems. RBAC with principle of least privilege enforced. "
            "Service accounts: use mTLS, rotate credentials every 90 days."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-SEC-03",
        title="Data Encryption & Key Management",
        content=(
            "Encryption at rest: AES-256 for all data stores. Encryption in transit: TLS 1.3+ required. "
            "Key rotation: 30 days for session keys, 90 days for data keys. HSM usage mandatory for master keys. "
            "No hardcoded secrets in code or container images."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-SEC-04",
        title="Vulnerability Management & Patching",
        content=(
            "Security patches: deploy within 24 hours. Critical CVEs: deploy within 4 hours. "
            "Annual penetration testing required. Bug bounty program active on HackerOne. "
            "Dependency scanning via Dependabot weekly. Max CVE CVSS 7.0 allowed in production."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-SEC-05",
        title="Incident Response & Breach Notification",
        content=(
            "Incident severity: P1 (<1hr), P2 (4hrs), P3 (1 day). Security incidents bypass normal escalation. "
            "Breach notification: customers within 72 hours, regulators within legal timeframe. "
            "Post-incident review mandatory within 1 week."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-SEC-06",
        title="Access Control & Privileged Account Management",
        content=(
            "Prod access requires approval ticket + manager sign-off. Admin access: temporary (max 4 hours). "
            "Shared accounts prohibited. All admin actions logged & audited. Quarterly access reviews required. "
            "Service accounts: no human login capability."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-SEC-07",
        title="Network Security & Firewall Rules",
        content=(
            "All traffic must traverse firewall. Whitelist-based ingress rules. Egress restrictions by service. "
            "No public internet access to data stores. VPC isolation between prod/staging/dev. "
            "WAF rules: block SQLi, XSS, path traversal attacks."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-SEC-08",
        title="Security Awareness & Training",
        content=(
            "Annual mandatory security training for all employees. Phishing simulation: monthly tests. "
            "Report suspicious activity to security@company.internal. No retaliation for good-faith reports. "
            "Security champions program: 1 per team, trained quarterly."
        ),
        allowed_roles=["employee", "engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-SEC-09",
        title="Third-Party & Vendor Management",
        content=(
            "Vendor security review before contract. Annual SOC 2 Type II audit required. "
            "Data processing agreements (DPA) for all processors. Vendor access revoked upon termination. "
            "Critical vendors: redundancy required."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-SEC-10",
        title="Compliance & Regulatory Requirements (HIPAA, CCPA, GDPR)",
        content=(
            "GDPR: right to be forgotten, data portability. CCPA: opt-out mechanisms, privacy policy. "
            "HIPAA (if applicable): BAA with vendors, PHI encryption. GDPR fines: up to 4% of annual revenue. "
            "Data retention: comply with regulations, delete after retention period."
        ),
        allowed_roles=["hr", "executive"],
    ),
    Document(
        doc_id="DOC-SEC-11",
        title="Secure Code Review Checklist",
        content=(
            "OWASP Top 10 mitigation required. Avoid: SQL injection, XSS, CSRF, XXE, RCE, insecure deserialization. "
            "Review: input validation, output encoding, authentication logic. Use security linting tools (Semgrep, Bandit). "
            "Security team reviews all auth/crypto code."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-SEC-12",
        title="Disaster Recovery & Business Continuity Plan",
        content=(
            "RTO (Recovery Time): 4 hours. RPO (Recovery Point): 1 hour max data loss. "
            "Backup frequency: hourly for critical systems, daily for others. Cross-region replication for mission-critical. "
            "Annual disaster recovery drill (DR drill) required."
        ),
        allowed_roles=["engineering", "executive"],
    ),

    # Executive & Strategy (8 docs)
    Document(
        doc_id="DOC-EXEC-01",
        title="Project Titan Acquisition Memo (Restricted)",
        content=(
            "Board approval is pending for the $42M acquisition of CloudScale Analytics, "
            "targeted to close in Q1 2027. Deal lead is CFO Elena Vance. "
            "This memo is strictly confidential under NDA until public SEC filing."
        ),
        allowed_roles=["executive"],
    ),
    Document(
        doc_id="DOC-EXEC-02",
        title="FY2027 Financial Guidance & Revenue Targets",
        content=(
            "Target revenue: $500M (20% YoY growth). Gross margin: 65%. Operating margin: 25%. "
            "Capex budget: $50M for infrastructure. R&D investment: 20% of revenue. "
            "Guidance assumes no major macro disruptions or new compliance costs."
        ),
        allowed_roles=["executive"],
    ),
    Document(
        doc_id="DOC-EXEC-03",
        title="Board of Directors & Officer Compensation",
        content=(
            "CEO total comp: $5M (base $1M + bonus + equity). CTO total comp: $3.5M. "
            "Board compensation: $200K/year + equity for independent directors. Equity vesting: 4-year cliff. "
            "Clawback policy applies to all executives."
        ),
        allowed_roles=["executive"],
    ),
    Document(
        doc_id="DOC-EXEC-04",
        title="Strategic Technology Roadmap 2027-2029",
        content=(
            "2027: AI-driven personalization launch. 2028: Global expansion (3 new regions). 2029: IPO preparation. "
            "Major tech investments: ML platform ($20M), API ecosystem ($15M). "
            "Sunset legacy monolith by end of 2027. Migrate to serverless by 2028."
        ),
        allowed_roles=["executive"],
    ),
    Document(
        doc_id="DOC-EXEC-05",
        title="Investor Relations & Quarterly Earnings",
        content=(
            "Q3 2026 results: revenue $110M, up 18% YoY. EPS: $0.45. "
            "Guidance for Q4: $115M revenue. Market expectations: 20% growth. "
            "Major risks: regulatory uncertainty, competitive pressure, talent retention."
        ),
        allowed_roles=["executive"],
    ),
    Document(
        doc_id="DOC-EXEC-06",
        title="Organizational Restructuring Plan (Confidential)",
        content=(
            "Effective Q1 2027: merge Sales & Customer Success divisions. Create Chief Revenue Officer role. "
            "Target headcount reduction: 5% through attrition. Expected severance cost: $3M. "
            "This information is embargoed until board approval."
        ),
        allowed_roles=["executive"],
    ),
    Document(
        doc_id="DOC-EXEC-07",
        title="Diversity & Inclusion Goals 2027",
        content=(
            "Target women in technical roles: 30% by end of 2027 (currently 22%). "
            "Underrepresented minorities: 20% across company (currently 15%). "
            "Leadership diversity: 40% women in director+ roles. Allocate $2M for D&I initiatives."
        ),
        allowed_roles=["executive"],
    ),
    Document(
        doc_id="DOC-EXEC-08",
        title="Environmental Sustainability & ESG Commitments",
        content=(
            "Carbon neutral by 2030. 100% renewable energy for all data centers. "
            "Water usage reduction target: 30% by 2028. Diversity metric: 50% women by 2030. "
            "Annual ESG report published. Third-party ESG rating: target A- grade."
        ),
        allowed_roles=["executive"],
    ),

    # Product & Customer (8 docs)
    Document(
        doc_id="DOC-PROD-01",
        title="Product Roadmap Q4 2026 - Q2 2027",
        content=(
            "Q4 2026: AI recommendations engine. Q1 2027: mobile app v2.0 launch. Q2 2027: API v3 (breaking changes). "
            "Major features: dark mode, offline sync, real-time collaboration. "
            "Platform deprecations: API v1 sunset June 2027, Flash support end of 2026."
        ),
        allowed_roles=["engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-PROD-02",
        title="Customer Pricing & Packaging Strategy",
        content=(
            "Tier 1 (Starter): $49/month, up to 100 users. Tier 2 (Professional): $299/month, unlimited users. "
            "Tier 3 (Enterprise): custom pricing, SLA, dedicated support. Volume discount: 20% off for 2-year annual. "
            "Pricing increases 5% annually Jan 1. Free tier: limited to 30 days trial."
        ),
        allowed_roles=["engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-PROD-03",
        title="Customer Support & SLA Commitments",
        content=(
            "Starter: email support, 24-hour response. Professional: email + chat, 4-hour response. "
            "Enterprise: dedicated support team, 1-hour response, 24/7 coverage. "
            "Uptime SLA: 99.95%. Maintenance window: Sundays 2am-4am PT, notice 72 hours in advance."
        ),
        allowed_roles=["engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-PROD-04",
        title="Beta Program & Early Access",
        content=(
            "Beta features available to Enterprise tier customers. Opt-in required. "
            "Feedback collection via surveys & usage analytics. Break changes in beta OK (no SLA). "
            "Beta features graduate to stable after 4 weeks + 100 paying customers using it."
        ),
        allowed_roles=["engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-PROD-05",
        title="Data Import/Export & Migration Tools",
        content=(
            "Bulk import: CSV, JSON, SQL. Max file size: 1GB. Export formats: PDF, CSV, JSON, Parquet. "
            "Migration assistant for competing products. Data retention: 30 days after account deletion. "
            "GDPR right to be forgotten: deletion within 30 days."
        ),
        allowed_roles=["engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-PROD-06",
        title="API Rate Limits & Usage Quotas",
        content=(
            "Starter: 100 API calls/min. Professional: 1000 API calls/min. Enterprise: custom limits. "
            "Burst capacity: 2x limit for 30 seconds. Exceeding limit: 429 Too Many Requests. "
            "Monthly quota: Starter 100K calls, Professional 10M calls, Enterprise unlimited."
        ),
        allowed_roles=["engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-PROD-07",
        title="Integrations & Partner Ecosystem",
        content=(
            "Official integrations: Salesforce, HubSpot, Slack, Zapier. Zapier support via public API. "
            "Partner program: revenue share 20%. Partner onboarding: 2-week process. "
            "API stability commitment: backward-compatible changes only (unless major version bump)."
        ),
        allowed_roles=["engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-PROD-08",
        title="Analytics & Usage Reporting",
        content=(
            "Dashboard available to account admins. Metrics: active users, features used, API calls, data stored. "
            "Usage export: CSV monthly. Forecasting: AI-driven cost predictions. "
            "Anomaly detection: alert if usage spikes >50% month-over-month."
        ),
        allowed_roles=["engineering", "hr", "executive"],
    ),

    # Company Operations (2 additional docs)
    Document(
        doc_id="DOC-OPS-01",
        title="Office Facilities & Building Access",
        content=(
            "San Francisco HQ: open 7am-10pm. New York office: open 7am-9pm. "
            "Badge access: temporary during onboarding, permanent after 30 days. "
            "Reserved parking: VP level. Free lunch & snacks for all employees. Dog-friendly office."
        ),
        allowed_roles=["employee", "engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-OPS-02",
        title="IT Hardware & Software Provisioning",
        content=(
            "Laptop options: MacBook Pro 16-inch or Lenovo ThinkPad X1. "
            "Monitors: 2x 27-inch for engineers, 1x 24-inch for others. "
            "Software: licensed tools approved in company marketplace. No unapproved SaaS without IT review. "
            "Hardware replacement: every 3 years."
        ),
        allowed_roles=["employee", "engineering", "hr", "executive"],
    ),
]

from docs_extra_a import DOCS as _DOCS_A, SCENARIOS as _SCEN_A
from docs_extra_b import DOCS as _DOCS_B, SCENARIOS as _SCEN_B
from docs_extra_c import DOCS as _DOCS_C, SCENARIOS as _SCEN_C
from docs_extra_d import DOCS as _DOCS_D, SCENARIOS as _SCEN_D

SEED_DOCUMENTS += [
    Document(doc_id=doc_id, title=title, content=content, allowed_roles=list(roles))
    for doc_id, title, content, roles in _DOCS_A + _DOCS_B + _DOCS_C + _DOCS_D
]

# (question, role authorized for the doc, doc_id expected to be retrieved)
SCENARIOS: List[tuple] = _SCEN_A + _SCEN_B + _SCEN_C + _SCEN_D
