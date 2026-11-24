ALL = ["employee", "engineering", "hr", "executive"]
ENG = ["engineering", "executive"]
HR = ["hr", "executive"]
EXEC = ["executive"]
MGMT = ["engineering", "hr", "executive"]

DOCS = [
    # ---------------- Finance & Accounting ----------------
    ("DOC-FIN-01", "Expense Report Submission Deadlines",
     "Expense reports must be submitted in Concur Expense within 30 days of the transaction date, with itemized receipts attached for any charge over $25. "
     "Reports submitted 31-60 days late need VP approval and are paid in the next quarterly reimbursement run. "
     "Approved reports are reimbursed every Friday by direct deposit.", ALL),
    ("DOC-FIN-02", "Purchase Order Approval Thresholds",
     "Purchases under $1,000 need manager approval only. "
     "Purchase orders from $1,000 to $24,999 require director sign-off in Coupa, $25,000 to $99,999 require the VP of Finance, and anything at or above $100,000 requires CFO approval plus three competitive bids. "
     "Splitting a purchase to stay under a threshold is a policy violation.", ALL),
    ("DOC-FIN-03", "Month-End Close Calendar",
     "The month-end close follows a business-day schedule: BD1 subledger cutoff, BD2 accrual journal entries posted in NetSuite, BD3 intercompany eliminations, BD4 flux analysis review, and BD5 controller sign-off. "
     "Journal entries submitted after BD3 require a controller waiver. "
     "Department managers must submit accrual estimates by noon on BD1.", MGMT),
    ("DOC-FIN-04", "Revenue Recognition Policy (ASC 606)",
     "Subscription revenue is recognized ratably over the contract term beginning on the service activation date. "
     "Professional services revenue is recognized as milestones are accepted, and multi-element deals are split using standalone selling price. "
     "Contract modifications that change term or price must be reviewed by Revenue Accounting before booking.", MGMT),
    ("DOC-FIN-05", "Annual Budget Planning Cycle",
     "Budget planning opens each August 1 with a department kickoff in Adaptive Planning, drafts are due September 15, and the CFO review runs through October. "
     "The final operating budget is locked on November 30 and mid-year reforecasts open in June. "
     "Unspent budget does not roll over to the next fiscal year.", ALL),
    ("DOC-FIN-06", "Corporate Credit Card Rules",
     "Brex corporate cards are issued to employees with a manager-approved business need and carry a default $5,000 monthly limit. "
     "Cards must never be used for personal purchases, cash advances, or recurring subscriptions without a Coupa PO. "
     "Receipts must be uploaded within 5 days of each swipe or the card is frozen.", ALL),
    ("DOC-FIN-07", "Mileage Reimbursement & Per Diem Rates",
     "Personal vehicle mileage is reimbursed at the IRS standard rate, currently 70 cents per mile, with a log of start and end odometer readings. "
     "Domestic per diem for overnight client travel is $75 per day and international per diem follows the GSA foreign rate table. "
     "Commuting miles between home and the primary office are not reimbursable.", ALL),
    ("DOC-FIN-08", "External Audit Preparation Checklist",
     "The annual financial statement audit by the outside auditor begins in January, and managers must deliver their PBC (prepared by client) request items within 5 business days. "
     "Control owners must retain SOX evidence such as approval screenshots and reconciliations for seven years. "
     "Walkthrough meetings are scheduled by the Controller and attendance is mandatory for process owners.", MGMT),
    ("DOC-FIN-09", "Vendor Onboarding & W-9 Collection",
     "New vendors must complete a supplier intake form in Coupa and provide a signed W-9 (or W-8BEN for foreign vendors) before the first invoice is paid. "
     "Banking details are verified by a call-back to a known contact to prevent payment fraud. "
     "Vendor onboarding typically takes 7 business days.", ALL),
    ("DOC-FIN-10", "Accounts Payable Invoice Payment Terms",
     "Standard supplier payment terms are net 45 days from the invoice receipt date, with payment runs every Tuesday and Thursday. "
     "Invoices must be emailed to the AP inbox with a valid PO number or they are returned unpaid. "
     "Early-payment discounts of 2/10 net 30 are taken only when approved by Treasury.", ALL),
    ("DOC-FIN-11", "Cash Forecast & Treasury Positions (Confidential)",
     "Current unrestricted cash and marketable securities total $186M, with a 13-week rolling cash forecast showing a low point of $142M in week 9. "
     "Excess cash is laddered in treasury bills and AAA money-market funds with a 90-day average maturity. "
     "Distribution of the forecast outside the executive team is prohibited.", EXEC),
    ("DOC-FIN-12", "Foreign Currency Expense Reimbursement",
     "Expenses incurred in foreign currencies are converted to USD using the exchange rate on the transaction date from the card statement or the Oanda rate table. "
     "Employees should not be out of pocket for currency conversion fees on pre-approved travel, up to 3% of the transaction. "
     "Cash withdrawals abroad are limited to $300 per trip.", ALL),
    ("DOC-FIN-13", "Payroll Cutoff & Off-Cycle Payments",
     "Payroll is processed semi-monthly on the 15th and the last business day, with Workday changes locked three business days before each pay date. "
     "Off-cycle checks for terminated employees are issued within 72 hours in states requiring immediate final pay, and manual payroll corrections require HR plus Payroll Manager approval. "
     "Retroactive pay adjustments are capped at 90 days.", HR),
    ("DOC-FIN-14", "Software Development Cost Capitalization",
     "Engineers working on eligible internal-use software must log time against capitalizable Jira epics so Finance can capitalize costs under ASC 350-40. "
     "Costs incurred during the preliminary project stage and post-implementation maintenance are expensed. "
     "Capitalized costs are amortized straight-line over 36 months once the feature is generally available.", ENG),
    ("DOC-FIN-15", "Employee Recognition Awards & Gift Card Tax Treatment",
     "Cash and gift card awards are taxable wages and are processed through payroll, not through expense reports. "
     "Non-cash length-of-service awards up to $400 are excluded from tax. "
     "Peer-to-peer Bonusly points are redeemable for merchandise and are capped at $100 per month.", ALL),
    ("DOC-FIN-16", "Sales Tax & VAT Nexus Guidelines",
     "Sales tax is collected through Avalara on SaaS subscriptions in states with economic nexus, which begins at $100,000 in sales or 200 transactions. "
     "EU and UK customers are charged VAT unless a valid VAT ID is on file. "
     "Managers must notify the Tax team before hiring remote employees in a new state because it can create nexus.", MGMT),
    ("DOC-FIN-17", "409A Valuation & Option Strike Price (Confidential)",
     "The most recent independent 409A valuation sets common stock fair market value at $14.20 per share, effective for 12 months or until the next material event. "
     "New option grants are priced at this strike price after board approval. "
     "Disclosure of the valuation to non-executives is restricted until grant letters are issued.", EXEC),
    ("DOC-FIN-18", "Charitable Matching Gifts Program",
     "The company matches employee donations to registered 501(c)(3) nonprofits dollar for dollar up to $1,000 per employee per calendar year through the Benevity portal. "
     "Matches are processed in the month after the donation is verified. "
     "Political and religious organizations are not eligible.", ALL),
    ("DOC-FIN-19", "Petty Cash & Cash Handling Procedures",
     "Office petty cash funds are limited to $500 and held in a locked drawer managed by the office manager. "
     "Every disbursement needs a signed voucher, and the fund is reconciled and replenished on the first Monday of each month. "
     "Discrepancies over $20 must be reported to the Controller within one business day.", ALL),
    ("DOC-FIN-20", "Cloud Cost Allocation & FinOps Tagging",
     "Every AWS resource must carry the cost-center, service-owner, and environment tags or it is flagged in the weekly FinOps report. "
     "Untagged spend over $500 per week is escalated to the engineering director. "
     "Savings Plan and reserved-instance coverage targets are 70 percent for steady-state workloads.", ENG),
    ("DOC-FIN-21", "Quarterly Board Financial Package (Confidential)",
     "The board package includes the consolidated P&L, a bookings and ARR bridge, net revenue retention of 118 percent, and a variance narrative against plan. "
     "Draft materials are distributed through the Diligent portal five days before each board meeting. "
     "Material weaknesses or unusual items must be flagged to the Audit Committee chair in advance.", EXEC),
    ("DOC-FIN-22", "Employee Stock Purchase Plan (ESPP) Enrollment",
     "Eligible employees can buy company stock at a 15 percent discount through payroll deductions of 1 to 10 percent of pay. "
     "Offering periods run six months starting March 1 and September 1, and the purchase price is based on the lower of the start or end price. "
     "Enrollment must be completed in the Shareworks portal two weeks before the period starts.", ALL),
    ("DOC-FIN-23", "Wage Garnishment & Withholding Orders",
     "Payroll must honor court-ordered garnishments, child support orders, and IRS levies within the first pay period after receipt. "
     "Total garnishment cannot exceed 25 percent of disposable earnings under federal limits, while child support may reach 50 percent. "
     "HR forwards each order to the Payroll Manager and notifies the employee in writing.", HR),
    ("DOC-FIN-24", "Department Budget Variance Reporting",
     "Budget owners must explain variances greater than 10 percent or $25,000 versus plan in the monthly variance template by BD8. "
     "Headcount-related overages require a hiring review with the FP&A partner. "
     "Unfavorable variances persisting over two consecutive months trigger a reforecast.", MGMT),
    ("DOC-FIN-25", "Credit Facility & Debt Covenant Summary (Confidential)",
     "The $75M revolving credit facility with Meridian Bank carries a minimum liquidity covenant of $50M and a maximum total leverage ratio of 3.0x. "
     "Compliance certificates are due within 45 days of each quarter end. "
     "The drawn balance is currently $0 and the facility matures in March 2029.", EXEC),

    # ---------------- Legal & Compliance ----------------
    ("DOC-LEG-01", "Contract Review Intake & SLA",
     "Submit all vendor and customer contracts through the Ironclad intake form before signing. "
     "Legal commits to a first-pass review within 3 business days for standard agreements and 7 business days for non-standard terms. "
     "Contracts sent for signature without Legal review are not binding on the company.", ALL),
    ("DOC-LEG-02", "Mutual NDA Template Usage",
     "Use the approved mutual NDA template from the Legal wiki for all prospective partners, with a standard term of 2 years and confidentiality obligations surviving 5 years. "
     "Any redline to the definition of confidential information or the residuals clause must be approved by Legal. "
     "One-way NDAs are only allowed when the company is solely receiving information.", ALL),
    ("DOC-LEG-03", "Employee IP Assignment & Invention Disclosure",
     "All work created within the scope of employment belongs to the company under the signed Proprietary Information and Inventions Agreement. "
     "Employees must file an invention disclosure form within 30 days of conceiving a potentially patentable idea. "
     "Prior inventions must be listed in Exhibit A at hire to be excluded.", ALL),
    ("DOC-LEG-04", "Open-Source License Policy",
     "Approved licenses for use in production code are MIT, BSD, and Apache 2.0. "
     "Copyleft licenses such as GPL and AGPL are prohibited in distributed or hosted products without a written exception from Legal. "
     "Dependencies are scanned with FOSSA on every pull request and an SBOM is exported at each release.", ENG),
    ("DOC-LEG-05", "Records Retention Schedule",
     "Financial records and tax filings are retained 7 years, employment records 7 years after separation, customer contracts 7 years after expiration, and marketing materials 3 years. "
     "Email is auto-deleted after 3 years unless subject to a legal hold. "
     "Destruction of records must follow the approved schedule and be logged by Records Management.", ALL),
    ("DOC-LEG-06", "Data Subject Access Request (DSAR) Handling",
     "Requests from individuals to access, correct, or delete personal data are logged in OneTrust and must be answered within 30 days under GDPR and 45 days under CCPA. "
     "Employees who receive a request must forward it to privacy@company.internal within 1 business day. "
     "Identity verification is required before any data is released.", ALL),
    ("DOC-LEG-07", "Litigation Hold Procedure",
     "When Legal issues a litigation hold notice, recipients must immediately stop deleting emails, Slack messages, and documents related to the matter. "
     "IT suspends auto-deletion for the custodians listed in the notice. "
     "Holds stay in effect until Legal sends a written release, and custodians must acknowledge the notice within 48 hours.", MGMT),
    ("DOC-LEG-08", "Trademark & Brand Usage Guidelines",
     "Use the company logo only from the Brand Hub with the required clear space of one logo height on all sides. "
     "Never alter the colors, stretch the wordmark, or combine it with partner logos without Marketing approval. "
     "Partners and customers need a signed trademark license to use our marks in their materials.", ALL),
    ("DOC-LEG-09", "Export Controls & Sanctions Screening",
     "Our encryption software is classified under ECCN 5D002 with license exception ENC, so exports to embargoed countries including Iran, Cuba, North Korea, Syria, and Crimea are prohibited. "
     "New customers and resellers are screened against the OFAC SDN list in Descartes before contract signature. "
     "Engineers must not share source code with persons in restricted destinations.", ENG),
    ("DOC-LEG-10", "Ethics Hotline & Whistleblower Protections",
     "Concerns about fraud, accounting irregularities, or misconduct can be reported anonymously to the EthicsPoint hotline 24 hours a day. "
     "The company prohibits retaliation against anyone who reports in good faith, and the Audit Committee reviews all financial complaints. "
     "Reports are acknowledged within 5 business days.", ALL),
    ("DOC-LEG-11", "Conflict of Interest Disclosure",
     "Employees must disclose outside business activities, board seats, and financial interests of more than 1 percent in vendors or competitors in the annual disclosure form. "
     "Hiring or supervising a family member requires prior approval from HR and Legal. "
     "Undisclosed conflicts may lead to disciplinary action.", ALL),
    ("DOC-LEG-12", "Anti-Bribery & Gifts Policy (FCPA)",
     "Employees may not offer anything of value to a government official to obtain business, and facilitation payments are prohibited. "
     "Gifts and meals given to or received from business partners are limited to $100 per person per occasion and must be logged in the gift register. "
     "Third-party intermediaries in high-risk countries require anti-corruption due diligence.", ALL),
    ("DOC-LEG-13", "Insider Trading & Trading Window Policy",
     "Employees in possession of material nonpublic information may not trade company or partner securities. "
     "The quarterly blackout window begins two weeks before quarter end and ends one full trading day after earnings are released. "
     "Directors and officers need pre-clearance from Securities Counsel, and 10b5-1 plans must be set up during an open window.", ALL),
    ("DOC-LEG-14", "Employee Investigations Protocol",
     "HR opens an investigation case in Workday within 2 business days of a complaint and assigns a neutral investigator. "
     "Interviews are documented, witnesses are reminded of confidentiality, and findings are delivered to the complainant within 30 days. "
     "Outcomes and corrective actions are reviewed with Employment Counsel before communication.", HR),
    ("DOC-LEG-15", "Separation Agreement & Severance Release Template",
     "Standard severance is two weeks of base pay per year of service with a minimum of 4 weeks, conditioned on a signed general release. "
     "Employees age 40 or older get 21 days to consider the agreement (45 days for group layoffs) and 7 days to revoke under the OWBPA. "
     "All separation agreements must be approved by Employment Counsel.", HR),
    ("DOC-LEG-16", "Social Media & Public Statements Policy",
     "Only the Communications team and designated spokespersons may speak on behalf of the company to press or analysts. "
     "Employees posting on personal social media must make clear that views are their own and must not disclose customer names or nonpublic financial results. "
     "Media inquiries should be forwarded to press@company.internal.", ALL),
    ("DOC-LEG-17", "Subpoena & Government Request Handling",
     "Managers who receive a subpoena, search warrant, or regulator inquiry must not respond directly and must forward it to the General Counsel within 24 hours. "
     "Legal verifies jurisdiction and scope before any documents or customer data are produced. "
     "Employees approached by agents have the right to request that Legal be present.", MGMT),
    ("DOC-LEG-18", "Pending Litigation Summary (Confidential)",
     "There are three active matters: Halvorsen v. Company (a wage and hour class action with estimated exposure of $2.1M), a patent infringement claim by Brightwave Systems, and a vendor contract dispute with Northgate Cloud. "
     "Outside counsel reserves have been set at $3.4M. "
     "This summary is attorney-client privileged and must not be forwarded.", EXEC),
    ("DOC-LEG-19", "Patent Portfolio Strategy (Confidential)",
     "The company holds 14 granted patents and 9 pending applications, with filing priority on streaming ingestion and access control inventions. "
     "The 2027 patent budget is $850,000 and continuation filings are planned for the Q1 anchor patent. "
     "Defensive publication is used for non-core ideas.", EXEC),
    ("DOC-LEG-20", "Contract Signing Authority & Delegation Matrix",
     "Only authorized signers listed in the delegation of authority matrix may execute contracts through DocuSign. "
     "Managers may sign up to $10,000, directors up to $50,000, VPs up to $250,000, and only the CEO or CFO above $250,000. "
     "Signing a contract beyond your authority is grounds for corrective action.", ALL),
    ("DOC-LEG-21", "Customer Contract Fallback Positions",
     "In customer negotiations the standard limitation of liability is capped at 12 months of fees, and sales may fall back to 24 months with Legal approval. "
     "Uncapped liability is only allowed for confidentiality breach and IP infringement indemnity. "
     "Auto-renewal terms must keep a 60-day non-renewal notice window.", MGMT),
    ("DOC-LEG-22", "Copyright & Third-Party Content Usage",
     "Images, fonts, music, and stock photos used in marketing must come from the licensed Getty and Adobe Stock libraries or have written permission. "
     "Do not copy content from websites or competitors into presentations or documentation. "
     "Attribution requirements for Creative Commons material must be recorded in the content tracker.", ALL),
    ("DOC-LEG-23", "Board Resolutions & Authorization Register (Confidential)",
     "The register lists all board resolutions in force, including the approved $20M stock repurchase authorization, executive severance plan amendments, and delegation of acquisition authority up to $5M to the CEO. "
     "Resolutions are maintained by the Corporate Secretary in Diligent. "
     "Access is limited to officers and directors.", EXEC),
    ("DOC-LEG-24", "Digital Accessibility Compliance (ADA & WCAG)",
     "All customer-facing web and mobile products must conform to WCAG 2.1 Level AA and ship with a current VPAT. "
     "Engineers run axe automated checks and screen reader testing with VoiceOver and NVDA before launch. "
     "High-severity accessibility defects must be fixed within 30 days.", ALL),
    ("DOC-LEG-25", "Vendor DPA & Subprocessor Review",
     "Vendors that process customer personal data must sign the Data Processing Addendum with Standard Contractual Clauses before go-live. "
     "Legal maintains the public subprocessor list, and customers are given 30 days notice of any new subprocessor. "
     "Annual reviews check vendor breach history and certifications such as ISO 27701.", MGMT),
]

SCENARIOS = [
    ("How many days do I have to submit an expense report in Concur?", "employee", "DOC-FIN-01"),
    ("Who has to approve a $50,000 purchase order in Coupa?", "employee", "DOC-FIN-02"),
    ("When are accrual estimates due during the month-end close?", "engineering", "DOC-FIN-03"),
    ("How is subscription revenue recognized under ASC 606 for a multi-element deal?", "engineering", "DOC-FIN-04"),
    ("When does the annual budget planning cycle open and when are drafts due?", "employee", "DOC-FIN-05"),
    ("What is the monthly limit on my Brex corporate card and when must receipts be uploaded?", "employee", "DOC-FIN-06"),
    ("What is the mileage reimbursement rate per mile for using my personal vehicle?", "employee", "DOC-FIN-07"),
    ("How quickly must managers deliver PBC request items for the annual audit?", "engineering", "DOC-FIN-08"),
    ("What tax form does a new vendor need before we can pay their first invoice?", "employee", "DOC-FIN-09"),
    ("What are the standard net payment terms for supplier invoices and which days are payment runs?", "employee", "DOC-FIN-10"),
    ("What is the 13-week cash forecast low point and current treasury cash position?", "executive", "DOC-FIN-11"),
    ("What exchange rate is used when I expense something in euros?", "employee", "DOC-FIN-12"),
    ("How many days before pay date do payroll changes lock in Workday?", "hr", "DOC-FIN-13"),
    ("Which Jira epics do I log time to so software costs can be capitalized?", "engineering", "DOC-FIN-14"),
    ("Are gift card awards taxable and do they go through expense reports?", "employee", "DOC-FIN-15"),
    ("What triggers economic nexus for sales tax and who do I notify before hiring remotely in a new state?", "engineering", "DOC-FIN-16"),
    ("What is the current 409A fair market value per share for new option grants?", "executive", "DOC-FIN-17"),
    ("How much will the company match for my donation to a 501(c)(3) charity through Benevity?", "employee", "DOC-FIN-18"),
    ("How much is the petty cash fund limit and when is it reconciled?", "employee", "DOC-FIN-19"),
    ("Which tags must every AWS resource have for FinOps cost allocation?", "engineering", "DOC-FIN-20"),
    ("What is in the quarterly board financial package and when is it distributed via Diligent?", "executive", "DOC-FIN-21"),
    ("What discount do I get under the ESPP and when do offering periods start?", "employee", "DOC-FIN-22"),
    ("What is the maximum percentage of disposable earnings that can be garnished for a court order?", "hr", "DOC-FIN-23"),
    ("What size budget variance requires an explanation in the monthly variance report?", "engineering", "DOC-FIN-24"),
    ("What is the minimum liquidity covenant on the Meridian Bank revolving credit facility?", "executive", "DOC-FIN-25"),
    ("How many business days does Legal take to review a contract submitted through Ironclad?", "employee", "DOC-LEG-01"),
    ("What is the standard term of the mutual NDA template and how long does confidentiality survive?", "employee", "DOC-LEG-02"),
    ("How soon do I have to file an invention disclosure form for a patentable idea?", "employee", "DOC-LEG-03"),
    ("Can I use an AGPL library in our hosted product or only MIT and Apache licensed ones?", "engineering", "DOC-LEG-04"),
    ("How long do we retain employment records after an employee leaves?", "employee", "DOC-LEG-05"),
    ("How many days do we have to respond to a CCPA data deletion request and where do I forward it?", "employee", "DOC-LEG-06"),
    ("What must I do when I receive a litigation hold notice and how fast must I acknowledge?", "engineering", "DOC-LEG-07"),
    ("What clear space is required around the company logo from the Brand Hub?", "employee", "DOC-LEG-08"),
    ("Can we ship our encryption software to a customer in an embargoed country and what is the ECCN?", "engineering", "DOC-LEG-09"),
    ("How do I anonymously report accounting fraud through the EthicsPoint hotline?", "employee", "DOC-LEG-10"),
    ("Do I need to disclose a family member I would supervise and who approves it?", "employee", "DOC-LEG-11"),
    ("What is the dollar limit on gifts to business partners under the FCPA policy?", "employee", "DOC-LEG-12"),
    ("When does the quarterly trading blackout window begin and end?", "employee", "DOC-LEG-13"),
    ("How quickly does HR open an investigation case and deliver findings after a complaint?", "hr", "DOC-LEG-14"),
    ("How many days do employees over 40 get to consider a separation agreement under OWBPA?", "hr", "DOC-LEG-15"),
    ("Who is allowed to speak to the press and where do I forward media inquiries?", "employee", "DOC-LEG-16"),
    ("What should a manager do within 24 hours after receiving a subpoena or search warrant?", "engineering", "DOC-LEG-17"),
    ("What is the estimated exposure in the Halvorsen wage and hour class action?", "executive", "DOC-LEG-18"),
    ("How many granted patents and pending applications does the company have and what is the 2027 patent budget?", "executive", "DOC-LEG-19"),
    ("What is the contract signing limit for a director in DocuSign?", "employee", "DOC-LEG-20"),
    ("What is the standard liability cap in customer contracts and how far can we fall back?", "engineering", "DOC-LEG-21"),
    ("Which stock photo libraries are licensed for use in marketing materials?", "employee", "DOC-LEG-22"),
    ("What is the approved stock repurchase authorization in the board resolutions register?", "executive", "DOC-LEG-23"),
    ("What WCAG level must our products conform to and what is a VPAT?", "employee", "DOC-LEG-24"),
    ("How much notice do customers get before we add a new subprocessor?", "engineering", "DOC-LEG-25"),
]
