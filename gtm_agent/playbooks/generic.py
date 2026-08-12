"""Generic, public-safe GTM playbooks.

This is the content the agents fall back to when no private playbook pack is
installed (see ``playbooks/__init__.py``). Everything here is industry-standard
sales methodology written clean-room — no company-confidential material — so it is
safe to commit and publish.

To layer in organization-specific plays (your real trial process, RFP tooling,
named sales plays, etc.), drop a ``playbooks/private/content.py`` that defines the
same names; it is gitignored and takes precedence at runtime.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# MEDDPICC — a widely used B2B qualification framework. The dimensions and the
# qualifying questions below are standard industry practice.
# ---------------------------------------------------------------------------
MEDDPICC_GUIDE = """
MEDDPICC — opportunity qualification framework. Score each dimension and name the
single biggest gap.

- Metrics: the quantified business/technical impact the customer uses to measure
  success. Ask: How is this tied to a strategic initiative? How will they measure
  the impact? What proof points do we have from similar customers? Metrics answer
  "why buy anything, why now, why us".
- Economic Buyer: the person with final authority who owns/creates budget. Ask:
  Have we confirmed who it is? Are we engaging at the right (business-outcome)
  level? Who influences them?
- Decision Criteria: the technical + business requirements used to evaluate us vs.
  alternatives (including do-nothing / do-it-internally). Ask: What are they? Who
  set them and can we influence them? Do they map to our differentiators?
- Decision Process: the steps to evaluate, select, and purchase. Ask: What are the
  steps and timelines? Can we accelerate them? When did we last re-confirm them?
- Paper Process: the steps to release funds and execute (POs, T&Cs, security/legal
  review). Map a reverse timeline from the target close date; identify required
  signatures and approval SLAs early.
- Identify Pain: the high-impact business/technical pain and the cost of doing
  nothing. Ask: How big is it? Who is impacted? What's the cost in time/risk/
  revenue? Use open-ended discovery questions.
- Champion: someone with power and credibility who sells on your behalf. Ask: Why
  are they a champion? What's their personal win? Have you tested and prepared
  them? (A coach gives info but won't sell for you — not the same thing.)
- Competition: anyone/anything that can take the budget, including internal builds
  and status quo. Ask: Who are they, their strengths/weaknesses, our
  differentiators, and how do we position against "do nothing"?
""".strip()

# ---------------------------------------------------------------------------
# POV / trial governance — generic best practice for running a technical proof.
# ---------------------------------------------------------------------------
POV_TRIAL_GUIDE = """
Proof-of-Value (POV) / trial governance — run a technical proof that converts.

Entry (before you start):
- The opportunity should be qualified (MEDDPICC in reasonable shape) and in an
  evaluation stage. A POV without a qualified business case wastes both sides' time.
- Write success criteria FIRST: the specific, measurable outcomes the customer will
  accept as "proven". No success criteria, no POV.
- For a trial that runs inside a paying customer's environment, get a written
  evaluation agreement (or email acceptance) before provisioning.

Running it:
- Time-box it (30 days is a healthy default). Don't provision before the customer
  is actually ready to start — the clock is value, not setup.
- Scope to the success criteria only; resist scope creep into a free implementation.
- Track progress against each criterion and keep the economic buyer informed.

Exit:
- Review outcomes against the written criteria and get explicit sign-off on the
  technical win before moving to proposal/close.
- Extensions should be the exception and require a documented business justification.
""".strip()

# ---------------------------------------------------------------------------
# RFP / security questionnaire handling — generic self-service approach.
# ---------------------------------------------------------------------------
RFP_GUIDE = """
RFPs / vendor forms / security questionnaires — handling approach.

- Ownership: the account team owns completing these. Don't wait — start early;
  security/legal reviews rarely have a fast turnaround.
- Self-serve first: answer from your reusable answer library / knowledge base
  (search by keyword: e.g. data privacy, APM, compute, AI). Reuse pre-approved,
  customer-facing answers rather than writing from scratch.
- Lean on certifications and standard artifacts (e.g. SOC 2, ISO 27001) and your
  security/trust documentation to satisfy common requirements.
- Escalate the right things: legal/security/privacy questions or anything requiring
  accepting terms or a signature go to the relevant SME (Customer Trust / Legal) —
  individual reps are not authorized to bind the company to terms.
- Accuracy is the account team's responsibility; have a manager review if needed.
""".strip()

# ---------------------------------------------------------------------------
# "Art-of-the-Possible" demo methodology — generic, product-neutral best practice
# for running an inspiration-focused platform demo (as opposed to build_demo_script,
# which produces the beat-by-beat click path for a single use case).
# ---------------------------------------------------------------------------
DEMO_GUIDE = """
Art-of-the-Possible demo — a framework for running an inspiration demo that wins a
commitment to go deeper. It is NOT a feature-by-feature product tour; the goal is a
customer commitment to a next step (deep-dive, trial, or instrumentation).
Three phases: Preparation, Delivery, Follow-Through.

Guiding principle: your biggest competitor is not another vendor — it is the
customer's other priorities. Align to those priorities instead of competing with
them, or the customer tunes out.

1) PREPARATION ("if you have 8 hours to chop down a tree, spend 6 sharpening the axe").
Outcome: know what each meeting participant values.
- Research: the company (site/"About Us", industry, competitors, parent company if a
  subsidiary), and each attendee (role, and what they value). Build a rough org chart.
  Note the current relationship (prospect vs. customer, contract type, usage level).
- Discovery: ideally a dedicated pre-demo discovery call; otherwise weave discovery
  into the demo. You are preparing to say "based on what you told me, here's how we
  can help" — you can't say that until they've told you what they value. Reflect
  priorities back and get them confirmed. Sample questions: what keeps you up at
  night; what tools do you use today; team goals/KPIs; MTTD/MTTR today; cost of a
  recent incident; on-call load; how you prep for your biggest day.
- Demo prep: don't plan to show everything — pick what matters to them, keep it under
  an hour. Prepare Tell-Show-Tell motions (for each capability: "so what? why does
  this matter to THIS customer?"). Anchor on what they use now. Build a narrative,
  not a click path. Set a PALO: Purpose, Agenda, Logistics, Outcome.

2) DELIVERY ("show just enough to get them hooked — this is not a training session").
Outcome: enough energy/interest to commit to a next step.
- Turn video on. Open with a purpose slide: why this meeting is worth their time.
- Attention span on a video call is ~15 minutes — if you aren't on their use case or
  in conversation, you'll lose them. Pause often for questions; validate relevance.
- Tell-Show-Tell each capability. Lead with the highest-value solution. Tie everything
  to their stated priorities and to stories/other-customer use cases — value, not
  features. Do in-demo discovery; be ready to pivot ("be audible-ready").
- Roles: the account owner (AE) is accountable for the plan (PALO), opens and
  facilitates, manages chat, asks value-focused questions, captures follow-ups, and
  ensures the outcome. The technical seller (SC/SE) drives the platform show, handles
  technical questions, and makes the value of each capability explicit against the
  pain found in discovery. Each backs up the other.
- Practice. There is no substitute for rehearsing the flow.

3) FOLLOW-THROUGH ("don't expect a newly planted tree to grow without watering").
Outcome: make committing and getting value easy for the customer.
- Use an assumptive close to book the next meeting immediately, with a clear goal and
  agenda tied to their priorities. Capture attendees (a screenshot works) and roles.
- Note what resonated and who engaged; follow up on those specifically.
- Echo back what you heard ("you're focused on reducing X, improving Y — here's how
  we help with each"). Send a timely follow-up with key value points and next steps.
- The long game after interest is won is basically project management: track the
  deep-dive/enablement meetings through to realized value.
""".strip()

# ---------------------------------------------------------------------------
# Named sales plays — generic analogues of common observability motions. These are
# safe, vendor-neutral versions; organization-specific plays live in the private
# pack and override these by name.
# ---------------------------------------------------------------------------
SALES_PLAYS = {
    "observability-maturity": {
        "name": "Observability Maturity",
        "when": "Customer has tools but inconsistent adoption, coverage gaps, or "
        "can't tie observability to business outcomes.",
        "play": "Assess the customer's current maturity across dimensions "
        "(instrumentation coverage, MTTR, alerting quality, business-KPI "
        "correlation, cost governance). Show the gap to a target state and a "
        "staged roadmap. Anchor each stage to a measurable outcome (e.g. reduced "
        "MTTR, fewer escalations) so it maps to MEDDPICC Metrics.",
        "outcomes": ["Lower MTTR", "Higher coverage", "Outcome-tied adoption"],
    },
    "alert-quality": {
        "name": "Alert Quality / Noise Reduction",
        "when": "Customer suffers alert fatigue, noisy pages, or missed real "
        "incidents.",
        "play": "Audit current alert conditions for noise (low signal-to-noise, "
        "flapping, non-actionable pages). Prioritize alerting on symptoms that map "
        "to user impact/SLOs, consolidate duplicates, and tune thresholds. Measure "
        "improvement (alerts per incident, actionable-alert ratio, on-call load).",
        "outcomes": ["Fewer non-actionable pages", "Faster detection", "Lower "
        "on-call burden"],
    },
}
