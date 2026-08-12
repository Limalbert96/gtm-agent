"""Playbook content for the GTM agents, with a private-over-generic override.

The agents "bake in" real sales content through this module. By default they use
the public-safe guides in ``generic.py``. If an organization-specific pack exists at
``gtm_agent/playbooks/private/content.py`` (gitignored — never committed), any names
it defines override the generic ones at runtime.

This is the same safety pattern as ``.env``: the confidential material lives only in
a local, gitignored file, so a fresh public clone works out of the box on the
generic content and can never leak the private version.

Exposed names: MEDDPICC_GUIDE, POV_TRIAL_GUIDE, RFP_GUIDE, DEMO_GUIDE, SALES_PLAYS, SOURCE.
"""

from __future__ import annotations

from typing import Any

from . import generic

try:  # optional, gitignored, present only in a private/internal checkout
    from .private import content as _private  # type: ignore
except Exception:  # nothing private installed -> pure generic content
    _private = None  # type: ignore

# Which pack is actually in effect (handy for a "where did this come from" tool).
SOURCE = "private" if _private is not None else "generic"


def _pick(name: str) -> Any:
    """Return the private value for ``name`` if the private pack defines it, else generic."""
    if _private is not None and hasattr(_private, name):
        return getattr(_private, name)
    return getattr(generic, name)


MEDDPICC_GUIDE: str = _pick("MEDDPICC_GUIDE")
POV_TRIAL_GUIDE: str = _pick("POV_TRIAL_GUIDE")
RFP_GUIDE: str = _pick("RFP_GUIDE")
DEMO_GUIDE: str = _pick("DEMO_GUIDE")
SALES_PLAYS: dict[str, Any] = _pick("SALES_PLAYS")

# Topic -> guide text, for the get_playbook tool.
GUIDES: dict[str, str] = {
    "meddpicc": MEDDPICC_GUIDE,
    "pov": POV_TRIAL_GUIDE,
    "trial": POV_TRIAL_GUIDE,
    "rfp": RFP_GUIDE,
    "demo": DEMO_GUIDE,
    "aotp": DEMO_GUIDE,
}
