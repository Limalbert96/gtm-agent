"""Claude authentication for the GTM agent.

Public default (nothing else required): read ANTHROPIC_API_KEY from the
environment and call Anthropic's public API.

Optional: route Claude through an internal gateway that mints a short-lived token
and authenticates on a Bearer header. That support lives entirely in the single
INTERNAL GATEWAY block at the bottom of this file, is OFF unless you set
GTM_USE_INTERNAL_GATEWAY=1, and reads its command/URL from environment variables
so no internal hostnames are hard-coded here.

    >>> If you don't want gateway support in a public repo, delete the one
    >>> block marked "INTERNAL GATEWAY" below. Nothing else references it. <<<
"""

from __future__ import annotations

import os


def resolve_api_token() -> str | None:
    """Return a Claude auth token, or None if none is configured.

    Public default is the ANTHROPIC_API_KEY env var. If the internal gateway is
    explicitly enabled and yields a token, that wins.
    """
    token, _ = _internal_gateway()  # no-op unless GTM_USE_INTERNAL_GATEWAY=1
    return token or os.environ.get("ANTHROPIC_API_KEY") or None


def base_url() -> str | None:
    """The API base URL, or None to use Anthropic's default endpoint.

    Only set when routing through a gateway (internal gateway, or an explicit
    GTM_BASE_URL override).
    """
    _, gateway = _internal_gateway()
    return gateway or os.environ.get("GTM_BASE_URL") or None


# ===========================================================================
#  INTERNAL GATEWAY  —  optional, OFF by default.
#  --------------------------------------------------------------------------
#  Enable locally by setting these in your (gitignored) .env:
#      GTM_USE_INTERNAL_GATEWAY=1
#      GTM_KEY_COMMAND=/path/to/token-command      # prints a token (JSON or raw)
#      GTM_BASE_URL=https://your-internal-gateway  # gateway endpoint
#
#  It shells out to GTM_KEY_COMMAND to mint a short-lived token and routes
#  requests through GTM_BASE_URL (agent.py adds the Bearer header).
#
#  >>> DELETE THIS ENTIRE BLOCK (down to "END INTERNAL GATEWAY") before pushing
#  >>> to a public repo if you don't want gateway support shipped.
# ===========================================================================
def _internal_gateway() -> tuple[str | None, str | None]:
    """Return (token, gateway_url) from the internal gateway, or (None, None)."""
    if os.environ.get("GTM_USE_INTERNAL_GATEWAY") != "1":
        return None, None

    import json
    import subprocess

    key_command = os.environ.get("GTM_KEY_COMMAND")
    gateway = os.environ.get("GTM_BASE_URL") or None
    if not key_command:
        return None, gateway

    try:
        result = subprocess.run([key_command], capture_output=True, text=True, timeout=10)
        raw = result.stdout.strip()
        if raw:
            try:
                data = json.loads(raw)
                for field in ("token", "api_key", "key", "anthropic_api_key"):
                    if data.get(field):
                        return data[field], gateway
            except json.JSONDecodeError:
                pass  # not JSON -- treat the whole output as the token
            return raw, gateway
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass  # command not present -- fall through to the public default

    return None, gateway
# ===========================================================================
#  END INTERNAL GATEWAY
# ===========================================================================
