"""Environment / .env loading, shared by every entry point.

The agent reads its model + auth settings from environment variables (GTM_MODEL,
ANTHROPIC_API_KEY, the internal-gateway vars, etc.). ADK's own launchers load a
``.env`` for you, but the FastAPI web server, ``run_cli.py``, and tests do not --
so this module provides one dependency-free loader they all call, and the values
land in ``os.environ`` regardless of how the app was started.

Real environment variables always win: we only fill in keys that aren't already
set, so ``GTM_MODEL=... uvicorn ...`` still overrides the file.
"""

from __future__ import annotations

import os
from pathlib import Path

# Repo root = the parent of the gtm_agent package (where .env lives).
_REPO_ROOT = Path(__file__).resolve().parent.parent
_LOADED = False


def load_env(path: str | os.PathLike | None = None) -> None:
    """Load KEY=VALUE lines from the repo-root .env into os.environ (once).

    Uses python-dotenv if it's installed (nicer parsing), otherwise falls back
    to a small built-in parser so there's no hard dependency. Idempotent.
    """
    global _LOADED
    if _LOADED and path is None:
        return

    env_path = Path(path) if path else _REPO_ROOT / ".env"
    if not env_path.is_file():
        _LOADED = True
        return

    try:
        from dotenv import load_dotenv  # optional dependency

        load_dotenv(env_path, override=False)
    except Exception:
        _parse_into_environ(env_path)

    if path is None:
        _LOADED = True


def _parse_into_environ(env_path: Path) -> None:
    """Minimal .env parser: KEY=VALUE per line, '#' comments, optional quotes."""
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        if key:
            os.environ.setdefault(key, value)
