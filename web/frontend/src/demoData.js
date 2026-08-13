// Static demo content for the dashboard views (Sales / Pre-sales / Customer
// Success). It is intentionally illustrative — the figures are for demonstration
// only and are NOT fetched live from the ADK backend. The GTM Coordinator view,
// by contrast, is the real streaming assistant.
//
// IMPORTANT: the companies and numbers below are kept in sync with the sample
// accounts in `gtm_agent/data.py`, so the dashboards and the live agent talk
// about the *same* cast (Acme Retail, Globex FinTech, Nexus Industries, Meridian
// Health, Vertex Logistics, Sterling Financial, Initech SaaS, Umbra Media). If
// you edit an account in data.py, mirror it here. When you wire the dashboards to
// a real source, swap these arrays for live connector data (or the agent's own
// tools).

// ---------------------------------------------------------------- Coordinator
// Right-rail widgets for the Coordinator Workspace.
export const STRATEGIC_OVERVIEW = [
  { label: "Sales Velocity", delta: "↑ 12%", tone: "up", pct: 82, bar: "blue" },
  { label: "Pre-sales Win Rate", delta: "↑ 5%", tone: "up", pct: 71, bar: "green" },
  { label: "CS Handover Risk", delta: "Medium", tone: "warn", pct: 48, bar: "amber" },
];

export const NEXT_STEPS = [
  { title: "Push Vertex Logistics to signature", meta: "Legal cleared", tone: "warn" },
  { title: "Protect Acme Retail POV — 9 days left", meta: "Before security review", tone: "muted" },
  { title: "Re-engage Initech SaaS", meta: "Renewal in ~120 days", tone: "muted" },
];

// A seeded opening exchange so the Coordinator view isn't empty on load. These
// render as normal transcript bubbles; the real assistant takes over on send.
export const COORDINATOR_SEED = [
  {
    role: "assistant",
    agent: "gtm_coordinator",
    text: "I've reviewed the pipeline. Acme Retail's POV has 9 days left and Vertex Logistics is through legal — both need attention before quarter close.",
  },
  { role: "user", text: "Which validation is most at risk of slipping?" },
  {
    role: "assistant",
    agent: "gtm_coordinator",
    text: "Meridian Health is flagged At Risk with 5 days left and an unresolved PII-redaction criterion. Want me to draft a get-well plan with Pre-Sales?",
    // These seeded turns are never sent to the agent, so each action carries a
    // self-contained prompt rather than its label ("Yes, draft it" alone gives the
    // agent nothing for "it" to refer to).
    actions: [
      {
        label: "Yes, draft it",
        prompt:
          "Draft a get-well plan for the Meridian Health POV with Pre-Sales. It's At Risk with 5 days left and an unresolved PII-redaction success criterion. Cover the open criteria, an owner for each, and a day-by-day plan through the POV end date.",
      },
      {
        label: "View details",
        prompt:
          "Give me the full technical validation status for Meridian Health: each POV success criterion and whether it's met or open, days remaining, and what the risk means for the close.",
      },
    ],
  },
];

// ---------------------------------------------------------------------- Sales
export const SALES_KPIS = [
  { label: "Pipeline Coverage", icon: "trend", value: "3.2x", sub: "↑ 0.4x vs Last Qtr", tone: "up" },
  { label: "Quota Attainment", icon: "flag", value: "68%", sub: "$4.2M / $6.1M", bar: 68 },
  { label: "Avg Sales Cycle", icon: "clock", value: "42", unit: "days", sub: "↓ 5 days shorter", tone: "up" },
];

export const SALES_AGENT_INSIGHT =
  '"Acme Retail" shows high-intent signals with 9 days left in its POV. Recommend executive alignment before the security review to protect the Sep 30 close.';

export const SALES_COLUMNS = [
  {
    key: "discovery",
    name: "Discovery",
    count: 2,
    total: "$625K",
    dot: "slate",
    deals: [
      {
        code: "NX",
        name: "Nexus Industries",
        amount: "$145,000",
        owner: "J. Smith",
        due: "Nov 20",
      },
      {
        code: "GX",
        name: "Globex FinTech",
        amount: "$480,000",
        owner: "M. Ross",
        due: "Oct 30",
      },
    ],
  },
  {
    key: "validation",
    name: "Validation",
    count: 2,
    total: "$1.17M",
    dot: "amber",
    deals: [
      {
        code: "AC",
        name: "Acme Retail",
        amount: "$850,000",
        owner: "S. Connor",
        tags: ["High Intent", "Enterprise"],
        status: "Active POV · 9d left",
        statusTone: "ok",
        agent: true,
        highlight: true,
      },
      {
        code: "MH",
        name: "Meridian Health",
        amount: "$320,000",
        owner: "D. Kaur",
        status: "POV · 5d left",
        statusTone: "warn",
      },
    ],
  },
  {
    key: "negotiation",
    name: "Negotiation",
    count: 1,
    total: "$1.2M",
    dot: "blue",
    deals: [
      {
        code: "VX",
        name: "Vertex Logistics",
        amount: "$1,200,000",
        owner: "A. Chen",
        progress: 80,
        status: "Legal Approved",
        statusTone: "ok",
      },
    ],
  },
];

// ------------------------------------------------------------------ Pre-sales
// All pre-sale accounts (Discovery through Negotiation) and their technical
// state. Active POVs show On Track / At Risk; earlier-stage deals show as
// Scoping. Mirrors the `deal.solution_architect` field in data.py.
export const VALIDATIONS = [
  {
    account: "Acme Retail",
    deal: "Deal: #49281 ($850k)",
    phase: "APM / Checkout",
    health: "On Track",
    healthTone: "ok",
    architect: "Albert L.",
    initials: "AL",
    avatar: "blue",
    close: "Sep 30",
  },
  {
    account: "Meridian Health",
    deal: "Deal: #49302 ($320k)",
    phase: "UAT",
    health: "At Risk",
    healthTone: "warn",
    architect: "John D.",
    initials: "JD",
    avatar: "green",
    close: "Oct 24",
  },
  {
    account: "Vertex Logistics",
    deal: "Deal: #49315 ($1.2M)",
    phase: "Migration Plan",
    health: "On Track",
    healthTone: "ok",
    architect: "Albert L.",
    initials: "AL",
    avatar: "blue",
    close: "Sep 15",
  },
  {
    account: "Globex FinTech",
    deal: "Deal: #49330 ($480k)",
    phase: "Scoping",
    health: "Planning",
    healthTone: "muted",
    architect: "John D.",
    initials: "JD",
    avatar: "green",
    close: "Oct 30",
  },
  {
    account: "Nexus Industries",
    deal: "Deal: #49341 ($145k)",
    phase: "Discovery",
    health: "Planning",
    healthTone: "muted",
    architect: "Albert L.",
    initials: "AL",
    avatar: "blue",
    close: "Nov 20",
  },
];

export const SA_UTILIZATION = [
  { name: "Albert L.", active: 3, pct: 85 },
  { name: "John D.", active: 2, pct: 55 },
];

export const CRITERIA_TEMPLATES = [
  {
    title: "OTel Ingest Validation",
    body: "Confirm existing OpenTelemetry data ingests with no re-instrumentation, under load.",
  },
  {
    title: "Security & Compliance Review",
    body: "InfoSec criteria: SSO/RBAC, PII redaction, and SOC2 / HIPAA evidence.",
  },
];

// ------------------------------------------------------------ Customer Success
export const CS_STATS = {
  portfolioHealth: { score: 69, delta: "↑ 2.4%" },
  renewalRisk: {
    arr: "$276K",
    sub: "ARR at risk — renewals within 2 quarters",
    accounts: [
      { name: "Initech SaaS", amount: "$96k" },
      { name: "Sterling Financial", amount: "$180k" },
    ],
  },
  accountGrowth: { count: 1, sub: "Expansion signal — Umbra Media (RUM + mobile)" },
};

// Full portfolio-health view — every account in data.py, worst health first so
// "priority" is meaningful. Prospects (still in a deal) show renewal "—"; only
// live customers carry a renewal date. Mirrors each account's `cs` block.
export const PRIORITY_ACCOUNTS = [
  {
    name: "Nexus Industries",
    tier: "Mid-Market",
    score: 52,
    band: "Poor",
    lastTouch: "2 weeks ago",
    lastKind: "Workshop",
    renewal: "—",
  },
  {
    name: "Initech SaaS",
    tier: "SMB",
    score: 55,
    band: "Poor",
    lastTouch: "30+ days ago",
    lastKind: "Unresponsive",
    lastTone: "warn",
    renewal: "Dec 09, 2026",
  },
  {
    name: "Globex FinTech",
    tier: "Enterprise",
    score: 60,
    band: "Fair",
    lastTouch: "1 week ago",
    lastKind: "Discovery call",
    renewal: "—",
  },
  {
    name: "Meridian Health",
    tier: "Enterprise",
    score: 64,
    band: "Fair",
    lastTouch: "3 days ago",
    lastKind: "POV check-in",
    renewal: "—",
  },
  {
    name: "Sterling Financial",
    tier: "Mid-Market",
    score: 68,
    band: "Fair",
    lastTouch: "5 days ago",
    lastKind: "Onboarding call",
    renewal: "Jun 07, 2027",
  },
  {
    name: "Acme Retail",
    tier: "Enterprise",
    score: 78,
    band: "Good",
    lastTouch: "2 days ago",
    lastKind: "POV review",
    renewal: "—",
  },
  {
    name: "Vertex Logistics",
    tier: "Enterprise",
    score: 84,
    band: "Good",
    lastTouch: "1 day ago",
    lastKind: "Legal review",
    renewal: "—",
  },
  {
    name: "Umbra Media",
    tier: "Enterprise",
    score: 91,
    band: "Good",
    lastTouch: "3 days ago",
    lastKind: "QBR",
    renewal: "Mar 09, 2027",
  },
];

export const CS_PLAYBOOKS = [
  {
    title: "Executive Alignment",
    body: "Triggered for Initech SaaS: low health score (55) and renewal in ~120 days.",
    tags: [{ label: "High Priority", tone: "warn" }, { label: "3 Steps", tone: "muted" }],
  },
  {
    title: "Feature Adoption Push",
    body: "Triggered for Sterling Financial: onboarding stalled at 11/18 active seats.",
    tags: [{ label: "Med Priority", tone: "info" }],
  },
  {
    title: "Expansion Play",
    body: "Triggered for Umbra Media: strong health, RUM + mobile monitoring upsell signal.",
    tags: [{ label: "Growth", tone: "info" }, { label: "Automated", tone: "muted" }],
  },
];

// ------------------------------------------------------------------ Analytics
// Cross-role rollups over the same roster. Open pipeline = the 5 pre-sale deals
// ($625K Discovery + $1.17M Validation + $1.2M Negotiation ≈ $3.0M). Weighted
// forecast applies illustrative stage win-rates (20% / 50% / 85%). Customer ARR
// = the 3 live customers ($240K + $180K + $96K = $516K). Avg health = mean of
// all 8 account scores.
export const ANALYTICS_KPIS = [
  { label: "Open Pipeline", icon: "dollar", value: "$3.0M", sub: "5 open deals", tone: "up" },
  { label: "Weighted Forecast", icon: "trend", value: "$1.73M", sub: "Stage-weighted commit" },
  { label: "Customer ARR", icon: "heart", value: "$516K", sub: "3 live customers", tone: "up" },
  { label: "Avg Portfolio Health", icon: "flag", value: "69", unit: "/100", sub: "8 accounts" },
];

// Pipeline value by sales stage. `pct` is bar width relative to the largest stage.
export const PIPELINE_BY_STAGE = [
  { stage: "Discovery", count: 2, value: "$625K", pct: 52, bar: "blue" },
  { stage: "Technical Validation", count: 2, value: "$1.17M", pct: 98, bar: "amber" },
  { stage: "Negotiation & Close", count: 1, value: "$1.2M", pct: 100, bar: "green" },
];

// Annual recurring revenue by live customer. `pct` relative to the largest.
export const ARR_BY_CUSTOMER = [
  { name: "Umbra Media", value: "$240K", pct: 100, bar: "blue" },
  { name: "Sterling Financial", value: "$180K", pct: 75, bar: "green" },
  { name: "Initech SaaS", value: "$96K", pct: 40, bar: "amber" },
];

// Portfolio health mix across all 8 accounts (Good/Fair/Poor).
export const HEALTH_DISTRIBUTION = [
  { band: "Good", count: 3, seg: "ok" },
  { band: "Fair", count: 3, seg: "warn" },
  { band: "Poor", count: 2, seg: "bad" },
];

// GTM funnel — account count reaching each lifecycle phase.
export const FUNNEL = [
  { stage: "Discovery", count: 8, pct: 100 },
  { stage: "Technical Validation", count: 6, pct: 75 },
  { stage: "Negotiation & Close", count: 4, pct: 50 },
  { stage: "Closed / Live", count: 3, pct: 38 },
];
