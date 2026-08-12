"""GTM lifecycle agent, built on Google ADK and powered by Claude.

Architecture: a Coordinator (root) agent with three role sub-agents. ADK's
LLM-driven delegation lets the coordinator transfer control to whichever role owns
the current lifecycle stage.

    Coordinator (root_agent)
      |- Sales             -- qualify, price, mutual action plan          (a.k.a. AE)
      |- Pre-Sales         -- POV, demo, discovery, competitive, ingest   (a.k.a. SC/SE)
      |- Customer Success  -- onboarding, adoption, expansion, renewal    (a.k.a. TSM/CSM)

Claude is wired in through ADK's LiteLLM wrapper, so no Gemini/Vertex is required -
just an ANTHROPIC_API_KEY (see auth.py). `adk web` / `adk run` discover `root_agent`.
"""

from __future__ import annotations

import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from . import prompts
from .auth import base_url, resolve_api_token
from .config import load_env
from .data import PRODUCT_NAME
from .tools import ae_tools, sc_tools, shared_tools, tsm_tools

# Load the repo-root .env before reading any config below. ADK's own launchers
# load it too, but non-ADK entry points (the FastAPI web server, run_cli, tests)
# would otherwise miss it -- so the model + gateway settings must be applied
# here, at import time, no matter who imports the agent.
load_env()

# Best-effort: send ADK's OpenTelemetry traces to an OTLP backend if one is
# configured via env (see observability.py). No-op otherwise.
try:  # pragma: no cover - optional dependency / config
    from .observability import configure_tracing

    configure_tracing()
except Exception:  # never let telemetry setup break the agent
    pass

# ---------------------------------------------------------------------------
# Model selection. GTM_MODEL picks the backend via a LiteLLM model id
# "provider/name":
#   anthropic/claude-...        -> Claude (public API by default; see auth.py)
#   gemini/gemini-2.5-pro       -> Google Gemini (needs GEMINI_API_KEY)
#   ollama_chat/qwen3           -> local Ollama
#   openai/<model>              -> LM Studio / vLLM (OpenAI-compatible)
# ---------------------------------------------------------------------------
_MODEL_ID = os.environ.get("GTM_MODEL", "anthropic/claude-sonnet-4-20250514")
_PROVIDER = _MODEL_ID.split("/", 1)[0].lower()

# Cap output tokens. Without a cap, some providers assume a very large max_tokens,
# and Anthropic then *requires* streaming for requests that could exceed 10 minutes
# (the "Streaming is required..." error). GTM answers are short, so a modest cap
# keeps non-streaming requests valid. Override with GTM_MAX_TOKENS.
_MAX_TOKENS = int(os.environ.get("GTM_MAX_TOKENS", "8192"))


def _model() -> LiteLlm:
    """Fresh LiteLlm instance per agent (ADK expects a model object per agent).

    Anthropic: uses the token from auth.py (ANTHROPIC_API_KEY by default). Only if
    a gateway base URL is configured do we also send the Bearer header the gateway
    expects. Non-anthropic providers point at a local/OpenAI-compatible server.
    """
    kwargs: dict = {"model": _MODEL_ID, "max_tokens": _MAX_TOKENS}

    if _PROVIDER == "anthropic":
        token = resolve_api_token()
        gateway = base_url()
        if token:
            kwargs["api_key"] = token
        if gateway:
            kwargs["api_base"] = gateway
            # A gateway (if any) authenticates on a Bearer header. The public
            # Anthropic API needs no api_base and no extra header.
            if token:
                kwargs["extra_headers"] = {"Authorization": f"Bearer {token}"}
    elif _PROVIDER in ("gemini", "vertex_ai"):
        # Google Gemini via LiteLLM. LiteLLM reads GEMINI_API_KEY from the env
        # on its own; we pass it explicitly (also accepting GOOGLE_API_KEY) so
        # the key resolves the same way regardless of which var you set.
        gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get(
            "GOOGLE_API_KEY"
        )
        if gemini_key:
            kwargs["api_key"] = gemini_key
    else:
        # Local / OpenAI-compatible backend (Ollama, LM Studio, vLLM). Point at
        # the server; pass a (often dummy) key only if it wants one.
        local_base = os.environ.get("GTM_LOCAL_BASE_URL")
        if local_base:
            kwargs["api_base"] = local_base
        local_key = os.environ.get("GTM_LOCAL_API_KEY")
        if local_key:
            kwargs["api_key"] = local_key

    return LiteLlm(**kwargs)


_SHARED = [
    shared_tools.list_all_accounts,
    shared_tools.get_account_overview,
    shared_tools.get_lifecycle_map,
    shared_tools.get_playbook,
    shared_tools.list_sales_plays,
]

sales_agent = Agent(
    name="sales_agent",
    model=_model(),
    description=(
        "Sales (Account Executive). Owns the commercial deal: MEDDPICC "
        "qualification, consumption-based deal economics, mutual action plans, and "
        "driving to close. Owns Prospecting, Discovery, Proposal, and Negotiation & Close."
    ),
    instruction=prompts.SALES_INSTRUCTION,
    tools=[
        ae_tools.qualify_opportunity,
        ae_tools.estimate_deal_value,
        ae_tools.build_mutual_action_plan,
        *_SHARED,
    ],
)

presales_agent = Agent(
    name="presales_agent",
    model=_model(),
    description=(
        "Pre-Sales (Solutions Consultant / Sales Engineer). Owns the technical win: "
        "POV/POC scoping, demo design, technical discovery, competitive positioning, "
        "and ingest sizing. Owns the Technical Validation stage."
    ),
    instruction=prompts.PRESALES_INSTRUCTION,
    tools=[
        sc_tools.scope_pov,
        sc_tools.build_demo_script,
        sc_tools.technical_discovery_questions,
        sc_tools.competitive_battlecard,
        sc_tools.estimate_ingest,
        *_SHARED,
    ],
)

customer_success_agent = Agent(
    name="customer_success_agent",
    model=_model(),
    description=(
        "Customer Success (Technical Success Manager). Owns the post-sale lifecycle: "
        "onboarding to first value, adoption health, expansion, and renewal risk. "
        "Owns Onboarding, Adoption, and Expansion & Renewal."
    ),
    instruction=prompts.CUSTOMER_SUCCESS_INSTRUCTION,
    tools=[
        tsm_tools.onboarding_checklist,
        tsm_tools.assess_adoption_health,
        tsm_tools.identify_expansion,
        tsm_tools.assess_renewal_risk,
        *_SHARED,
    ],
)

root_agent = Agent(
    name="gtm_coordinator",
    model=_model(),
    description=(
        f"GTM lifecycle coordinator for {PRODUCT_NAME}; routes across Sales, "
        "Pre-Sales, and Customer Success specialists."
    ),
    instruction=prompts.COORDINATOR_INSTRUCTION,
    tools=_SHARED,
    sub_agents=[sales_agent, presales_agent, customer_success_agent],
)
