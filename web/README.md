# GTM Lifecycle Assistant — Web Frontend

A dark "GTM Hub" console in front of the existing `gtm_agent` ADK multi-agent
app. It replaces the raw ADK dev UI with a four-view workspace, navigated from
the left sidebar:

- **GTM Coordinator** — the one *functional* view: a chat with the real,
  **streaming** ADK assistant ("ADK Intelligence"). The coordinator delegates to
  the specialist agents, and a role badge shows which specialist answered. A
  right rail carries a Strategic Overview and Next Steps.
- **Sales** — a GTM Intelligence deal board (KPI cards + kanban stages).
- **Pre-sales** — a Solution Dashboard (active validations, SA utilization,
  criteria templates).
- **Customer Success** — a CS Health Center (portfolio health, renewal risk,
  priority accounts, suggested playbooks).

> The Coordinator chat is wired to the live backend. The Sales, Pre-sales, and
> CS dashboards render **static demo data** (`frontend/src/demoData.js`) for
> visual fidelity — they are illustrative, not backed by the running agent.

Three parts:

- `server.py` — a FastAPI app that serves the UI and proxies chat turns through
  the ADK `Runner`. Streams responses over Server-Sent Events.
- `frontend/` — a **React + Vite** single-page app (the modern UI). Its source
  lives here; `npm run build` emits `frontend/dist/`, which the server serves.
- `static/index.html` — the original dependency-free page, kept as a fallback
  for when `frontend/dist/` hasn't been built.

The server prefers the built SPA and falls back to the static page automatically.

## Running

You need **Python** (for the backend) and **Node 18+** (to build the frontend).

### 1. Backend

From the **repository root** (the parent of both `gtm_agent/` and `web/`), so
`import gtm_agent` resolves:

```bash
pip install -r requirements.txt -r web/requirements.txt
uvicorn web.server:app --reload --port 8000
```

Then open http://localhost:8000.

> Tip: don't paste the URL onto the `uvicorn` line as a `# comment` —
> interactive zsh doesn't treat `#` as a comment, so it gets passed to uvicorn
> as arguments and errors out. Put the URL on its own line.

### 2. Frontend

**Option A — build once, served by FastAPI (simplest).** From `web/frontend/`:

```bash
cd web/frontend
npm install
npm run build      # emits web/frontend/dist/
```

Reload http://localhost:8000 — the server now serves the built React app.
Rebuild whenever you change the frontend source.

**Option B — live dev server with hot reload.** Run the backend (step 1) and,
in a second terminal:

```bash
cd web/frontend
npm install
npm run dev        # http://localhost:5173, proxies /api -> :8000
```

Use `:5173` while developing; it hot-reloads on save.

## Auth

Same Claude auth as the rest of the app — set `ANTHROPIC_API_KEY` (or whatever
`gtm_agent` resolves at runtime, e.g. Gemini's `GEMINI_API_KEY`) in your
environment before starting the server. The frontend adds no auth of its own.

## Endpoints

- `GET /` — the chat UI (built SPA if present, else the legacy page).
- `GET /api/meta` — `{model, product_name, playbook_source}` for the header.
- `GET /api/accounts` — account index for the selector.
- `GET /api/lifecycle` — ordered lifecycle stages + owning role (for the rail).
- `POST /api/chat/stream` — body `{session_id, message, account_id?, file_text?}`.
  Streams the turn as SSE frames: `agent` (responding specialist changed),
  `delta` / `replace` (text), `final` (`{reply, agent}`), `error`.
- `POST /api/chat` — the same turn, non-streaming, returns `{reply, agent}`.
  Kept for simple/legacy clients.
- `POST /api/upload` — multipart file upload; returns `{file_text, filename,
  chars}`. Text files decode directly; PDF/`.docx` extraction is attempted only
  if `pypdf` / `python-docx` are installed.

## Design notes

- **Color is information.** Each role has a fixed accent — Sales (amber),
  Pre-Sales (teal), Customer Success (violet), Coordinator (slate). The header
  accent and the lifecycle-rail dots use these, so you can see which specialist
  owns each stage and who's currently answering.
- The **lifecycle rail** is the signature element: eight stages as a spine,
  dots colored by the owning role, the account's current stage ringed with its
  exit criteria.
- Fonts (Space Grotesk + Inter) are bundled via `@fontsource` — no CDN, works
  offline — and degrade to system fonts if unavailable.
- No `localStorage`; state is in-memory per page load. Sessions are in-memory
  per server process, so restarting the server clears history.

## Status

The React frontend is authored source; **build it with `npm run build`** (needs
network access to npm the first time). The `server.py` streaming reads ADK event
text and the responding agent's name best-effort across google-adk versions — if
the badge always shows the coordinator, confirm the event attribute names
against your installed version.
