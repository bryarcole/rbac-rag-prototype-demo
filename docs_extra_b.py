ALL = ["employee", "engineering", "hr", "executive"]
ENG = ["engineering", "executive"]
HR = ["hr", "executive"]
EXEC = ["executive"]
MGMT = ["engineering", "hr", "executive"]

DOCS = [
    # ------------------------- Sales & Marketing -------------------------
    (
        "DOC-SAL-01",
        "Inbound Lead Routing Rules",
        "Inbound demo requests are scored in HubSpot and routed by round-robin within 5 minutes of form submission. "
        "Leads scoring 80+ go to the Enterprise pod, 40-79 to the Mid-Market pod, and below 40 to the nurture queue. "
        "Any lead untouched for 2 business hours is automatically reassigned to the next rep in rotation.",
        ALL,
    ),
    (
        "DOC-SAL-02",
        "Discount Approval Matrix",
        "Reps may approve up to 10% discount on list price. Discounts of 11-20% need front-line sales manager sign-off in Salesforce, "
        "21-30% require the VP of Sales, and anything above 30% goes to the Deal Desk committee. "
        "Multi-year prepay deals earn an extra 3% concession that does not count toward the cap.",
        MGMT,
    ),
    (
        "DOC-SAL-03",
        "Sales Commission Plan Mechanics",
        "Account Executives earn 9% of first-year ACV on new logos and 4% on expansions, paid monthly in arrears on the 15th. "
        "Accelerators of 1.5x apply once quarterly attainment passes 110% of quota, and clawback applies if a customer cancels within 90 days. "
        "Spiffs for strategic product launches are capped at $2,500 per rep per quarter.",
        HR,
    ),
    (
        "DOC-SAL-04",
        "CRM Hygiene Standards",
        "Every open opportunity must have a next step, close date, and amount updated within the last 14 days. "
        "Opportunities older than 45 days without activity are auto-flagged by the Friday Pipeline Scrub report. "
        "Duplicate accounts must be merged using the Salesforce Dupe Blocker tool, never by manual deletion.",
        ALL,
    ),
    (
        "DOC-SAL-05",
        "Quote-to-Cash Process",
        "Quotes are generated in Salesforce CPQ and sent via DocuSign for signature. "
        "Once a signed order form lands, Finance creates the invoice in NetSuite within 1 business day, with Net-30 payment terms by default. "
        "Bookings are only recognized after Deal Desk marks the opportunity Closed-Won and Verified.",
        ALL,
    ),
    (
        "DOC-SAL-06",
        "Brand Identity Guidelines",
        "The primary brand color is Harbor Blue (#0B5FA5) with Sandstone (#E8DCC4) as the secondary palette. "
        "Use the Inter typeface for all decks and web content, and keep logo clear-space equal to the height of the letter H. "
        "Approved logo files live in the Brand Hub on Frontify; do not stretch, recolor, or add drop shadows.",
        ALL,
    ),
    (
        "DOC-SAL-07",
        "Press & Social Media Policy",
        "Only the Communications team may speak to journalists; forward all press inquiries to press@company.internal within one hour. "
        "Employees may share company blog posts on personal LinkedIn but must not disclose unreleased features, customer names, or financial results. "
        "Use the #LifeAtCompany hashtag only on approved employer-brand posts.",
        ALL,
    ),
    (
        "DOC-SAL-08",
        "Event & Trade Show Budgets",
        "The field marketing budget is split into Tier A conferences (up to $120,000 per booth), Tier B regionals (up to $35,000), and Tier C meetups (up to $8,000). "
        "Booth staffing is capped at 6 people per Tier A event, and each event must project at least 3x pipeline return within two quarters. "
        "Budget transfers between tiers need Marketing VP approval.",
        MGMT,
    ),
    (
        "DOC-SAL-09",
        "Webinar Production Process",
        "Webinars are scheduled in ON24 at least 21 days ahead, with a dry run 48 hours before airtime. "
        "Plan 25 minutes of content plus 15 minutes of live Q&A, and send three reminder emails at 7 days, 1 day, and 1 hour. "
        "Recordings must be uploaded to the on-demand library within 3 business days.",
        ALL,
    ),
    (
        "DOC-SAL-10",
        "Competitive Battlecard Handling",
        "Battlecards are maintained by Product Marketing in the Highspot library and refreshed every quarter. "
        "Reps must never disparage a competitor by name in writing and must apply the Win/Loss tag in Salesforce on every closed opportunity. "
        "Claims about competitor pricing need a public source link attached.",
        ALL,
    ),
    (
        "DOC-SAL-11",
        "Partner Deal Registration",
        "Resellers register deals through the partner portal, and registrations are valid for 90 days with a single 30-day extension. "
        "The first registrant with a qualified buyer contact wins channel protection, and conflicts are resolved by the Channel Chief within 5 business days. "
        "Registered deals earn a 10% rebate, while sourced-only referrals earn a 5% finder fee.",
        ALL,
    ),
    (
        "DOC-SAL-12",
        "Territory Assignment & Account Segmentation",
        "Accounts are segmented by employee count: SMB under 200, Mid-Market 200-2,000, and Enterprise above 2,000. "
        "Territories are reset every January 2 using the Fiscal Carve plan, and named-account lists are capped at 75 per Enterprise rep. "
        "Mid-year territory changes require RevOps approval and a written rationale.",
        ALL,
    ),
    (
        "DOC-SAL-13",
        "Sales Forecasting Cadence",
        "Reps submit a commit, best-case, and pipeline call in Clari every Monday by 9am PT. "
        "Managers roll up by Tuesday noon, and the VP of Sales presents the weekly forecast to the CFO on Wednesdays. "
        "Forecast accuracy target is within 5% of final quarterly bookings.",
        MGMT,
    ),
    (
        "DOC-SAL-14",
        "Proof-of-Concept Trial Guidelines",
        "Sales engineers may provision a sandbox POC for up to 30 days with a maximum of 25 seeded users. "
        "Each POC needs a written success-criteria document signed by the customer before provisioning, and sandbox data is wiped automatically on day 35. "
        "Requests for custom integrations beyond 40 engineering hours require Solutions Architecture approval.",
        ENG,
    ),
    (
        "DOC-SAL-15",
        "SDR Outbound Cadence & Email Compliance",
        "Outbound sequences run 12 touches over 21 days across email, phone, and LinkedIn using Outreach. "
        "Every email must include an unsubscribe link and the company mailing address to satisfy CAN-SPAM, and EU contacts require a documented legitimate-interest justification. "
        "Do-not-contact requests must be honored in the CRM within 24 hours.",
        ALL,
    ),
    (
        "DOC-SAL-16",
        "Customer Reference Program",
        "Reference customers are tracked in the Referenceable field of Salesforce and may be asked for no more than one call per quarter. "
        "Sales must submit a reference request through the Advocacy form at least 5 business days before it is needed. "
        "Reference customers receive a thank-you gift capped at $100.",
        ALL,
    ),
    (
        "DOC-SAL-17",
        "Content Marketing Editorial Calendar",
        "The blog publishes two long-form posts every week, on Tuesdays and Thursdays, with a monthly gated ebook on the first Wednesday. "
        "Every post needs one subject-matter expert quote, a primary keyword, and sign-off from the Managing Editor. "
        "Submit pitches in the Content Requests board in Asana by the 20th of the prior month.",
        ALL,
    ),
    (
        "DOC-SAL-18",
        "Search & Paid Media Budget Allocation (Confidential)",
        "FY2027 demand generation spend totals $9.4M, with 38% to paid search, 27% to paid social, 20% to review sites, and 15% to ABM display. "
        "Blended customer acquisition cost is currently $18,200 against a target of $15,500. "
        "The board has asked for a 12% reduction in cost per qualified opportunity by Q3.",
        EXEC,
    ),
    (
        "DOC-SAL-19",
        "Sales Kickoff & President's Club Plan (Confidential)",
        "The 2027 Sales Kickoff will take place in Austin from January 12-14 with a $1.1M budget. "
        "President's Club qualifies the top 12% of reps at 120%+ of annual quota and includes a trip to Lisbon for the rep and one guest. "
        "Final qualification lists are embargoed until the CRO signs off.",
        EXEC,
    ),
    (
        "DOC-SAL-20",
        "Security Questionnaire Response Process",
        "Prospect security questionnaires are triaged through the Vanta Trust Center and answered by Security Engineering within 7 business days. "
        "Reuse answers from the approved Answer Library and escalate any question about pen-test results or subprocessors to the CISO's office. "
        "Never share SOC 2 reports without a signed NDA on file.",
        ENG,
    ),
    (
        "DOC-SAL-21",
        "Contract Redlines & Legal Fallback Clauses",
        "Pre-approved fallbacks exist for limitation of liability (up to 12 months of fees), governing law (Delaware), and auto-renewal notice (60 days). "
        "Any request for uncapped liability, source code escrow, or most-favored-customer pricing must go to Legal. "
        "Redlines are tracked in Ironclad and the turnaround SLA is 2 business days.",
        MGMT,
    ),
    (
        "DOC-SAL-22",
        "Marketing Attribution Model",
        "Pipeline is attributed using a W-shaped model: 30% to first touch, 30% to lead creation, 30% to opportunity creation, and 10% spread across remaining touches. "
        "Campaign members must be tagged with a UTM source and medium or they default to Direct. "
        "The attribution dashboard in Looker refreshes nightly at 2am PT.",
        ALL,
    ),
    (
        "DOC-SAL-23",
        "Swag & Merchandise Ordering",
        "Order branded swag through the Printful portal and expect 10 business days for delivery. "
        "The budget limit is $15 per item and $500 per order without manager approval. "
        "Prospect gifts above $75 per person must be logged in the gift register to comply with anti-bribery rules.",
        ALL,
    ),
    (
        "DOC-SAL-24",
        "Strategic Account Plan: Top 10 Targets (Confidential)",
        "The Top 10 named target list includes Fortune 500 logos in banking, logistics, and healthcare with a combined 3-year potential of $64M. "
        "Each target has an executive sponsor and a bespoke land-and-expand plan reviewed monthly by the CEO. "
        "Do not circulate the target list outside the leadership team.",
        EXEC,
    ),
    (
        "DOC-SAL-25",
        "Sales Hiring Ramp & Quota Attainment Benchmarks",
        "New Account Executives ramp over 6 months with quota set at 25%, 50%, and 75% for months 4, 5, and 6. "
        "The historical benchmark is 68% of reps hitting quota, and reps below 50% attainment for two consecutive quarters enter a 60-day performance improvement plan. "
        "SDR to AE promotions require 4 straight months over 100% of meeting goal.",
        HR,
    ),
    # --------------------- Customer Success & Support ---------------------
    (
        "DOC-CS-01",
        "Support Escalation Paths",
        "Tier 1 agents escalate to Tier 2 after 30 minutes without resolution or any mention of data loss. "
        "Tier 2 escalates to the Engineering on-call through the #support-escalations Slack channel using the Escalation Form. "
        "Named Enterprise accounts bypass Tier 1 and route directly to a designated Technical Account Manager.",
        ALL,
    ),
    (
        "DOC-CS-02",
        "Refund & Service Credit Policy",
        "Refunds are available within 30 days of a first purchase for annual plans, prorated by unused full months. "
        "Service credits of 5% of the monthly fee per hour of excess downtime are capped at 30% of the invoice. "
        "Refunds above $5,000 need Finance Director approval and are issued through Stripe within 7 business days.",
        MGMT,
    ),
    (
        "DOC-CS-03",
        "CSAT and NPS Targets",
        "Support targets a CSAT of 92% on the post-ticket survey and a relationship NPS of 45 or higher, measured quarterly through Delighted. "
        "Agents are coached when their rolling 30-day CSAT falls below 88%. "
        "Detractor responses (score 0-6) trigger a follow-up call within 2 business days.",
        ALL,
    ),
    (
        "DOC-CS-04",
        "Customer Onboarding Checklist",
        "New customers receive a kickoff call within 3 business days of contract signature. "
        "The checklist covers SSO setup, data import validation, admin training, and a go-live date confirmed in the Gainsight timeline. "
        "Target time-to-first-value is 21 days, and customers not live by day 45 are flagged for executive attention.",
        ALL,
    ),
    (
        "DOC-CS-05",
        "Quarterly Business Review (QBR) Process",
        "Quarterly business reviews are held for every account above $50,000 ARR using the standard 12-slide template. "
        "Customer Success Managers must send the agenda 5 business days ahead and capture action items in Gainsight within 24 hours. "
        "Each QBR should include adoption metrics, an ROI summary, and a roadmap preview.",
        ALL,
    ),
    (
        "DOC-CS-06",
        "Churn-Risk Playbook",
        "Accounts are labeled at-risk when the health score drops below 60, the executive sponsor leaves, or login activity falls 40% over 30 days. "
        "The CSM opens a Save Plan in Gainsight within 48 hours and schedules an exec-to-exec call within 2 weeks. "
        "Discounts of up to 15% for a multi-year renewal may be offered only with VP of Customer Success approval.",
        MGMT,
    ),
    (
        "DOC-CS-07",
        "Ticket Triage Severity Matrix",
        "Tickets are labeled P1 (service down), P2 (major feature impaired), P3 (minor issue with workaround), and P4 (how-to question). "
        "Internal acknowledgement targets are 15 minutes for P1, 1 hour for P2, 8 hours for P3, and 24 hours for P4. "
        "Agents must set severity in Zendesk before the first reply and may only downgrade P1 with team-lead approval.",
        ALL,
    ),
    (
        "DOC-CS-08",
        "Knowledge Base Style Guide",
        "Articles use second person, present tense, and sentences under 25 words. "
        "Titles begin with a verb such as Configure or Reset, and every article requires at least one annotated screenshot and a Last reviewed date. "
        "Articles older than 180 days are automatically queued for review in Guru.",
        ALL,
    ),
    (
        "DOC-CS-09",
        "Macros and Canned Responses Library",
        "Macros are stored in Zendesk with a prefix naming convention such as BILL- for billing and TECH- for technical. "
        "Always personalize the greeting and the closing line, and never send a macro unedited when the customer is upset. "
        "New macros are proposed in the monthly Macro Review and must be approved by the Support Operations lead.",
        ALL,
    ),
    (
        "DOC-CS-10",
        "Zendesk Admin Runbook",
        "Zendesk triggers and automations are changed only in the sandbox, then deployed on Tuesdays and Thursdays after 6pm PT. "
        "Webhook endpoints to the billing API use rotating tokens that must be refreshed every 60 days. "
        "Engineering owns the Jira Cloud sync and its field mapping, and any change needs a rollback note.",
        ENG,
    ),
    (
        "DOC-CS-11",
        "Customer Data Deletion Request Handling",
        "Deletion requests received under GDPR or CCPA are logged in the Privacy Portal and must be completed within 30 days. "
        "Engineering runs the purge-tenant job, which removes primary database rows within 24 hours and backups on the next 35-day rotation. "
        "Support confirms completion to the customer using the approved Deletion Certificate template.",
        ENG,
    ),
    (
        "DOC-CS-12",
        "Renewal Forecasting & Auto-Renew Notices",
        "Renewals are forecast 120 days before term end, and auto-renew notices go out at 60 days as required by contract. "
        "Renewal managers categorize each deal as Green, Yellow, or Red, with Red renewals reviewed weekly by the VP of Customer Success. "
        "Target gross revenue retention is 91% and net revenue retention is 112%.",
        MGMT,
    ),
    (
        "DOC-CS-13",
        "Customer Health Score Model",
        "Health score runs from 0 to 100 and weights product usage at 40%, support sentiment at 25%, executive engagement at 20%, and invoice payment history at 15%. "
        "Scores are recalculated nightly in Gainsight, and colors are Green (75+), Yellow (50-74), and Red (below 50). "
        "CSMs should review any account that drops 15 points in a week.",
        ALL,
    ),
    (
        "DOC-CS-14",
        "Support Shift Schedule & Weekend Coverage",
        "Support operates on three follow-the-sun shifts: Americas 6am-2pm PT, EMEA 2pm-10pm PT, and APAC 10pm-6am PT. "
        "Weekend coverage is a voluntary rotation paid at 1.5x hourly rate, with a maximum of 2 weekends per month per agent. "
        "Shift swaps must be posted in the scheduling tool at least 48 hours ahead.",
        HR,
    ),
    (
        "DOC-CS-15",
        "Customer Advisory Board",
        "The Customer Advisory Board has 18 members who meet twice yearly, once in person in Chicago and once virtually. "
        "Members are nominated by CSMs and must be accounts above $100,000 ARR with 2+ years of tenure. "
        "Feedback from the board is summarized in the Product Council notes within 10 business days.",
        ALL,
    ),
    (
        "DOC-CS-16",
        "Training Academy & Certification Program",
        "Customers can enroll in the self-paced Academy with three certification levels: Associate, Professional, and Architect. "
        "Each exam has 60 questions with a 75% passing score, and certificates expire after 24 months. "
        "Enterprise customers receive 10 free exam vouchers per contract year.",
        ALL,
    ),
    (
        "DOC-CS-17",
        "Handling Abusive Customers",
        "Agents may end a call or chat after one verbal warning if a customer uses threats, slurs, or harassment. "
        "Document the interaction with the Abusive Contact tag in Zendesk and notify the team lead immediately. "
        "Repeat offenders are reviewed by the Customer Experience Director for possible communication restrictions.",
        ALL,
    ),
    (
        "DOC-CS-18",
        "Top Churned Accounts Postmortem (Confidential)",
        "FY2026 saw 14 enterprise logos churn for $7.8M of ARR, with the largest loss being Halvorsen Logistics at $1.9M. "
        "Top reasons were competitor consolidation (36%), missing SSO features (29%), and executive sponsor turnover (21%). "
        "The retention task force recommends a dedicated rescue team funded at $1.2M.",
        EXEC,
    ),
    (
        "DOC-CS-19",
        "Strategic Customer Concessions & Contract Exceptions (Confidential)",
        "Five strategic customers hold side letters granting extended SLAs, uncapped support hours, or price-lock guarantees through 2028. "
        "Total concession value is estimated at $3.4M annually. "
        "Any new exception requires CEO and General Counsel sign-off and must be recorded in the executive concessions ledger.",
        EXEC,
    ),
    (
        "DOC-CS-20",
        "Community Forum Moderation",
        "Community moderators review flagged posts within 4 hours and remove spam, self-promotion, and any content containing customer credentials. "
        "Moderators award Gold Badge status to members with 50+ accepted answers. "
        "Product questions with no reply after 24 hours are escalated to a staff responder.",
        ALL,
    ),
    (
        "DOC-CS-21",
        "Bug Report Intake from Support to Engineering",
        "Support files confirmed bugs in Jira using the BUG template with reproduction steps, expected result, actual result, and affected customer count. "
        "Engineering triage happens daily at 10am PT, and agents should link every related Zendesk ticket to the Jira issue. "
        "Customers are updated at least every 5 business days until the bug is closed.",
        ALL,
    ),
    (
        "DOC-CS-22",
        "Professional Services Scoping & Rate Card",
        "Professional services are billed at $225 per hour for implementation and $275 per hour for architecture advisory, with a minimum engagement of 20 hours. "
        "Fixed-fee statements of work require a 15% contingency buffer and sign-off from the Services Director. "
        "Unused hours expire 12 months after purchase.",
        MGMT,
    ),
    (
        "DOC-CS-23",
        "Support Headcount & Cost-to-Serve Model (Confidential)",
        "Current cost-to-serve is $14.20 per ticket, with a target of $11.50 by the end of FY2027 through chatbot deflection. "
        "The plan freezes support headcount at 86 agents while ticket volume grows 22%. "
        "A vendor proposal to outsource Tier 1 to Manila would save an estimated $2.1M but remains unannounced.",
        EXEC,
    ),
    (
        "DOC-CS-24",
        "Voice of Customer Feedback Loop",
        "Feedback is collected from surveys, sales call transcripts in Gong, and support tickets, then tagged in Productboard by theme. "
        "The Voice of Customer report is published on the first Monday of each month and reviewed by Product leadership. "
        "Customers who submit a feature request receive a status update within 30 days.",
        ALL,
    ),
    (
        "DOC-CS-25",
        "Enterprise Customer Executive Sponsor Program (Confidential)",
        "Each of the top 25 customers by ARR is paired with a named executive sponsor who holds two touchpoints per year. "
        "Sponsors receive a briefing document with open escalations, renewal dates, and unreleased roadmap items under NDA. "
        "Sponsor assignments are reviewed each October by the CEO.",
        EXEC,
    ),
]

SCENARIOS = [
    ("How fast are inbound demo leads routed by round-robin and what lead score goes to the Enterprise pod?", "employee", "DOC-SAL-01"),
    ("What discount can a rep approve and when does the VP of Sales need to sign off?", "engineering", "DOC-SAL-02"),
    ("What commission percent do Account Executives earn on new logos and when do accelerators apply?", "hr", "DOC-SAL-03"),
    ("How long can an opportunity sit without activity before the Friday Pipeline Scrub flags it?", "employee", "DOC-SAL-04"),
    ("How does a quote go from Salesforce CPQ and DocuSign to a NetSuite invoice with Net-30 terms?", "employee", "DOC-SAL-05"),
    ("What is the Harbor Blue hex color and which typeface do the brand guidelines require?", "employee", "DOC-SAL-06"),
    ("Can I post about unreleased features on my personal LinkedIn or talk to journalists?", "employee", "DOC-SAL-07"),
    ("What is the booth budget for Tier A trade show conferences and what pipeline return is required?", "engineering", "DOC-SAL-08"),
    ("How many days ahead do I schedule an ON24 webinar and when do reminder emails go out?", "employee", "DOC-SAL-09"),
    ("Where do I find Highspot battlecards and can I name competitors in writing?", "employee", "DOC-SAL-10"),
    ("How long is a partner deal registration valid and who resolves channel conflicts?", "employee", "DOC-SAL-11"),
    ("How are SMB, Mid-Market, and Enterprise accounts segmented by employee count in territory assignment?", "employee", "DOC-SAL-12"),
    ("When do reps submit the Clari commit and best-case forecast call each week?", "engineering", "DOC-SAL-13"),
    ("How long can a sales engineer run a sandbox POC and how many seeded users are allowed?", "engineering", "DOC-SAL-14"),
    ("How many touches are in an Outreach SDR sequence and what does CAN-SPAM require in emails?", "employee", "DOC-SAL-15"),
    ("How often can a reference customer be asked for a reference call and what is the thank-you gift cap?", "employee", "DOC-SAL-16"),
    ("How many blog posts publish each week and when is the monthly gated ebook?", "employee", "DOC-SAL-17"),
    ("What is the FY2027 demand generation budget and the blended customer acquisition cost target?", "executive", "DOC-SAL-18"),
    ("Where is the 2027 Sales Kickoff and who qualifies for President's Club?", "executive", "DOC-SAL-19"),
    ("How quickly must Security Engineering answer a prospect security questionnaire and can I share the SOC 2 report?", "engineering", "DOC-SAL-20"),
    ("What are the pre-approved fallback clauses for limitation of liability and auto-renewal notice in contract redlines?", "engineering", "DOC-SAL-21"),
    ("How does the W-shaped marketing attribution model split pipeline credit?", "employee", "DOC-SAL-22"),
    ("How do I order branded swag through Printful and what is the gift register limit?", "employee", "DOC-SAL-23"),
    ("Which Fortune 500 targets are on the Top 10 strategic account plan and what is the 3-year potential?", "executive", "DOC-SAL-24"),
    ("How long is the new Account Executive ramp and when does a rep enter a performance improvement plan for low quota attainment?", "hr", "DOC-SAL-25"),
    ("When does a Tier 1 agent escalate to Tier 2 and which Slack channel is used for Engineering on-call escalations?", "employee", "DOC-CS-01"),
    ("What is the refund window for annual plans and what service credit applies for excess downtime?", "engineering", "DOC-CS-02"),
    ("What are the CSAT and NPS targets and what happens after a detractor response?", "employee", "DOC-CS-03"),
    ("What does the customer onboarding checklist cover and what is the target time-to-first-value?", "employee", "DOC-CS-04"),
    ("Which accounts get a quarterly business review and how many slides are in the QBR template?", "employee", "DOC-CS-05"),
    ("What triggers an at-risk label in the churn playbook and how big a discount can be offered for a multi-year renewal?", "engineering", "DOC-CS-06"),
    ("What are the P1 through P4 ticket severity labels and their acknowledgement targets?", "employee", "DOC-CS-07"),
    ("What are the knowledge base style guide rules for article titles and sentence length?", "employee", "DOC-CS-08"),
    ("What is the Zendesk macro naming convention and when should I not send a canned response unedited?", "employee", "DOC-CS-09"),
    ("When are Zendesk triggers deployed from the sandbox and how often must billing webhook tokens rotate?", "engineering", "DOC-CS-10"),
    ("How long do we have to complete a GDPR deletion request and what does the purge-tenant job do?", "engineering", "DOC-CS-11"),
    ("When are renewals forecast and when do auto-renew notices go out?", "engineering", "DOC-CS-12"),
    ("How is the customer health score weighted across usage, sentiment, engagement, and payment history?", "employee", "DOC-CS-13"),
    ("What are the follow-the-sun support shifts and how is weekend coverage paid?", "hr", "DOC-CS-14"),
    ("How many members are on the Customer Advisory Board and what ARR is required to join?", "employee", "DOC-CS-15"),
    ("How many questions are in a Training Academy certification exam and what is the passing score?", "employee", "DOC-CS-16"),
    ("What should I do when a customer uses threats or harassment on a call?", "employee", "DOC-CS-17"),
    ("How much ARR did we lose to enterprise churn in FY2026 and what were the top churn reasons?", "executive", "DOC-CS-18"),
    ("Which strategic customers have side letters or price-lock guarantees and what is the concession value?", "executive", "DOC-CS-19"),
    ("How fast must community moderators review flagged forum posts and what earns a Gold Badge?", "employee", "DOC-CS-20"),
    ("What information goes in a Jira BUG template when support reports a confirmed bug to Engineering?", "employee", "DOC-CS-21"),
    ("What are the professional services hourly rates for implementation and architecture advisory?", "engineering", "DOC-CS-22"),
    ("What is the current cost-to-serve per ticket and is Tier 1 support being outsourced?", "executive", "DOC-CS-23"),
    ("How is the monthly Voice of Customer report built from Gong and Productboard feedback?", "employee", "DOC-CS-24"),
    ("How does the executive sponsor program pair sponsors with the top 25 customers by ARR?", "executive", "DOC-CS-25"),
]
