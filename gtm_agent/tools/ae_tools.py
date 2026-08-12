"""Sales (Account Executive) tools: qualification, deal economics, mutual action plans.

Sales owns the commercial relationship: qualifying the opportunity, quantifying
the deal on a consumption pricing model, and driving the process to close.
"""

from __future__ import annotations

from typing import Any

from ..data import PRICING, get_account


def qualify_opportunity(account_id: str) -> dict[str, Any]:
    """Score how well-qualified a deal is using the MEDDPICC framework.

    Inspects the account's captured MEDDPICC fields and returns a completeness
    score plus the specific gaps still to close.

    Args:
        account_id: The account identifier or display name.

    Returns:
        dict with "status" and, on success, "qualification": the MEDDPICC score
        (0-8 elements captured), a readable "grade", the filled elements, and the
        list of "gaps" to work next.
    """
    acct = get_account(account_id)
    if acct is None:
        return {"status": "error", "message": f"No account found for '{account_id}'."}

    fields = ["metrics", "economic_buyer", "decision_criteria", "decision_process",
              "paper_process", "identified_pain", "champion", "competition"]
    med = acct.get("meddpicc", {}) or {}

    filled, gaps = {}, []
    for f in fields:
        val = (med.get(f) or "").strip()
        weak = (not val) or val.lower().startswith(("unknown", "not yet", "unquantified"))
        if weak:
            gaps.append(f)
        else:
            filled[f] = val

    score = len(filled)
    grade = ("Strong - advance the deal" if score >= 7 else
             "Developing - fill gaps before forecasting" if score >= 4 else
             "Early - keep in discovery")
    return {
        "status": "success",
        "qualification": {
            "account": acct["name"],
            "stage": acct["stage"],
            "meddpicc_score": f"{score}/8",
            "grade": grade,
            "captured": filled,
            "gaps": gaps or ["None - fully qualified"],
        },
    }


def estimate_deal_value(
    ingest_gb_per_month: float,
    full_users: int,
    core_users: int = 0,
    term_years: int = 1,
) -> dict[str, Any]:
    """Estimate annual contract value on a consumption pricing model.

    The model bills on data ingest (GB/month beyond a free tier) plus billable
    users (full-platform and core). This produces a rough, list-price estimate
    with a volume-commitment discount applied. It is NOT a quote.

    Args:
        ingest_gb_per_month: Expected data ingest per month, in GB.
        full_users: Number of full-platform users.
        core_users: Number of core users (default 0).
        term_years: Contract term in years, used only for the multi-year note (default 1).

    Returns:
        dict with "status" and an "estimate" breaking down ingest cost, user cost,
        the discount tier applied, and the estimated annual and total-term value.
    """
    if ingest_gb_per_month < 0 or full_users < 0 or core_users < 0:
        return {"status": "error", "message": "Usage inputs must be non-negative."}

    billable_gb = max(0.0, ingest_gb_per_month - PRICING["free_ingest_gb_per_month"])
    monthly_ingest = billable_gb * PRICING["ingest_usd_per_gb"]
    monthly_users = (full_users * PRICING["full_user_usd_per_month"]
                     + core_users * PRICING["core_user_usd_per_month"])
    annual_list = (monthly_ingest + monthly_users) * 12

    discount = 0.0
    for tier in PRICING["annual_discount_tiers"]:
        if annual_list >= tier["min_annual_usd"]:
            discount = tier["discount"]
    annual_net = annual_list * (1 - discount)

    return {
        "status": "success",
        "estimate": {
            "assumptions": "Illustrative list rates; consumption-based; not a quote.",
            "billable_ingest_gb_per_month": round(billable_gb, 1),
            "monthly_ingest_usd": round(monthly_ingest, 2),
            "monthly_user_usd": round(monthly_users, 2),
            "annual_list_usd": round(annual_list, 2),
            "discount_applied_pct": round(discount * 100, 1),
            "annual_net_usd": round(annual_net, 2),
            "term_years": term_years,
            "total_term_usd": round(annual_net * term_years, 2),
        },
    }


def build_mutual_action_plan(account_id: str, target_close: str) -> dict[str, Any]:
    """Draft a Mutual Action Plan (MAP) of milestones from now to close.

    Sequences the standard buyer+seller milestones a deal needs, tailored to
    whether a POV is already running, so Sales can align with the champion.

    Args:
        account_id: The account identifier or display name.
        target_close: Human-readable target close (e.g. "end of Q3", "2026-09-30").

    Returns:
        dict with "status" and a "mutual_action_plan": an ordered list of
        {milestone, owner, notes} steps toward the target close date.
    """
    acct = get_account(account_id)
    if acct is None:
        return {"status": "error", "message": f"No account found for '{account_id}'."}

    poc_active = bool(acct.get("poc", {}).get("active"))
    steps = [
        {"milestone": "Confirm success criteria & economic buyer", "owner": "Sales + Champion",
         "notes": "Written, mutually agreed definition of a technical + business win."},
        {"milestone": "Scoped POV / technical validation", "owner": "Pre-Sales + Champion",
         "notes": "In progress." if poc_active else "Kick off; timebox to ~2 weeks."},
        {"milestone": "Value / ROI business case review", "owner": "Sales + Economic Buyer",
         "notes": "Quantify MTTR, tool consolidation, and cost vs incumbent."},
        {"milestone": "Security review & DPA", "owner": "Buyer InfoSec + Vendor",
         "notes": "Start early - usually the long pole for enterprise."},
        {"milestone": "Commercial proposal & pricing", "owner": "Sales",
         "notes": "Consumption estimate + volume commitment options."},
        {"milestone": "Procurement & legal (order form)", "owner": "Buyer Procurement",
         "notes": "Redlines on MSA; confirm signature authority."},
        {"milestone": f"Signature - target {target_close}", "owner": "Economic Buyer",
         "notes": "Warm the exact signing path before the final week."},
    ]
    return {
        "status": "success",
        "mutual_action_plan": {
            "account": acct["name"],
            "target_close": target_close,
            "steps": steps,
        },
    }
