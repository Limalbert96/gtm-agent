"""Sample GTM data layer for the lifecycle agent.

This is intentionally an in-memory, dependency-free "CRM + telemetry" stub so the
agent runs out of the box with no external accounts. Every accessor below is a
single, obvious place to swap in a real source:

  * Opportunity / pipeline data   -> Salesforce, HubSpot, Clari, etc.
  * Usage / consumption telemetry  -> your observability backend's API / MCP server
  * Product adoption signals        -> product analytics, Gainsight, Vitally, etc.

Keep the *shape* of the returned dicts stable when you wire in real data and the
tools in `tools/` keep working unchanged.

The product being sold is referenced generically via PRODUCT_NAME so this scaffold
is vendor-neutral. Set GTM_PRODUCT_NAME to brand it for your own platform.
"""

from __future__ import annotations

import os
from typing import Any

# The product these agents sell. Kept generic so the repo is vendor-neutral;
# override with GTM_PRODUCT_NAME (e.g. "Acme Observability").
PRODUCT_NAME = os.environ.get("GTM_PRODUCT_NAME", "our platform")

# ---------------------------------------------------------------------------
# GTM lifecycle stages (the spine the whole agent reasons about)
# ---------------------------------------------------------------------------
# Sales            -> commercial owner: pipeline, qualification, close (a.k.a. AE)
# Pre-Sales        -> technical win: POV/POC, demo, discovery (a.k.a. SC / SE)
# Customer Success -> post-sale adoption, expansion, renewal (a.k.a. TSM / CSM)

LIFECYCLE_STAGES: list[dict[str, Any]] = [
    {"stage": "Prospecting",             "primary_role": "Sales",            "exit_criteria": "Qualified meeting booked with an economic buyer or champion."},
    {"stage": "Discovery",               "primary_role": "Sales",            "exit_criteria": "Business pain, metrics, and decision process documented (MEDDPICC)."},
    {"stage": "Technical Validation",    "primary_role": "Pre-Sales",        "exit_criteria": "Success criteria met in a scoped POV/POC; technical win confirmed."},
    {"stage": "Proposal & Business Case","primary_role": "Sales",            "exit_criteria": "Quantified value / ROI and pricing accepted by the buyer."},
    {"stage": "Negotiation & Close",     "primary_role": "Sales",            "exit_criteria": "Signed order form; procurement and legal cleared."},
    {"stage": "Onboarding",              "primary_role": "Customer Success", "exit_criteria": "First value delivered: data flowing, first dashboards/alerts live."},
    {"stage": "Adoption",                "primary_role": "Customer Success", "exit_criteria": "Committed use cases in production; healthy active-user growth."},
    {"stage": "Expansion & Renewal",     "primary_role": "Customer Success", "exit_criteria": "Renewal secured and/or expansion opportunity created for Sales."},
]

# ---------------------------------------------------------------------------
# Consumption-based pricing model -- simplified for demo estimates.
# Bills on (1) data ingest in GB and (2) billable "full platform" / "core" users.
# These are illustrative list rates, not a quote. Adjust per your rate card.
# ---------------------------------------------------------------------------
PRICING = {
    "ingest_usd_per_gb": 0.35,            # per GB beyond the free tier
    "free_ingest_gb_per_month": 100,      # illustrative
    "full_user_usd_per_month": 349,       # illustrative list, per full-platform user
    "core_user_usd_per_month": 49,        # illustrative list, per core user
    "annual_discount_tiers": [            # illustrative volume commitment discounts
        {"min_annual_usd": 0,       "discount": 0.00},
        {"min_annual_usd": 50_000,  "discount": 0.10},
        {"min_annual_usd": 150_000, "discount": 0.18},
        {"min_annual_usd": 400_000, "discount": 0.25},
    ],
}

# ---------------------------------------------------------------------------
# Sample accounts. A roster spanning every lifecycle stage so each role has
# something to do -- and so the web dashboards (which mirror this same data)
# stay populated. Fictional companies; any resemblance to real customers is
# coincidental.
#
# Optional per-account blocks used by the dashboards (safe to omit; tools don't
# depend on them):
#   * "deal" -> pipeline card fields (amount, owner, target close, progress)
#   * "cs"   -> Customer Success health fields (score, tier, last touch, renewal)
# ---------------------------------------------------------------------------
_ACCOUNTS: dict[str, dict[str, Any]] = {
    "acme-retail": {
        "account_id": "acme-retail",
        "name": "Acme Retail",
        "industry": "E-commerce / Retail",
        "employees": 4200,
        "region": "AMER",
        "stage": "Technical Validation",
        "incumbent_tool": "Datadog",
        "champion": "Priya Nair (Director, SRE)",
        "economic_buyer": "Tom Blake (VP Engineering)",
        "meddpicc": {
            "metrics": "Cut MTTR from 45m to <15m; reduce observability spend 20%.",
            "economic_buyer": "Tom Blake (VP Engineering) - confirmed budget owner.",
            "decision_criteria": "Single pane across APM+logs+RUM; predictable cost; OTel-native.",
            "decision_process": "POV -> security review -> VP + Procurement sign-off. Q3 close.",
            "paper_process": "MSA in place; needs security questionnaire + DPA.",
            "identified_pain": "Tool sprawl (5 tools), noisy alerts, surprise Datadog overages.",
            "champion": "Priya Nair - actively running the eval, wants to standardize on OTel.",
            "competition": "Datadog (incumbent), Grafana Cloud (cost play).",
        },
        "poc": {
            "active": True,
            "use_cases": ["APM for checkout service", "Log-in-context", "Kubernetes monitoring", "OTel ingest from existing collectors"],
            "success_criteria": ["Trace checkout latency end-to-end", "Correlate logs to a specific trace in <2 clicks", "Ingest existing OTel data with no re-instrumentation"],
            "days_remaining": 9,
        },
        "usage": {  # would come from your observability backend's API / MCP in production
            "ingest_gb_per_month": 640,
            "full_users": 22,
            "core_users": 60,
            "weekly_active_users": 41,
            "dashboards": 18,
            "alerts_configured": 34,
            "apm_apps_reporting": 12,
        },
        "deal": {"amount_usd": 850_000, "owner": "S. Connor", "target_close": "Sep 30",
                 "solution_architect": "Albert L.", "health": "On Track", "high_intent": True},
        "cs": {"health_score": 78, "band": "Good", "tier": "Enterprise",
               "last_touch": "2 days ago", "last_touch_kind": "POV review", "renewal_date": "—"},
    },
    "globex-fintech": {
        "account_id": "globex-fintech",
        "name": "Globex FinTech",
        "industry": "Financial Services",
        "employees": 9000,
        "region": "AMER",
        "stage": "Discovery",
        "incumbent_tool": "Splunk + Dynatrace",
        "champion": "Dana Fisher (Platform Eng Lead)",
        "economic_buyer": "Unknown - not yet accessed",
        "meddpicc": {
            "metrics": "Unquantified - needs discovery.",
            "economic_buyer": "Not yet identified.",
            "decision_criteria": "Compliance/audit, data residency, SIEM interplay.",
            "decision_process": "Unknown.",
            "paper_process": "Unknown - likely heavy procurement + infosec.",
            "identified_pain": "Splunk license cost; Dynatrace agent overhead.",
            "champion": "Dana Fisher - interested but not yet a mobilizer.",
            "competition": "Splunk (incumbent logs), Dynatrace (incumbent APM).",
        },
        "poc": {"active": False, "use_cases": [], "success_criteria": [], "days_remaining": 0},
        "usage": {
            "ingest_gb_per_month": 0, "full_users": 0, "core_users": 0,
            "weekly_active_users": 0, "dashboards": 0, "alerts_configured": 0, "apm_apps_reporting": 0,
        },
        "deal": {"amount_usd": 480_000, "owner": "M. Ross", "target_close": "Oct 30",
                 "solution_architect": "John D.", "health": "Early", "high_intent": False},
        "cs": {"health_score": 60, "band": "Fair", "tier": "Enterprise",
               "last_touch": "1 week ago", "last_touch_kind": "Discovery call", "renewal_date": "—"},
    },
    "nexus-industries": {
        "account_id": "nexus-industries",
        "name": "Nexus Industries",
        "industry": "Manufacturing / Industrial IoT",
        "employees": 6500,
        "region": "AMER",
        "stage": "Discovery",
        "incumbent_tool": "Nagios + in-house scripts",
        "champion": "Carlos Mendez (Director, Platform Engineering)",
        "economic_buyer": "Unknown - not yet accessed",
        "meddpicc": {
            "metrics": "Unquantified - reduce plant-floor telemetry blind spots.",
            "economic_buyer": "Not yet identified (likely VP Operations).",
            "decision_criteria": "Edge/on-prem collection, long retention, OT/IT correlation.",
            "decision_process": "Unknown - first technical workshop scheduled.",
            "paper_process": "Unknown.",
            "identified_pain": "No unified view across factories; alert fatigue from Nagios.",
            "champion": "Carlos Mendez - technically sold, needs an internal sponsor.",
            "competition": "Grafana Cloud, Datadog.",
        },
        "poc": {"active": False, "use_cases": [], "success_criteria": [], "days_remaining": 0},
        "usage": {
            "ingest_gb_per_month": 0, "full_users": 0, "core_users": 0,
            "weekly_active_users": 0, "dashboards": 0, "alerts_configured": 0, "apm_apps_reporting": 0,
        },
        "deal": {"amount_usd": 145_000, "owner": "J. Smith", "target_close": "Nov 20",
                 "solution_architect": "Albert L.", "health": "Early", "high_intent": False},
        "cs": {"health_score": 52, "band": "Poor", "tier": "Mid-Market",
               "last_touch": "2 weeks ago", "last_touch_kind": "Workshop", "renewal_date": "—"},
    },
    "meridian-health": {
        "account_id": "meridian-health",
        "name": "Meridian Health",
        "industry": "Healthcare / HealthTech",
        "employees": 5400,
        "region": "AMER",
        "stage": "Technical Validation",
        "incumbent_tool": "Elastic + Prometheus",
        "champion": "Rajesh Kumar (Director, SRE)",
        "economic_buyer": "Emily Zhang (CIO)",
        "meddpicc": {
            "metrics": "Meet 99.95% uptime SLA on patient portal; cut incident triage time 40%.",
            "economic_buyer": "Emily Zhang (CIO) - engaged, budget in FY planning.",
            "decision_criteria": "HIPAA controls, PII redaction, SSO, audit trails.",
            "decision_process": "POV -> InfoSec/compliance review -> CIO sign-off.",
            "paper_process": "BAA required in addition to MSA + DPA.",
            "identified_pain": "Slow triage across Elastic + Prometheus; no distributed tracing.",
            "champion": "Rajesh Kumar - running the POV, wants tracing on the portal.",
            "competition": "Elastic (incumbent logs), Dynatrace.",
        },
        "poc": {
            "active": True,
            "use_cases": ["Distributed tracing for patient portal", "PII redaction in logs", "SSO + RBAC validation"],
            "success_criteria": ["Trace a portal request across 4 services", "Confirm PII scrubbed at ingest", "SAML SSO with role mapping"],
            "days_remaining": 5,
        },
        "usage": {
            "ingest_gb_per_month": 180, "full_users": 8, "core_users": 15,
            "weekly_active_users": 6, "dashboards": 5, "alerts_configured": 7, "apm_apps_reporting": 4,
        },
        "deal": {"amount_usd": 320_000, "owner": "D. Kaur", "target_close": "Oct 24",
                 "solution_architect": "John D.", "health": "At Risk", "high_intent": False},
        "cs": {"health_score": 64, "band": "Fair", "tier": "Enterprise",
               "last_touch": "3 days ago", "last_touch_kind": "POV check-in", "renewal_date": "—"},
    },
    "vertex-logistics": {
        "account_id": "vertex-logistics",
        "name": "Vertex Logistics",
        "industry": "Logistics / Supply Chain",
        "employees": 8000,
        "region": "EMEA",
        "stage": "Negotiation & Close",
        "incumbent_tool": "Datadog",
        "champion": "Sophie Martin (Head of Platform)",
        "economic_buyer": "Marcus Webb (CTO) - budget approved",
        "meddpicc": {
            "metrics": "Consolidate 3 tools; save ~30% vs Datadog renewal.",
            "economic_buyer": "Marcus Webb (CTO) - signed off on budget.",
            "decision_criteria": "Cost predictability, EU data residency, migration support.",
            "decision_process": "Technical win complete; in procurement + legal redlines.",
            "paper_process": "Order form issued; legal cleared, awaiting signature.",
            "identified_pain": "Datadog renewal spike; cardinality overage bills.",
            "champion": "Sophie Martin - driving the internal business case.",
            "competition": "Datadog (incumbent, being displaced).",
        },
        "poc": {"active": False, "use_cases": ["Fleet telemetry pipeline", "Cost-per-service allocation"],
                "success_criteria": ["EU-region ingest verified", "Migration runbook accepted"], "days_remaining": 0},
        "usage": {
            "ingest_gb_per_month": 900, "full_users": 35, "core_users": 90,
            "weekly_active_users": 30, "dashboards": 24, "alerts_configured": 48, "apm_apps_reporting": 18,
        },
        "deal": {"amount_usd": 1_200_000, "owner": "A. Chen", "target_close": "Sep 15",
                 "solution_architect": "Albert L.", "health": "Legal Approved", "progress": 80, "high_intent": False},
        "cs": {"health_score": 84, "band": "Good", "tier": "Enterprise",
               "last_touch": "1 day ago", "last_touch_kind": "Legal review", "renewal_date": "—"},
    },
    "sterling-financial": {
        "account_id": "sterling-financial",
        "name": "Sterling Financial",
        "industry": "Financial Services",
        "employees": 3000,
        "region": "EMEA",
        "stage": "Onboarding",
        "incumbent_tool": f"{PRODUCT_NAME} (new customer, onboarding)",
        "champion": "Aisha Rahman (Observability Lead)",
        "economic_buyer": "Nils Andersson (VP Infrastructure)",
        "meddpicc": {},
        "poc": {"active": False, "use_cases": [], "success_criteria": [], "days_remaining": 0},
        "usage": {
            "ingest_gb_per_month": 210, "full_users": 18, "core_users": 40,
            "weekly_active_users": 11, "dashboards": 9, "alerts_configured": 12, "apm_apps_reporting": 7,
            "contract_arr_usd": 180_000, "renewal_in_days": 300,
        },
        "cs": {"health_score": 68, "band": "Fair", "tier": "Mid-Market",
               "last_touch": "5 days ago", "last_touch_kind": "Onboarding call", "renewal_date": "Jun 07, 2027"},
    },
    "initech-saas": {
        "account_id": "initech-saas",
        "name": "Initech SaaS",
        "industry": "B2B SaaS",
        "employees": 1200,
        "region": "AMER",
        "stage": "Adoption",
        "incumbent_tool": f"{PRODUCT_NAME} (existing customer since 2024)",
        "champion": "Sam Ortiz (Head of Platform)",
        "economic_buyer": "Lee Vance (CTO)",
        "meddpicc": {},
        "poc": {"active": False, "use_cases": [], "success_criteria": [], "days_remaining": 0},
        "usage": {
            "ingest_gb_per_month": 310,
            "full_users": 14,
            "core_users": 30,
            "weekly_active_users": 5,          # 5/14 seats active -> soft adoption, renewal risk
            "dashboards": 6,
            "alerts_configured": 8,            # low -> not yet operationalized
            "apm_apps_reporting": 5,
            "contract_arr_usd": 96_000,
            "renewal_in_days": 120,
        },
        "cs": {"health_score": 55, "band": "Poor", "tier": "SMB",
               "last_touch": "30+ days ago", "last_touch_kind": "Unresponsive", "last_touch_tone": "warn",
               "renewal_date": "Dec 09, 2026"},
    },
    "umbra-media": {
        "account_id": "umbra-media",
        "name": "Umbra Media",
        "industry": "Media / Streaming",
        "employees": 2200,
        "region": "AMER",
        "stage": "Expansion & Renewal",
        "incumbent_tool": f"{PRODUCT_NAME} (existing customer since 2023)",
        "champion": "Grace Liu (SRE Manager)",
        "economic_buyer": "Daniel Cross (CTO)",
        "meddpicc": {},
        "poc": {"active": False, "use_cases": [], "success_criteria": [], "days_remaining": 0},
        "usage": {
            "ingest_gb_per_month": 520, "full_users": 30, "core_users": 75,
            "weekly_active_users": 28, "dashboards": 22, "alerts_configured": 40, "apm_apps_reporting": 15,
            "contract_arr_usd": 240_000, "renewal_in_days": 210,
        },
        "cs": {"health_score": 91, "band": "Good", "tier": "Enterprise",
               "last_touch": "3 days ago", "last_touch_kind": "QBR", "renewal_date": "Mar 09, 2027",
               "expansion_signal": "Upsell: RUM + mobile monitoring for new streaming app."},
    },
}


# ---------------------------------------------------------------------------
# Accessors -- the seam between "sample data" and "real systems".
# Swap the bodies of these for real API/MCP calls; keep the return shapes.
# ---------------------------------------------------------------------------
def list_accounts() -> list[dict[str, Any]]:
    """Return a lightweight index of all known accounts."""
    return [
        {"account_id": a["account_id"], "name": a["name"], "stage": a["stage"], "industry": a["industry"]}
        for a in _ACCOUNTS.values()
    ]


def get_account(account_id: str) -> dict[str, Any] | None:
    """Look up a full account record by id (case-insensitive, tolerant of names)."""
    if not account_id:
        return None
    key = account_id.strip().lower()
    if key in _ACCOUNTS:
        return _ACCOUNTS[key]
    # tolerate being handed a display name like "Acme Retail"
    for acct in _ACCOUNTS.values():
        if acct["name"].lower() == key:
            return acct
    return None
