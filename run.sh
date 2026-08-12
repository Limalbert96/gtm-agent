#!/usr/bin/env bash
#
# Convenience launcher for the GTM lifecycle agent.
#
#   ./run.sh          # start the ADK web UI (default)
#   ./run.sh web      # same as above
#   ./run.sh cli      # one-shot terminal run (uses run_cli.py)
#   ./run.sh check    # offline validation, no key / no network
#
# Telemetry: this records "disabled" once so ADK never shows the consent prompt,
# and also auto-answers "no" to the first-run prompt just in case.

set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"
CMD="${1:-web}"

# Turn ADK telemetry off, quietly. Safe to run every time; ignore if unsupported.
"$PY" -m google.adk.cli telemetry disable >/dev/null 2>&1 || true

case "$CMD" in
  web)
    # `printf 'n\n'` auto-declines the consent prompt if it ever appears.
    printf 'n\n' | "$PY" -m google.adk.cli web
    ;;
  cli)
    shift || true
    "$PY" run_cli.py "$@"
    ;;
  check)
    "$PY" validate_offline.py
    ;;
  *)
    echo "usage: ./run.sh [web|cli|check]" >&2
    exit 2
    ;;
esac
