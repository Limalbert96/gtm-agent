"""Offline sanity checks that need NO API key and NO network.

Exercises every tool function directly (the ADK-independent business logic) and,
if google-adk happens to be installed, also builds the agent tree to catch wiring
errors. Run:  python validate_offline.py
"""

from __future__ import annotations

import sys

from gtm_agent.data import list_accounts
from gtm_agent.tools import ae_tools, sc_tools, shared_tools, tsm_tools

FAILS = []


def check(label: str, result: dict, *, must_have: str | None = None) -> None:
    ok = isinstance(result, dict) and result.get("status") == "success"
    if ok and must_have is not None:
        ok = must_have in result
    print(f"  [{'ok' if ok else 'FAIL'}] {label}")
    if not ok:
        FAILS.append((label, result))


def main() -> int:
    print(f"Accounts in sample book: {[a['account_id'] for a in list_accounts()]}\n")

    print("shared_tools")
    check("list_all_accounts", shared_tools.list_all_accounts(), must_have="accounts")
    check("get_account_overview(acme-retail)", shared_tools.get_account_overview("acme-retail"), must_have="overview")
    check("get_account_overview(Acme Retail by name)", shared_tools.get_account_overview("Acme Retail"), must_have="overview")
    check("get_lifecycle_map(Technical Validation)", shared_tools.get_lifecycle_map("Technical Validation"), must_have="position")
    bad = shared_tools.get_account_overview("nope")
    print(f"  [{'ok' if bad.get('status') == 'error' else 'FAIL'}] get_account_overview(unknown) -> error")
    if bad.get("status") != "error":
        FAILS.append(("unknown-account", bad))

    print("\nae_tools (Sales)")
    check("qualify_opportunity(acme-retail)", ae_tools.qualify_opportunity("acme-retail"), must_have="qualification")
    check("estimate_deal_value", ae_tools.estimate_deal_value(640, 22, 60, 1), must_have="estimate")
    check("build_mutual_action_plan", ae_tools.build_mutual_action_plan("acme-retail", "end of Q3"), must_have="mutual_action_plan")

    print("\nsc_tools (Pre-Sales)")
    check("scope_pov(acme-retail)", sc_tools.scope_pov("acme-retail"), must_have="pov_plan")
    check("build_demo_script(apm)", sc_tools.build_demo_script("apm"), must_have="demo_script")
    check("technical_discovery_questions(Datadog)", sc_tools.technical_discovery_questions("Datadog"), must_have="questions")
    check("competitive_battlecard(datadog)", sc_tools.competitive_battlecard("datadog"), must_have="battlecard")
    check("estimate_ingest", sc_tools.estimate_ingest(apm_apps=12, hosts=40, k8s_nodes=20, log_sources=12, monthly_pageviews_millions=5), must_have="ingest_estimate")

    print("\ntsm_tools (Customer Success)")
    check("assess_adoption_health(initech-saas)", tsm_tools.assess_adoption_health("initech-saas"), must_have="adoption_health")
    check("onboarding_checklist(initech-saas)", tsm_tools.onboarding_checklist("initech-saas"), must_have="onboarding")
    check("identify_expansion(initech-saas)", tsm_tools.identify_expansion("initech-saas"), must_have="expansion")
    check("assess_renewal_risk(initech-saas)", tsm_tools.assess_renewal_risk("initech-saas"), must_have="renewal")

    # Show one real computation so the numbers are visibly sane.
    est = ae_tools.estimate_deal_value(640, 22, 60, 1)["estimate"]
    print(f"\nSample deal economics (Acme): annual_net_usd=${est['annual_net_usd']:,} "
          f"(discount {est['discount_applied_pct']}%)")
    health = tsm_tools.assess_adoption_health("initech-saas")["adoption_health"]
    print(f"Sample adoption (Initech): health={health['health']} active_ratio={health['active_user_ratio']}")

    print("\nagent tree (requires google-adk installed)")
    import importlib.util
    if importlib.util.find_spec("google.adk") is None:
        print("  [skip] google-adk not installed here; tool logic above is validated. "
              "Install requirements.txt to build the agent tree.")
    else:
        try:
            from gtm_agent import root_agent
            subs = [s.name for s in root_agent.sub_agents]
            print(f"  [ok] root_agent='{root_agent.name}' sub_agents={subs}")
            expected = ["customer_success_agent", "presales_agent", "sales_agent"]
            if sorted(subs) != expected:
                FAILS.append(("sub_agents", subs))
        except Exception as e:  # pragma: no cover - surfaces wiring errors
            print(f"  [FAIL] building agent tree raised: {e!r}")
            FAILS.append(("agent-tree", repr(e)))

    print()
    if FAILS:
        print(f"RESULT: {len(FAILS)} failure(s).")
        for label, detail in FAILS:
            print(f"  - {label}: {detail}")
        return 1
    print("RESULT: all tool checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
