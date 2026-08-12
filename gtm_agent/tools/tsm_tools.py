"""Customer Success (Technical Success Manager) tools: adoption health, onboarding,
expansion, and renewal-risk assessment.

Customer Success owns the post-sale lifecycle: getting the customer to first value,
driving adoption of committed use cases, de-risking the renewal, and surfacing
expansion back to Sales.
"""

from __future__ import annotations

from typing import Any

from ..data import get_account


def assess_adoption_health(account_id: str) -> dict[str, Any]:
    """Score post-sale adoption health from product usage signals.

    Combines active-user ratio, alert coverage, and dashboard/app footprint into a
    simple health signal so Customer Success can spot stalls before they become churn.

    Args:
        account_id: The account identifier or display name.

    Returns:
        dict with "status" and an "adoption_health": a health band (Healthy /
        Watch / At risk), the signals behind it, and the top corrective actions.
    """
    acct = get_account(account_id)
    if acct is None:
        return {"status": "error", "message": f"No account found for '{account_id}'."}

    u = acct.get("usage", {}) or {}
    full_users = u.get("full_users", 0)
    wau = u.get("weekly_active_users", 0)
    alerts = u.get("alerts_configured", 0)
    apps = u.get("apm_apps_reporting", 0)

    active_ratio = (wau / full_users) if full_users else 0.0
    signals, actions, score = [], [], 0

    if active_ratio >= 0.6:
        score += 2; signals.append(f"Active-user ratio healthy ({wau}/{full_users} WAU/seats).")
    elif active_ratio >= 0.3:
        score += 1; signals.append(f"Active-user ratio soft ({wau}/{full_users}).")
        actions.append("Run an enablement session; audit who has seats but isn't logging in.")
    else:
        signals.append(f"Active-user ratio low ({wau}/{full_users}) - seats not being used.")
        actions.append("Reclaim/right-size seats and target a specific team for a value workshop.")

    if alerts >= 20:
        score += 1; signals.append(f"Alerting operationalized ({alerts} alerts).")
    else:
        signals.append(f"Thin alert coverage ({alerts}) - product not yet in the incident workflow.")
        actions.append("Co-build golden-signal alerts for the top services to embed the platform in on-call.")

    if apps >= 5:
        score += 1; signals.append(f"Broad APM footprint ({apps} apps reporting).")
    else:
        actions.append("Expand instrumentation to the next tier of services.")

    band = "Healthy" if score >= 3 else "Watch" if score == 2 else "At risk"
    return {
        "status": "success",
        "adoption_health": {
            "account": acct["name"],
            "health": band,
            "active_user_ratio": round(active_ratio, 2),
            "signals": signals,
            "recommended_actions": actions or ["Maintain cadence; look for expansion."],
        },
    }


def onboarding_checklist(account_id: str) -> dict[str, Any]:
    """Produce a first-value onboarding checklist for a newly closed account.

    Args:
        account_id: The account identifier or display name.

    Returns:
        dict with "status" and an "onboarding": an ordered checklist from access
        setup to first value (data flowing, first dashboard, first alert), with the
        30/60/90 milestone each item supports.
    """
    acct = get_account(account_id)
    if acct is None:
        return {"status": "error", "message": f"No account found for '{account_id}'."}
    return {
        "status": "success",
        "onboarding": {
            "account": acct["name"],
            "checklist": [
                {"item": "Provision accounts, SSO, and role-based access", "milestone": "Day 1-7"},
                {"item": "Get first telemetry flowing (agent or OTel collector)", "milestone": "Day 1-14 (first value)"},
                {"item": "Stand up the first golden-signal dashboard for the top service", "milestone": "Day 14-30"},
                {"item": "Configure first alerts and route to the on-call channel", "milestone": "Day 14-30"},
                {"item": "Enablement session for the primary team", "milestone": "Day 30-60"},
                {"item": "Instrument the committed use cases from the deal", "milestone": "Day 30-90"},
                {"item": "First value-review with the champion + economic buyer", "milestone": "Day 60-90"},
            ],
        },
    }


def identify_expansion(account_id: str) -> dict[str, Any]:
    """Spot expansion opportunities from usage patterns, to hand back to Sales.

    Args:
        account_id: The account identifier or display name.

    Returns:
        dict with "status" and an "expansion": specific, evidence-backed plays
        (more seats, adjacent use cases, higher ingest) Customer Success can qualify
        and pass to Sales, or a note that it's too early.
    """
    acct = get_account(account_id)
    if acct is None:
        return {"status": "error", "message": f"No account found for '{account_id}'."}

    u = acct.get("usage", {}) or {}
    plays = []
    if u.get("weekly_active_users", 0) and u.get("full_users", 0):
        if u["weekly_active_users"] >= 0.8 * u["full_users"]:
            plays.append({"play": "Add seats", "evidence": "Active users near the seat cap - teams are fully engaged."})
    if u.get("apm_apps_reporting", 0) and u["apm_apps_reporting"] < 10:
        plays.append({"play": "Expand instrumentation coverage", "evidence": f"Only {u['apm_apps_reporting']} apps reporting - more services remain uninstrumented."})
    if u.get("alerts_configured", 0) < 10:
        plays.append({"play": "Adjacent use case: incident response / on-call", "evidence": "Low alert count suggests untapped incident-management value."})
    if not plays:
        plays.append({"play": "Nurture", "evidence": "No strong expansion signal yet - focus on adoption depth first."})
    return {"status": "success", "expansion": {"account": acct["name"], "plays": plays}}


def assess_renewal_risk(account_id: str) -> dict[str, Any]:
    """Assess renewal risk ahead of the contract date and recommend a save plan.

    Args:
        account_id: The account identifier or display name.

    Returns:
        dict with "status" and a "renewal": a risk band, the drivers, days to
        renewal (if known), and a recommended play to secure it.
    """
    acct = get_account(account_id)
    if acct is None:
        return {"status": "error", "message": f"No account found for '{account_id}'."}

    u = acct.get("usage", {}) or {}
    renewal_days = u.get("renewal_in_days")
    full_users = u.get("full_users", 0)
    wau = u.get("weekly_active_users", 0)
    active_ratio = (wau / full_users) if full_users else 0.0

    drivers, risk = [], "Low"
    if active_ratio < 0.4:
        risk = "High"; drivers.append(f"Weak adoption (active ratio {round(active_ratio,2)}) - low stickiness at renewal.")
    if u.get("alerts_configured", 0) < 10:
        drivers.append("Not embedded in the incident workflow - easy to rip out.")
        if risk != "High":
            risk = "Medium"
    if renewal_days is not None and renewal_days <= 90 and risk != "Low":
        drivers.append(f"Only {renewal_days} days to renewal - time pressure to fix adoption.")

    plays = {
        "High": "Executive value-review now; targeted enablement blitz; document realized ROI vs the original success criteria.",
        "Medium": "Operationalize alerting with the on-call team and schedule a value-review 60 days out.",
        "Low": "Maintain cadence; pivot the conversation to expansion.",
    }
    return {
        "status": "success",
        "renewal": {
            "account": acct["name"],
            "risk": risk,
            "days_to_renewal": renewal_days if renewal_days is not None else "unknown",
            "drivers": drivers or ["Healthy adoption; no material risk signals."],
            "recommended_play": plays[risk],
        },
    }
