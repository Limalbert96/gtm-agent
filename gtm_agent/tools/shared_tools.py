"""Tools shared across roles: account lookup and lifecycle orientation.

ADK turns each plain function below into a tool the LLM can call. The docstring
and type hints ARE the tool's schema, so they're written for the model to read.
Every tool returns a dict with a "status" key so the model can branch on failure.
"""

from __future__ import annotations

from typing import Any

from .. import playbooks
from ..data import LIFECYCLE_STAGES, get_account, list_accounts


def list_all_accounts() -> dict[str, Any]:
    """List every account in the book of business with its current lifecycle stage.

    Use this when the user asks "what accounts do I have" or when you need to
    resolve a vague reference to a specific account_id before calling other tools.

    Returns:
        dict with "status" and "accounts": a list of {account_id, name, stage, industry}.
    """
    return {"status": "success", "accounts": list_accounts()}


def get_account_overview(account_id: str) -> dict[str, Any]:
    """Get the 360-degree overview of a single account.

    Args:
        account_id: The account identifier (e.g. "acme-retail") or its display
            name (e.g. "Acme Retail").

    Returns:
        dict with "status" and, on success, an "overview" containing the account's
        stage, industry, incumbent tool, key contacts, and headline usage figures.
    """
    acct = get_account(account_id)
    if acct is None:
        return {
            "status": "error",
            "message": f"No account found for '{account_id}'. Call list_all_accounts to see valid ids.",
        }
    usage = acct.get("usage", {})
    return {
        "status": "success",
        "overview": {
            "account_id": acct["account_id"],
            "name": acct["name"],
            "industry": acct["industry"],
            "employees": acct["employees"],
            "region": acct["region"],
            "stage": acct["stage"],
            "incumbent_tool": acct["incumbent_tool"],
            "champion": acct.get("champion"),
            "economic_buyer": acct.get("economic_buyer"),
            "ingest_gb_per_month": usage.get("ingest_gb_per_month", 0),
            "full_users": usage.get("full_users", 0),
            "weekly_active_users": usage.get("weekly_active_users", 0),
        },
    }


def get_lifecycle_map(current_stage: str = "") -> dict[str, Any]:
    """Return the GTM lifecycle stages, who owns each, and exit criteria.

    Args:
        current_stage: Optional. If provided, the response also flags which stage
            is current and what the immediate next stage and its owner are.

    Returns:
        dict with "status", the full "lifecycle", and (if current_stage given) a
        "position" object naming the current owner, next stage, and next owner.
    """
    result: dict[str, Any] = {"status": "success", "lifecycle": LIFECYCLE_STAGES}
    if current_stage:
        names = [s["stage"].lower() for s in LIFECYCLE_STAGES]
        cur = current_stage.strip().lower()
        if cur in names:
            i = names.index(cur)
            nxt = LIFECYCLE_STAGES[i + 1] if i + 1 < len(LIFECYCLE_STAGES) else None
            result["position"] = {
                "current_stage": LIFECYCLE_STAGES[i]["stage"],
                "current_owner": LIFECYCLE_STAGES[i]["primary_role"],
                "exit_criteria": LIFECYCLE_STAGES[i]["exit_criteria"],
                "next_stage": nxt["stage"] if nxt else "None - final stage",
                "next_owner": nxt["primary_role"] if nxt else "None",
            }
        else:
            result["note"] = f"'{current_stage}' is not a recognized stage."
    return result


def get_playbook(topic: str) -> dict[str, Any]:
    """Return the detailed guide for a GTM topic (qualification, POV/trials, RFPs).

    Use this when the user asks how to run one of these motions, or when you need
    the methodology to structure an answer. Content resolves to your organization's
    private playbook if one is installed, otherwise a generic best-practice guide.

    Args:
        topic: One of "meddpicc" (opportunity qualification), "pov" or "trial"
            (proof-of-value / trial governance), "rfp" (RFP / security questionnaire
            handling), or "demo" / "aotp" (art-of-the-possible demo methodology:
            preparation, delivery, follow-through).

    Returns:
        dict with "status" and, on success, "topic", "guide" (the full text), and
        "source" ("private" or "generic").
    """
    key = (topic or "").strip().lower()
    guide = playbooks.GUIDES.get(key)
    if guide is None:
        return {
            "status": "error",
            "message": f"No playbook for '{topic}'. Valid topics: {sorted(set(playbooks.GUIDES))}.",
        }
    return {"status": "success", "topic": key, "guide": guide, "source": playbooks.SOURCE}


def list_sales_plays() -> dict[str, Any]:
    """List the available named sales plays with when-to-use and expected outcomes.

    Use this when the user asks "what plays do we have" or wants a recommended
    motion for a customer situation. Plays resolve to your organization's private
    plays if installed, otherwise generic observability plays.

    Returns:
        dict with "status", "source" ("private" or "generic"), and "plays": a list
        of {id, name, when, play, outcomes[, doc]}.
    """
    plays = []
    for play_id, p in playbooks.SALES_PLAYS.items():
        entry = {"id": play_id, **p}
        plays.append(entry)
    return {"status": "success", "source": playbooks.SOURCE, "plays": plays}
