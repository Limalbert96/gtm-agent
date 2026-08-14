"""FastAPI chat frontend for the GTM lifecycle multi-agent app.

This is a thin, brandable web UI that sits in front of the existing ``gtm_agent``
ADK app so end users get a clean chat experience instead of the raw ADK dev UI.

Run it from the repository root (the parent of both ``gtm_agent/`` and ``web/``):

    uvicorn web.server:app --reload --port 8000

It needs the same Claude auth as the rest of the app (an ANTHROPIC_API_KEY, or
whatever ``gtm_agent`` resolves at runtime). This file is intentionally importable
even when google-adk is not installed: the heavy imports happen lazily inside the
request handlers, so you can inspect / syntax-check the module offline.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any, AsyncIterator, Optional

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
APP_NAME = "gtm_web"
USER_ID = "web-user"
COORDINATOR_NAME = "gtm_coordinator"

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_STATIC_DIR = _HERE / "static"           # legacy dependency-free page (fallback)
_SPA_DIST = _HERE / "frontend" / "dist"  # built React SPA (preferred if present)


def _load_dotenv() -> None:
    """Load the repo-root .env into os.environ so the web server picks up the
    same GTM_MODEL / auth config the ADK launchers get.

    Uvicorn doesn't load .env on its own, so without this the web frontend would
    fall back to the default model with no key. Done here (not via importing the
    gtm_agent package) so this module stays importable without google-adk. Real
    env vars win: we only fill keys that aren't already set.
    """
    env_path = _REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    try:
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if (value[:1], value[-1:]) in {('"', '"'), ("'", "'")}:
                value = value[1:-1]
            if key:
                os.environ.setdefault(key, value)
    except OSError:
        pass


_load_dotenv()

app = FastAPI(title="GTM Lifecycle Assistant")


# ---------------------------------------------------------------------------
# Lazy ADK runtime singleton.
#
# We build the ADK Runner + SessionService once and reuse them for the life of
# the process. ADK / google-adk / the agent package are imported lazily so that
# importing this module (for inspection or a syntax check) never requires the
# model dependencies to be installed.
# ---------------------------------------------------------------------------
class _Runtime:
    """Holds the singleton Runner + SessionService and tracks known sessions."""

    def __init__(self) -> None:
        self._runner: Any = None
        self._session_service: Any = None
        self._types: Any = None
        self._known_sessions: set[str] = set()
        self._lock = asyncio.Lock()

    async def ensure(self) -> None:
        """Build the runner/session service on first use (thread-safe-ish)."""
        if self._runner is not None:
            return
        async with self._lock:
            if self._runner is not None:  # re-check inside the lock
                return
            # Imported here so the module stays importable without google-adk.
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService
            from google.genai import types

            from gtm_agent import root_agent

            self._types = types
            self._session_service = InMemorySessionService()
            self._runner = Runner(
                agent=root_agent,
                app_name=APP_NAME,
                session_service=self._session_service,
            )

    async def _ensure_session(self, session_id: str) -> None:
        """Create the ADK session the first time we see this session_id."""
        if session_id in self._known_sessions:
            return
        await self._session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )
        self._known_sessions.add(session_id)

    async def run_turn(self, session_id: str, prompt: str) -> dict[str, str]:
        """Run one conversation turn and return {"reply", "agent"}."""
        await self.ensure()
        await self._ensure_session(session_id)

        message = self._types.Content(
            role="user", parts=[self._types.Part(text=prompt)]
        )

        reply_text = ""
        # Best-effort: which sub-agent authored the final answer. Falls back to
        # the coordinator name if the event doesn't expose an author/agent name.
        agent_name = COORDINATOR_NAME

        async for event in self._runner.run_async(
            user_id=USER_ID, session_id=session_id, new_message=message
        ):
            author = _event_author(event)
            if author:
                agent_name = author
            if (
                event.is_final_response()
                and getattr(event, "content", None)
                and event.content.parts
            ):
                text = event.content.parts[0].text
                if text:
                    reply_text = text

        if not reply_text:
            reply_text = "(The assistant returned no text for this turn.)"

        return {"reply": reply_text, "agent": agent_name or COORDINATOR_NAME}

    async def stream_turn(
        self, session_id: str, prompt: str
    ) -> AsyncIterator[tuple[str, Any]]:
        """Run one turn, yielding (kind, payload) events as they arrive.

        Yields, in order as ADK produces them:
            ("agent", name)             -- a new sub-agent is answering; the client
                                           treats this as a MESSAGE BOUNDARY and
                                           starts a fresh bubble
            ("delta", text)             -- append to the current bubble's answer
            ("replace", text)           -- replace the current bubble's answer
            ("thought", text)           -- append to the current bubble's reasoning
            ("agent_done", {agent, ms}) -- that agent finished, with its duration
            ("final", {reply, agent})   -- the turn is complete

        Reasoning is streamed separately from the answer so the UI can tuck it
        behind a disclosure instead of prepending a thinking model's deliberation
        to every reply. Durations are measured here rather than client-side
        because this loop is the only place that knows when an agent actually
        started and stopped.

        Whether text truly streams token-by-token depends on the installed
        google-adk version. If only the final event carries text, the client
        still gets a single "replace" then "final" -- it just appears at once.
        The prefix-growth check below turns any incremental events into deltas.
        """
        await self.ensure()
        await self._ensure_session(session_id)

        message = self._types.Content(
            role="user", parts=[self._types.Part(text=prompt)]
        )

        sent = ""            # answer text already emitted for the open bubble
        sent_thought = ""    # reasoning already emitted for the open bubble
        reply_text = ""
        agent_name = COORDINATOR_NAME     # ADK author of the current event
        client_agent = COORDINATOR_NAME   # bubble the client currently has open
        started = time.monotonic()
        specialists = {a.name for a in getattr(self._runner.agent, "sub_agents", [])}

        async for event in self._runner.run_async(
            user_id=USER_ID, session_id=session_id, new_message=message
        ):
            author = _event_author(event)
            if author:
                agent_name = author

            # A specialist consulted as a TOOL runs in a nested runner whose events
            # never reach this stream -- only its function_response does. Surface each
            # one as its own bubble, or three specialists' work collapses into
            # whatever the coordinator chose to say about it.
            for spec, answer in _tool_agent_answers(event, specialists):
                if sent or sent_thought:
                    yield (
                        "agent_done",
                        {"agent": client_agent, "ms": _elapsed_ms(started)},
                    )
                yield ("agent", spec)
                yield ("delta", answer)
                yield ("agent_done", {"agent": spec, "ms": _elapsed_ms(started)})
                client_agent = None  # whoever speaks next needs a fresh bubble
                sent = ""
                sent_thought = ""
                started = time.monotonic()

            thought = _event_thought(event)
            text = _event_text(event)

            # Open a new bubble whenever the speaker differs from what's on screen --
            # a real hand-off, or the coordinator resuming after a specialist's answer.
            # Skipping this when nothing was produced keeps empty bubbles out.
            if (thought or text) and client_agent != agent_name:
                if sent or sent_thought:
                    yield (
                        "agent_done",
                        {"agent": client_agent, "ms": _elapsed_ms(started)},
                    )
                yield ("agent", agent_name)
                client_agent = agent_name
                sent = ""
                sent_thought = ""
                started = time.monotonic()

            if thought and thought != sent_thought:
                # Same prefix-growth trick as the answer text below: emit only
                # what's new when the model streams cumulative reasoning.
                delta = (
                    thought[len(sent_thought):]
                    if thought.startswith(sent_thought)
                    else thought
                )
                if delta:
                    yield ("thought", delta)
                sent_thought = thought

            if text and text != sent:
                if text.startswith(sent):
                    yield ("delta", text[len(sent):])
                else:
                    yield ("replace", text)
                sent = text

            if event.is_final_response() and text:
                reply_text = text

        if sent or sent_thought:
            yield (
                "agent_done",
                {"agent": client_agent or agent_name, "ms": _elapsed_ms(started)},
            )
        if not reply_text:
            reply_text = sent or "(The assistant returned no text for this turn.)"
        yield ("final", {"reply": reply_text, "agent": agent_name or COORDINATOR_NAME})


_RUNTIME = _Runtime()


def _elapsed_ms(started: float) -> int:
    """Whole milliseconds since a time.monotonic() reading."""
    return int((time.monotonic() - started) * 1000)


def _parts_text(event: Any, *, thought: bool) -> str:
    """Concatenate an ADK event's text parts, selecting answer vs. reasoning.

    ADK marks a model's internal reasoning as ``Part(text=..., thought=True)``
    (see google/adk/models/lite_llm.py). Answer text and reasoning therefore live
    side by side on the same event, and the ``thought`` flag is the only thing
    separating them -- so callers must say which one they want.
    """
    content = getattr(event, "content", None)
    parts = getattr(content, "parts", None) if content else None
    if not parts:
        return ""
    chunks = [
        getattr(p, "text", None)
        for p in parts
        if bool(getattr(p, "thought", False)) is thought
    ]
    return "".join(c for c in chunks if c)


def _event_text(event: Any) -> str:
    """The answer text on an ADK event, excluding reasoning (empty if none).

    Excluding thought parts here is what keeps a thinking model's deliberation
    ("Okay, let me process this...") out of the reply.
    """
    return _parts_text(event, thought=False)


def _event_thought(event: Any) -> str:
    """The reasoning text on an ADK event, excluding the answer (empty if none)."""
    return _parts_text(event, thought=True)


def _tool_agent_answers(event: Any, specialists: set[str]) -> list[tuple[str, str]]:
    """Specialist answers that arrived as tool results, as (agent_name, text).

    The coordinator can reach a specialist two ways: transfer to it (the specialist
    becomes the event author, handled elsewhere) or call it as a tool. The tool path
    exists because a transfer can only ever reach ONE agent, so a multi-part question
    needs tool calls -- but a tool's inner agent runs in a nested runner whose events
    don't surface here. Its answer only appears as a function_response, which is what
    this reads so each specialist still gets attributed.
    """
    content = getattr(event, "content", None)
    parts = getattr(content, "parts", None) if content else None
    answers: list[tuple[str, str]] = []
    for part in parts or []:
        fn_response = getattr(part, "function_response", None)
        if fn_response is None or fn_response.name not in specialists:
            continue
        payload = fn_response.response
        text = payload.get("result") if isinstance(payload, dict) else payload
        if isinstance(text, str) and text.strip():
            answers.append((fn_response.name, text))
    return answers


def _event_author(event: Any) -> Optional[str]:
    """Best-effort extraction of the responding agent's name from an ADK event.

    Different google-adk versions expose this differently, so we try a few common
    attributes and return the first truthy one. Verify against your installed
    version (see README notes).
    """
    for attr in ("author", "agent_name"):
        value = getattr(event, attr, None)
        if isinstance(value, str) and value:
            return value
    return None


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    session_id: str
    message: str
    account_id: Optional[str] = None
    file_text: Optional[str] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
def _index_file() -> Path:
    """Prefer the built React SPA; fall back to the legacy static page."""
    spa = _SPA_DIST / "index.html"
    if spa.is_file():
        return spa
    return _STATIC_DIR / "index.html"


@app.get("/")
def index() -> FileResponse:
    """Serve the chat UI (built SPA if present, else the legacy page)."""
    return FileResponse(_index_file())


@app.get("/api/meta")
def meta() -> JSONResponse:
    """Small runtime descriptor for the UI header: model, product, playbook source."""
    model = os.environ.get("GTM_MODEL", "anthropic/claude-sonnet-4-20250514")
    product = "our platform"
    source = "generic"
    try:
        from gtm_agent.data import PRODUCT_NAME

        product = PRODUCT_NAME
    except Exception:
        pass
    try:
        from gtm_agent import playbooks

        source = playbooks.SOURCE
    except Exception:
        pass
    return JSONResponse(
        {"model": model, "product_name": product, "playbook_source": source}
    )


@app.get("/api/accounts")
def accounts() -> JSONResponse:
    """Return the account index for the selector (imported lazily)."""
    try:
        from gtm_agent.data import list_accounts

        return JSONResponse({"accounts": list_accounts()})
    except Exception as exc:  # pragma: no cover - depends on live env
        # Don't 500 the UI over a missing import; the selector just stays empty.
        return JSONResponse(
            {"accounts": [], "error": f"Could not load accounts: {exc}"}
        )


@app.get("/api/lifecycle")
def lifecycle() -> JSONResponse:
    """Return the ordered lifecycle stages + owning role (for the lifecycle rail)."""
    try:
        from gtm_agent.data import LIFECYCLE_STAGES

        return JSONResponse({"lifecycle": LIFECYCLE_STAGES})
    except Exception as exc:  # pragma: no cover
        return JSONResponse({"lifecycle": [], "error": str(exc)})


@app.post("/api/chat")
async def chat(req: ChatRequest) -> JSONResponse:
    """Run one turn through the ADK Runner and return the reply + agent name."""
    prompt = _compose_prompt(req.message, req.account_id, req.file_text)
    try:
        result = await _RUNTIME.run_turn(req.session_id, prompt)
        return JSONResponse(result)
    except ModuleNotFoundError as exc:
        return JSONResponse(
            {
                "reply": (
                    "The agent backend isn't available in this environment "
                    f"(missing module: {exc.name}). Install the app's dependencies "
                    "and make sure ANTHROPIC_API_KEY is set, then try again."
                ),
                "agent": COORDINATOR_NAME,
                "error": str(exc),
            }
        )
    except Exception as exc:  # keep the UI robust: never leak a raw 500
        return JSONResponse(
            {
                "reply": f"Sorry - the assistant hit an error: {exc}",
                "agent": COORDINATOR_NAME,
                "error": str(exc),
            }
        )


def _sse(kind: str, payload: Any) -> str:
    """Format one Server-Sent Event frame."""
    return f"event: {kind}\ndata: {json.dumps(payload)}\n\n"


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    """Stream one turn as Server-Sent Events (agent / delta / replace / final)."""
    prompt = _compose_prompt(req.message, req.account_id, req.file_text)

    async def gen() -> AsyncIterator[str]:
        try:
            async for kind, payload in _RUNTIME.stream_turn(req.session_id, prompt):
                yield _sse(kind, payload)
        except ModuleNotFoundError as exc:
            yield _sse(
                "error",
                {
                    "message": (
                        "The agent backend isn't available in this environment "
                        f"(missing module: {exc.name}). Install the app's "
                        "dependencies and set ANTHROPIC_API_KEY, then try again."
                    )
                },
            )
        except Exception as exc:  # never leak a raw 500 into the stream
            yield _sse("error", {"message": f"The assistant hit an error: {exc}"})

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)) -> JSONResponse:
    """Accept a file upload and return best-effort extracted plain text."""
    raw = await file.read()
    filename = file.filename or "attachment"
    file_text = _extract_text(filename, raw)
    return JSONResponse(
        {"file_text": file_text, "filename": filename, "chars": len(file_text)}
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _compose_prompt(
    message: str, account_id: Optional[str], file_text: Optional[str]
) -> str:
    """Assemble the final prompt: optional account context + message + attachment."""
    parts: list[str] = []
    if account_id:
        parts.append(f"Focus on account {account_id}.")
    parts.append(message or "")
    if file_text:
        parts.append("\n--- Attached document ---\n" + file_text)
    return "\n\n".join(p for p in parts if p).strip()


def _extract_text(filename: str, raw: bytes) -> str:
    """Extract plain text from an uploaded file, degrading gracefully.

    - text/*, .md, .csv, .txt, and friends: decode directly.
    - .pdf: use pypdf if importable.
    - .docx: use python-docx if importable.
    - anything else / extraction failure: return a friendly paste-the-text note.
    """
    lower = filename.lower()

    if lower.endswith(".pdf"):
        try:
            import io

            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(raw))
            pages = [(page.extract_text() or "") for page in reader.pages]
            text = "\n".join(pages).strip()
            return text or _paste_note(filename)
        except Exception:
            return _paste_note(filename, reason="PDF text extraction isn't available")

    if lower.endswith(".docx"):
        try:
            import io

            import docx  # python-docx

            document = docx.Document(io.BytesIO(raw))
            text = "\n".join(p.text for p in document.paragraphs).strip()
            return text or _paste_note(filename)
        except Exception:
            return _paste_note(
                filename, reason="Word (.docx) text extraction isn't available"
            )

    # Default: treat as text. Covers .txt, .md, .csv, .json, .log, text/* uploads.
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return raw.decode(encoding).strip()
        except (UnicodeDecodeError, LookupError):
            continue
    return _paste_note(filename, reason="This file didn't look like readable text")


def _paste_note(filename: str, reason: str = "") -> str:
    prefix = f"[{reason}. ] " if reason else ""
    return (
        f"{prefix}Couldn't extract text from '{filename}' automatically. "
        "Please paste the relevant text directly into the chat."
    )


# Mount static assets last so the explicit API/index routes above win.
# The built SPA emits hashed files under dist/assets, referenced as "/assets/..".
if (_SPA_DIST / "assets").is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=str(_SPA_DIST / "assets")),
        name="spa-assets",
    )
# Keep the legacy /static mount for the fallback page (and any of its assets).
if _STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
