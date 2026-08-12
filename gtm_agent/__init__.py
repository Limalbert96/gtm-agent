"""GTM lifecycle agent package.

ADK's `adk web` / `adk run` import this package and look for `agent.root_agent`.
The eager import below also makes `from gtm_agent import root_agent` work.

It's guarded so the pure-Python tool logic (in `tools/` and `data.py`) stays
importable and testable even in an environment where google-adk isn't installed
(e.g. running validate_offline.py in CI without the model deps).
"""

try:
    from . import agent  # noqa: F401
    from .agent import root_agent  # noqa: F401
except ModuleNotFoundError as _e:  # google-adk not installed; tools still usable.
    if _e.name not in {"google", "google.adk", "litellm"}:
        raise
