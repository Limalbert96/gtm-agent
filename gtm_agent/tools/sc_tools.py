"""Pre-Sales (Solutions Consultant / Sales Engineer) tools: POV scoping, demo
design, technical discovery, competitive positioning, and ingest sizing.

Pre-Sales owns the technical win: proving the platform solves the customer's
problem in a scoped proof-of-value, and positioning against the incumbent.
"""

from __future__ import annotations

from typing import Any

from ..data import PRICING, PRODUCT_NAME, get_account

# Rough per-source monthly ingest heuristics (GB) for quick sizing conversations.
_INGEST_HEURISTICS_GB = {
    "apm_per_app": 8,
    "logs_per_app": 25,
    "infra_per_host": 2,
    "kubernetes_per_node": 4,
    "rum_per_million_pageviews": 12,
    "otel_traces_per_app": 10,
}


def scope_pov(account_id: str) -> dict[str, Any]:
    """Assemble a scoped Proof-of-Value plan from an account's use cases.

    Turns the account's captured use cases and success criteria into a timeboxed
    POV with an entry/exit checklist. Falls back to a sensible default plan if the
    account has no POV data yet.

    Args:
        account_id: The account identifier or display name.

    Returns:
        dict with "status" and a "pov_plan": timebox, use cases, measurable exit
        criteria, and the technical prerequisites to start.
    """
    acct = get_account(account_id)
    if acct is None:
        return {"status": "error", "message": f"No account found for '{account_id}'."}

    poc = acct.get("poc", {}) or {}
    use_cases = poc.get("use_cases") or ["APM on one critical service", "Logs-in-context", "One golden-signal dashboard + alert"]
    criteria = poc.get("success_criteria") or ["End-to-end trace on the critical path", "Log correlated to a trace in <2 clicks", "Alert fires on an injected fault"]
    return {
        "status": "success",
        "pov_plan": {
            "account": acct["name"],
            "incumbent_tool": acct["incumbent_tool"],
            "timebox": "10 business days" if not poc.get("days_remaining") else f"{poc['days_remaining']} days remaining",
            "use_cases": use_cases,
            "exit_criteria": criteria,
            "prerequisites": [
                "Access to a non-prod environment for the target service",
                "Ability to deploy the platform agent or point existing OTel collectors at the platform",
                "A named champion to co-own daily check-ins",
            ],
        },
    }


def build_demo_script(use_case: str) -> dict[str, Any]:
    """Produce a beat-by-beat demo script for a specific observability use case.

    Args:
        use_case: The scenario to demo. Recognized examples: "apm", "logs",
            "kubernetes", "otel", "rum". Anything else yields a generic outline.

    Returns:
        dict with "status" and a "demo_script": an ordered list of beats, each with
        a talk-track and the platform capability it showcases.
    """
    uc = use_case.strip().lower()
    scripts = {
        "apm": [
            ("Open the failing checkout service in APM", "Show golden signals: throughput, latency, error rate."),
            ("Drill into a slow transaction", "Distributed trace waterfall - pinpoint the slow downstream call."),
            ("Jump from the span to its logs", "Logs-in-context: no tool-switching to root-cause."),
            ("Show the deployment marker", "Change tracking correlates the regression to a specific deploy."),
        ],
        "logs": [
            ("Search a spike of errors", "Fast log query + patterns to auto-cluster noise."),
            ("Pivot from a log line to its trace", "One click from symptom to the exact request."),
            ("Create an alert from the query", "Operationalize the finding in seconds."),
        ],
        "kubernetes": [
            ("Open the cluster explorer", "Node/pod health in one view."),
            ("Find a pod in CrashLoopBackOff", "Correlate events, logs, and container metrics."),
            ("Trace a request across services in the cluster", "APM + infra + logs unified."),
        ],
        "otel": [
            ("Point an existing OTel collector at the platform", "OTel-native ingest, no re-instrumentation."),
            ("Show the same traces already flowing", "Avoid lock-in; keep their instrumentation."),
            ("Blend OTel data with the platform's own agents", "Single backend for mixed fleets."),
        ],
        "rum": [
            ("Open browser/real-user monitoring for the storefront", "Core Web Vitals by page and geo."),
            ("Correlate a slow page to a backend trace", "Front-end to back-end in one trace."),
            ("Segment by release", "Prove a release improved real-user latency."),
        ],
    }
    beats = scripts.get(uc)
    if not beats:
        beats = [
            ("Frame the customer's pain in their words", "Anchor the demo to a documented success criterion."),
            ("Show the shortest path from symptom to root cause", "Emphasize the unified, single-backend story."),
            ("End on operationalizing it (alert/dashboard)", "Turn the demo into something they keep."),
        ]
    return {
        "status": "success",
        "demo_script": {
            "use_case": use_case,
            "beats": [{"do": d, "say": s} for d, s in beats],
        },
    }


def technical_discovery_questions(incumbent_tool: str = "") -> dict[str, Any]:
    """Generate technical discovery questions, sharpened against the incumbent.

    Args:
        incumbent_tool: Optional. The tool to displace (e.g. "Datadog", "Splunk",
            "Dynatrace", "Grafana"). Tailors a few incumbent-specific probes.

    Returns:
        dict with "status" and "questions": a list grouped by theme (architecture,
        pain, success) plus incumbent-specific probes when a tool is named.
    """
    base = [
        "What does your telemetry pipeline look like today (agents, OTel collectors, forwarders)?",
        "Which service, if it went down, would hurt the most - and how do you find out today?",
        "How long does a typical incident take from alert to root cause right now?",
        "How much of your instrumentation is OpenTelemetry vs vendor agents?",
        "Where does tool-switching slow your engineers down during an incident?",
    ]
    incumbent_probes = {
        "datadog": ["How predictable is your Datadog bill month to month?", "Which custom metrics / indexed-log costs surprise you?"],
        "splunk": ["What does your Splunk ingest license cost, and how close to the cap are you?", "How much SPL expertise is required to get value?"],
        "dynatrace": ["How heavy is the OneAgent footprint on your hosts?", "How flexible is DQL/host-unit licensing for your fleet?"],
        "grafana": ["Who maintains your LGTM stack, and what does that operational load cost?", "How do you correlate across Loki/Tempo/Mimir today?"],
    }
    result = {"architecture_and_pain": base}
    key = incumbent_tool.strip().lower()
    if key in incumbent_probes:
        result[f"vs_{key}"] = incumbent_probes[key]
    return {"status": "success", "questions": result}


def competitive_battlecard(competitor: str) -> dict[str, Any]:
    """Return a concise competitive battlecard for positioning the platform.

    Args:
        competitor: One of "datadog", "dynatrace", "splunk", "grafana".

    Returns:
        dict with "status" and a "battlecard": where the platform wins, likely
        objections, and traps to avoid. Positioning guidance, not disparagement.
    """
    cards = {
        "datadog": {
            "platform_wins": ["Predictable pricing (ingest + users) vs per-host + à-la-carte SKUs", "All-in-one platform included, not sold module-by-module", "Strong OTel-native ingest story"],
            "likely_objections": ["'Datadog has more integrations'", "'We already have dashboards built'"],
            "avoid": ["Feature-by-feature bake-offs - anchor on total cost and time-to-root-cause instead."],
        },
        "dynatrace": {
            "platform_wins": ["Simpler, more transparent consumption pricing vs host-unit + DDU model", "Faster time-to-value without heavy agent config", "Open, OTel-first vs proprietary OneAgent"],
            "likely_objections": ["'Davis AI is more automated'", "'Automatic dependency mapping'"],
            "avoid": ["Getting pulled into an AIOps-only conversation - keep it on unified data + cost."],
        },
        "splunk": {
            "platform_wins": ["Ingest-based pricing without index-volume license anxiety", "Observability-native UX vs SPL learning curve", "APM+RUM+infra included, not just logs/SIEM"],
            "likely_objections": ["'Splunk is our SIEM/system of record'", "'Our team knows SPL'"],
            "avoid": ["Trying to displace the SIEM - position as observability alongside it."],
        },
        "grafana": {
            "platform_wins": ["Managed, single backend vs self-run LGTM operational load", "Unified correlation out of the box", "One vendor to support vs assembling OSS pieces"],
            "likely_objections": ["'Grafana is cheaper / open source'", "'We like dashboard flexibility'"],
            "avoid": ["Dismissing OSS - quantify the hidden cost of running LGTM yourselves."],
        },
    }
    key = competitor.strip().lower()
    card = cards.get(key)
    if not card:
        return {"status": "error", "message": f"No battlecard for '{competitor}'. Try: {', '.join(cards)}."}
    return {"status": "success", "battlecard": {"competitor": competitor, "positioning_for": PRODUCT_NAME, **card}}


def estimate_ingest(apm_apps: int = 0, hosts: int = 0, k8s_nodes: int = 0,
                    log_sources: int = 0, monthly_pageviews_millions: float = 0.0) -> dict[str, Any]:
    """Rough-size expected monthly data ingest (GB) from an environment description.

    Uses simple per-source heuristics to give Sales a starting ingest number for
    a consumption estimate. Deliberately approximate - a sizing conversation, not a bill.

    Args:
        apm_apps: Number of applications to instrument with APM.
        hosts: Number of infrastructure hosts.
        k8s_nodes: Number of Kubernetes nodes.
        log_sources: Number of distinct log-producing services.
        monthly_pageviews_millions: Monthly browser pageviews, in millions, for RUM.

    Returns:
        dict with "status" and an "ingest_estimate": per-category GB and the total
        estimated GB/month, ready to feed into estimate_deal_value.
    """
    h = _INGEST_HEURISTICS_GB
    breakdown = {
        "apm_gb": apm_apps * h["apm_per_app"],
        "logs_gb": log_sources * h["logs_per_app"],
        "infra_gb": hosts * h["infra_per_host"],
        "kubernetes_gb": k8s_nodes * h["kubernetes_per_node"],
        "rum_gb": monthly_pageviews_millions * h["rum_per_million_pageviews"],
    }
    total = round(sum(breakdown.values()), 1)
    return {
        "status": "success",
        "ingest_estimate": {
            "breakdown_gb_per_month": {k: round(v, 1) for k, v in breakdown.items()},
            "total_gb_per_month": total,
            "note": f"~{total} GB/mo; {PRICING['free_ingest_gb_per_month']} GB free tier applies before billing.",
        },
    }
