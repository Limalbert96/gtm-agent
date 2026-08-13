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
from google.adk.models.google_llm import Gemini
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

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

# Best-effort: send ADK's OpenTelemetry traces/metrics/logs to an OTLP backend if
# one is configured via env (see observability.py). No-op otherwise.
try:  # pragma: no cover - optional dependency / config
    from .observability import configure_telemetry

    configure_telemetry()
except Exception:  # never let telemetry setup break the agent
    pass

# ---------------------------------------------------------------------------
# Model selection. GTM_MODEL picks the backend via a "provider/name" model id:
#   anthropic/claude-...        -> Claude (public API by default; see auth.py)
#   gemini/gemini-2.5-flash     -> Google Gemini (needs GEMINI_API_KEY)
#   ollama_chat/qwen3           -> local Ollama
#   openai/<model>              -> LM Studio / vLLM (OpenAI-compatible)
#
# Gemini uses ADK's NATIVE integration; every other provider goes through ADK's
# LiteLLM wrapper. Gemini via LiteLLM works but gives up streaming/tool-calling
# fidelity, and ADK warns about it ("[GEMINI_VIA_LITELLM]").
# ---------------------------------------------------------------------------
_MODEL_ID = os.environ.get("GTM_MODEL", "anthropic/claude-sonnet-4-20250514")
_PROVIDER = _MODEL_ID.split("/", 1)[0].lower()

# Bare model name for the native client, e.g. "gemini-2.5-flash". Empty for every
# other provider -- which is exactly what selects the LiteLLM path in _model().
_GEMINI_MODEL_NAME = _MODEL_ID.partition("/")[2] if _PROVIDER == "gemini" else ""

# Cap output tokens. Without a cap, some providers assume a very large max_tokens,
# and Anthropic then *requires* streaming for requests that could exceed 10 minutes
# (the "Streaming is required..." error). GTM answers are short, so a modest cap
# keeps non-streaming requests valid. Override with GTM_MAX_TOKENS.
_MAX_TOKENS = int(os.environ.get("GTM_MAX_TOKENS", "8192"))

# The native Gemini class has no max_tokens field -- generation settings belong to
# the Agent, not the model -- so on that path the cap is applied via each Agent's
# generate_content_config below. LiteLlm keeps taking max_tokens directly.
_GEN_CONFIG = (
    types.GenerateContentConfig(max_output_tokens=_MAX_TOKENS)
    if _GEMINI_MODEL_NAME
    else None
)


def _gemini_key() -> str | None:
    """The Gemini API key, under either name a client might look for."""
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def _model() -> LiteLlm | Gemini:
    """Fresh model instance per agent (ADK expects a model object per agent).

    Gemini: ADK's native client. The API key is passed explicitly so it doesn't
    matter whether google-genai looks for GEMINI_API_KEY or GOOGLE_API_KEY.
    Anthropic: uses the token from auth.py (ANTHROPIC_API_KEY by default). Only if
    a gateway base URL is configured do we also send the Bearer header the gateway
    expects. Everything else points at a local/OpenAI-compatible server.
    """
    if _GEMINI_MODEL_NAME:
        gemini_kwargs: dict = {"model": _GEMINI_MODEL_NAME}
        key = _gemini_key()
        if key:
            gemini_kwargs["client_kwargs"] = {"api_key": key}
        return Gemini(**gemini_kwargs)

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
    elif _PROVIDER == "vertex_ai":
        # Vertex AI still goes through LiteLLM (nothing here uses it, so it hasn't
        # been moved to the native client). Plain "gemini/..." ids never reach this
        # branch -- they return above.
        key = _gemini_key()
        if key:
            kwargs["api_key"] = key
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
    generate_content_config=_GEN_CONFIG,
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
    generate_content_config=_GEN_CONFIG,
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
    generate_content_config=_GEN_CONFIG,
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
    generate_content_config=_GEN_CONFIG,
    description=(
        f"GTM lifecycle coordinator for {PRODUCT_NAME}; routes across Sales, "
        "Pre-Sales, and Customer Success specialists."
    ),
    instruction=prompts.COORDINATOR_INSTRUCTION,
    tools=_SHARED,
    sub_agents=[sales_agent, presales_agent, customer_success_agent],
)
