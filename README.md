---
title: GTM Lifecycle Agent
emoji: 🚀
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
---

<!--
The YAML block above is Hugging Face Space metadata (Docker SDK), required for
deploying to a Space. It must stay at the very top of this file. Other Markdown
viewers ignore it, and it is only used if you deploy to a Space — the primary
deployment is Render. See the "Deploy" section below.
-->

# GTM Lifecycle Agent

A multi-agent assistant that models a **B2B go-to-market lifecycle** across the
three roles that carry a deal from first touch to renewal:

- **Sales** — Account Executive: commercial owner, qualification, close.
- **Pre-Sales** — Solutions Consultant / Sales Engineer: the technical win.
- **Customer Success** — Technical Success Manager: onboarding, adoption, expansion, renewal.

Built on **Google's Agent Development Kit (ADK)** as the agent framework, with
**Claude** as the model backend (via ADK's LiteLLM wrapper — no Gemini/Vertex needed).
The examples use an observability-software sales motion, but the product is generic
(`GTM_PRODUCT_NAME`) and the structure works for any consumption-priced B2B product.

It's a reusable scaffold: it runs out of the box against a small in-memory sample
"CRM + telemetry" dataset, and every data accessor is a single, obvious seam where you
plug in real sources (Salesforce/HubSpot for pipeline, your product's API/MCP for usage).

## Architecture

```
Coordinator (root_agent)              routes by lifecycle stage
  ├─ Sales (sales_agent)              qualify (MEDDPICC) · deal economics · mutual action plan
  ├─ Pre-Sales (presales_agent)       POV scoping · demo scripts · discovery · battlecards · ingest sizing
  └─ Customer Success (cs_agent)      onboarding · adoption health · expansion · renewal risk
```

The coordinator uses ADK's LLM-driven delegation: it reads the account's current
lifecycle stage and transfers control to whichever role owns that stage.

### The lifecycle spine

| Stage | Owner | Exit criteria |
|---|---|---|
| Prospecting | Sales | Qualified meeting with an economic buyer or champion |
| Discovery | Sales | Business pain, metrics, and decision process documented (MEDDPICC) |
| Technical Validation | Pre-Sales | Success criteria met in a scoped POV; technical win |
| Proposal & Business Case | Sales | Quantified ROI and pricing accepted |
| Negotiation & Close | Sales | Signed order form; procurement/legal cleared |
| Onboarding | Customer Success | First value: data flowing, first dashboards/alerts live |
| Adoption | Customer Success | Committed use cases in production; healthy active-user growth |
| Expansion & Renewal | Customer Success | Renewal secured and/or expansion created for Sales |

## Setup

```bash
cd gtm-agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env` (set `ANTHROPIC_API_KEY`, or a `GTM_MODEL` for a local/other backend).

### Auth

The default is a standard Anthropic API key — set `ANTHROPIC_API_KEY` in `.env` and
you're done. Model selection is via `GTM_MODEL` (a LiteLLM `provider/name` id), so you
can swap models without touching code. The repo-root `.env` is loaded automatically by
every entry point (the ADK launchers, `run_cli.py`, and the `web/` server), so your
settings apply no matter how you start the app.

If you route Claude through a corporate/internal gateway that mints a short-lived
token, there's an opt-in **INTERNAL GATEWAY** block in `gtm_agent/auth.py` (off unless
`GTM_USE_INTERNAL_GATEWAY=1`; reads its command + URL from env, so no hostnames are
hard-coded). Put those values in your local, gitignored `.env`.

## Run

**Launcher script** (declines ADK's telemetry prompt for you). `./run.sh` starts
the ADK dev UI; `./run.sh cli "..."` runs one CLI turn; `./run.sh check` runs the
offline validation (no key/network):

```bash
./run.sh
./run.sh cli "How qualified is the Acme Retail deal?"
./run.sh check
```

**ADK dev UI (manual)** — from the project root, so ADK discovers the `gtm_agent` package:

```bash
adk web            # or, if the adk shortcut isn't on PATH: python3 -m google.adk.cli web
```

Then open the printed local URL and pick `gtm_agent`.

**One-shot from the CLI:**

```bash
python run_cli.py "How qualified is the Acme Retail deal, and what's the gap to close?"
```

**Validate without an API key or network** (exercises all tool logic, and builds the
agent tree if ADK is installed):

```bash
python validate_offline.py
```

## Web UI — "GTM Hub" (optional)

`web/` contains a dark **GTM Hub** console (an alternative to the raw ADK dev UI):
a four-view workspace navigated from the left sidebar —

- **GTM Coordinator** — the one *functional* view: a chat with the real,
  **streaming** ADK assistant. The coordinator delegates to the specialists, and a
  role badge shows which one answered. File upload works here (drop a discovery
  transcript and ask for the MEDDPICC gaps).
- **Sales / Pre-Sales / Customer Success** — dashboards (deal board, solution
  dashboard, CS health center) rendered from **static demo data**
  (`web/frontend/src/demoData.js`) for visual fidelity; illustrative, not wired to
  the live agent.

It's a **React + Vite** SPA (needs Node 18+) served by a FastAPI backend.

> ⚠️ **Paste one line at a time and drop the `#` annotations below.** Interactive
> zsh does *not* treat `#` as a comment, so a trailing `# ...` gets passed to the
> command as arguments and errors out (npm/vite/cd/uvicorn all break this way).

First time — install deps (one line at a time):

```bash
pip install -r requirements.txt -r web/requirements.txt
```
```bash
cd web/frontend
npm install
npm run build
```

Then, from the **repo root**, run the backend:

```bash
cd ~/Documents/alim_workspace/gtm-agent
uvicorn web.server:app --reload --port 8000
```

Open http://localhost:8000. Rebuild the frontend (`npm run build`) only when you
change frontend source. For live hot-reload during development, run `npm run dev`
in `web/frontend/` instead (serves on `:5173`, proxies `/api` to the backend). See
`web/README.md` for details.

## Observability (optional)

ADK instruments the agent with OpenTelemetry (the spans behind the dev UI's "Trace"
view). `gtm_agent/observability.py` exports **traces, metrics, and logs** over OTLP to
any compatible backend — New Relic, Grafana, Honeycomb, a local Collector. It's off
unless an endpoint is set, vendor-neutral (no hostnames in code), and configured
**entirely by environment variables**: there is nothing to edit in that file to point it
at a backend.

These variables are documented here only; the deploy sections point back to this table.

| Variable | Purpose |
|---|---|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Base URL — setting it is what turns telemetry on. No `/v1/...` path; the SDK appends it. |
| `OTEL_EXPORTER_OTLP_HEADERS` | Auth, as a comma-separated list of `name=value` header pairs. New Relic: `api-key=<ingest License key>`. |
| `OTEL_SERVICE_NAME` | Service name in the backend (default `gtm-agent`). |
| `OTEL_RESOURCE_ATTRIBUTES` | Optional extra resource tags, e.g. `deployment.environment=render`. |
| `GTM_OTEL_METRICS` | `0` to skip the metrics pipeline. |
| `GTM_OTEL_LOGS` | `0` to skip the logs pipeline. |
| `GTM_OTEL_LOG_LEVEL` | Minimum level shipped as logs (default `INFO`). |

Locally:

```bash
pip install -r requirements-otel.txt      # the Dockerfile already installs these
export OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.nr-data.net
export OTEL_EXPORTER_OTLP_HEADERS="api-key=YOUR_INGEST_LICENSE_KEY"
export OTEL_SERVICE_NAME=gtm-agent
```

Startup prints which signals came up — the fastest way to tell config from plumbing:

```
[observability] OTel enabled -> https://otlp.nr-data.net (service.name=gtm-agent, signals=traces+metrics+logs)
```

### New Relic specifics

- **Endpoint:** `https://otlp.nr-data.net`, or `https://otlp.eu01.nr-data.net` for an EU
  account — the wrong region 403s.
- **Key:** an **ingest License key** (~40 chars, usually ends `NRAL`), *not* a user key
  (`NRAK-…`), sent as the `api-key` header:
  `OTEL_EXPORTER_OTLP_HEADERS=api-key=NRAL…`
  - The doubled `=` is correct. Per the
    [OTLP exporter spec](https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/),
    this variable is a comma-separated list of `name=value` header pairs — unlike the
    scalar `OTEL_SERVICE_NAME` and `..._ENDPOINT`. Drop the `api-key=` and it fails
    silently: the SDK logs `Header format invalid!`, sends no auth header, and every
    export 403s while the app looks perfectly healthy.
  - Other backends use their own header name — e.g. `x-honeycomb-team=<key>`.
- **No quotes** when typing it into a hosting dashboard — the `"…"` above is shell syntax.
- **`OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT=4095`** and
  **`OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT=4095`** — ADK puts prompts and responses on
  span attributes, and New Relic drops values longer than this. Set both.
- **`OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE=DELTA`** — what New Relic expects
  for counters and histograms.

**Where each signal lands.** OTel's three signals become three New Relic data types, each
queried separately:

| Signal | NRQL |
|---|---|
| Traces | `FROM Span SELECT * WHERE service.name = 'gtm-agent'` |
| Logs | `FROM Log SELECT * WHERE service.name = 'gtm-agent'` |
| Metrics | `FROM Metric SELECT * WHERE service.name = 'gtm-agent'` |

On "events": spans **are** events in New Relic — a trace arrives as `Span` records, which
is what powers APM & Services and the distributed-trace UI. OTel has no separate event
signal; OTel "events" are log records carrying an `event.name`, so they ride the logs
pipeline.

Traces and metrics both carry real data (see below). Logs are whatever the app and its
libraries write through stdlib `logging`, automatically stamped with the active
`trace_id`/`span_id` so each record correlates to a span.

### GenAI conventions and New Relic AI monitoring

**No extra GenAI instrumentation is needed.** ADK self-instruments against the OpenTelemetry
[GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/). The
per-framework instrumentors New Relic's AI-monitoring guide lists (`OpenAIInstrumentor`,
`AnthropicInstrumentor`, `LangchainInstrumentor`) are for apps that call an LLM SDK
directly — this one goes through ADK, which already emits the conventions itself.

ADK 2.6.3 emits, among others:

- **Span attributes:** `gen_ai.system`, `gen_ai.operation.name`, `gen_ai.request.model`,
  `gen_ai.request.max_tokens`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`,
  `gen_ai.response.finish_reasons`, `gen_ai.agent.name`, `gen_ai.tool.definitions`,
  `gen_ai.conversation.id`.
- **Metrics:** `gen_ai.invoke_agent.duration`, `gen_ai.invoke_workflow.duration`,
  `gen_ai.execute_tool.duration`, `gen_ai.invoke_agent.inference_calls`,
  `gen_ai.invoke_agent.tool_calls`, plus client operation duration and token usage. This
  is why the metrics pipeline is worth leaving on — per-agent latency, tool-call counts,
  and token usage all arrive as `Metric` data.

New Relic identifies AI spans by the presence of `gen_ai.system` / `gen_ai.provider.name`,
so **APM & Services → AI monitoring** should populate with no extra work. Confirm with:

```sql
FROM Span SELECT count(*)
WHERE `gen_ai.system` IS NOT NULL OR `gen_ai.provider.name` IS NOT NULL
FACET `service.name`, `gen_ai.operation.name`
```

Two caveats: AI monitoring is a **preview** feature that must be enabled on the account,
and its views key off `gen_ai.operation.name` values like `chat` — ADK also emits
agent/tool/workflow operations, which may only surface in raw `Span` queries.

> **Prompt content ships by default.** ADK's `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS`
> defaults *on*, which puts `gen_ai.input.messages`, `gen_ai.output.messages`, and
> `gen_ai.system_instructions` — full prompt and response text — into your backend. Set it
> to `false` to send latency, tokens, and errors only. (ADK's own `adk deploy` defaults it
> to `false` for exactly this reason.) Relevant once real CRM data replaces `data.py`.

## Things to ask it

- "What accounts do I have and what stage is each in?"
- "How qualified is the Acme Retail deal? What are the MEDDPICC gaps?" *(Sales)*
- "Size the Acme deal — ~640 GB/mo ingest, 22 full users, 60 core." *(Sales)*
- "Scope a POV for Acme and give me an APM demo script." *(Pre-Sales)*
- "Build me a discovery + competitive plan against Datadog." *(Pre-Sales)*
- "Is Initech healthy on adoption, and what's the renewal risk?" *(Customer Success)*
- "Give me a deal-team plan to advance Acme Retail to close." *(cross-functional)*

## Sample accounts

A roster spanning the whole lifecycle, so every role has live work — and the web
dashboards (which mirror this same data) stay populated:

| Account | Stage | Owner focus | Notes |
|---|---|---|---|
| **Nexus Industries** | Discovery | Sales | Manufacturing/IoT; Nagios incumbent, no sponsor yet |
| **Globex FinTech** | Discovery | Sales | Splunk + Dynatrace incumbent; economic buyer not yet accessed |
| **Acme Retail** | Technical Validation | Pre-Sales | Active POV (9d left), displacing Datadog |
| **Meridian Health** | Technical Validation | Pre-Sales | POV At Risk (5d left); HIPAA/PII-redaction criterion open |
| **Vertex Logistics** | Negotiation & Close | Sales | Through legal, awaiting signature; displacing Datadog |
| **Sterling Financial** | Onboarding | Customer Success | New customer; ramping seats |
| **Initech SaaS** | Adoption | Customer Success | Soft usage (5/14 seats), renewal ~120 days — renewal risk |
| **Umbra Media** | Expansion & Renewal | Customer Success | Healthy; RUM + mobile upsell signal |

The web dashboard demo data lives in `web/frontend/src/demoData.js` and is kept in
sync with these accounts — edit one, mirror the other.

## Playbooks (methodology + private content)

The agents "bake in" real sales methodology through `gtm_agent/playbooks/`. Out of
the box they use the public-safe generic guides in `playbooks/generic.py` — a
standard MEDDPICC qualification framework, POV/trial governance, RFP/questionnaire
handling, and a couple of observability sales plays — surfaced to agents both in
their instructions and via the `get_playbook(topic)` and `list_sales_plays` tools.

To layer in organization-specific content (your real trial process, RFP tooling,
named plays, etc.), create `gtm_agent/playbooks/private/content.py` defining the
same names (`MEDDPICC_GUIDE`, `POV_TRIAL_GUIDE`, `RFP_GUIDE`, `SALES_PLAYS`). That
folder is **gitignored** — it overrides the generic content at runtime but is never
committed, so nothing internal leaks into the public repo. Same safety model as
`.env`.

## Wiring in real data

`gtm_agent/data.py` is the only file that knows about data sources. Replace the
bodies of `list_accounts()` / `get_account()` (and swap the `usage` block for a live
API/MCP call) while keeping the returned dict shapes stable — the tools and agents keep
working unchanged.

## Project layout

```
gtm-agent/
├── gtm_agent/
│   ├── __init__.py         # exposes root_agent (guarded so tools import without ADK)
│   ├── agent.py            # coordinator + Sales/Pre-Sales/Customer Success sub-agents
│   ├── auth.py             # Claude auth (ANTHROPIC_API_KEY; opt-in internal gateway)
│   ├── observability.py    # optional OpenTelemetry OTLP export
│   ├── prompts.py          # per-role instructions
│   ├── data.py             # sample CRM/telemetry + the real-source seam
│   ├── playbooks/          # baked-in methodology (generic; private/ is gitignored)
│   └── tools/
│       ├── shared_tools.py # account lookup, lifecycle map
│       ├── ae_tools.py     # qualification, pricing, MAP           (Sales)
│       ├── sc_tools.py     # POV, demo, discovery, battlecards, ingest (Pre-Sales)
│       └── tsm_tools.py    # onboarding, adoption, expansion, renewal (Customer Success)
├── web/                    # optional chat console
│   ├── server.py           # FastAPI: serves the UI, streams turns (SSE)
│   ├── frontend/           # React + Vite SPA (source; build -> dist/)
│   └── static/             # legacy dependency-free page (fallback)
├── run_cli.py              # programmatic ADK Runner example
├── validate_offline.py     # no-key, no-network sanity checks
├── Dockerfile              # builds the SPA + serves it; used by Render / HF Spaces
├── .github/workflows/      # optional: mirror this repo to a Hugging Face Space
├── requirements.txt
├── requirements-otel.txt   # optional tracing deps
└── .env.example
```

## Choosing a model

The model id defaults to `anthropic/claude-sonnet-4-20250514` (LiteLLM
`provider/name` form). Swap backends with `GTM_MODEL` — no code change:

- **Anthropic:** `anthropic/claude-...` + `ANTHROPIC_API_KEY` (default).
- **Google Gemini:** `gemini/gemini-2.5-pro` (or `-flash`) + `GEMINI_API_KEY` from
  [AI Studio](https://aistudio.google.com/apikey). Uses ADK's **native** Gemini client
  rather than LiteLLM — see below.
- **Groq (hosted open models, free tier):** `groq/llama-3.3-70b-versatile` +
  `GROQ_API_KEY` — solid tool-calling, no local GPU. Good for free hosting (see below).
- **Local (Ollama / LM Studio / vLLM):** e.g. `ollama_chat/qwen3`.

**Gemini goes through ADK's native client.** Every other provider is wrapped in ADK's
LiteLLM adapter, but Gemini via LiteLLM gives up streaming and tool-calling fidelity, and
ADK warns about it (`[GEMINI_VIA_LITELLM]`). So a `gemini/…` id builds
`Gemini("gemini-2.5-flash")` directly and passes `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) to
it explicitly. `GTM_MAX_TOKENS` still applies — the native class has no `max_tokens`, so
it's set as each agent's `generate_content_config.max_output_tokens` instead. There's
nothing to configure and no env var to add: a `gemini/` id picks the native client, and
LiteLLM is never involved.

Because this is a **tool-calling** multi-agent system, if you run a local model
choose one with solid function-calling support (e.g. `qwen3`, `qwen2.5`, `mistral`,
`llama3.1`). Smaller models often mangle the delegation and tool arguments. See
`.env.example` for all the vars.

**Switching local models (Ollama).** The string after `ollama_chat/` must match the
Ollama tag exactly (`ollama list`), e.g. `ollama_chat/qwen3` (8B), `ollama_chat/qwen3:32b`,
`ollama_chat/qwen3-code`. Edit `GTM_MODEL` in `.env`, then **restart uvicorn** so it
reloads. Confirm with `curl -s localhost:8000/api/meta`. If the coordinator prints a
literal `transfer_to_agent(...)` instead of handing off, the model failed to fire the
tool call — try the larger `qwen3:32b`, or make routing explicit in `agent.py`.

> Ollama runs as a background service, so you don't need `ollama serve` — an
> `address already in use` on `:11434` just means it's already up. Keep `.env`
> values free of trailing `# comments`: the web server's `.env` reader doesn't strip
> them, so they become part of the value (e.g. a broken `GTM_LOCAL_BASE_URL`).

## Deploy

The repo ships a `Dockerfile`, so one image runs anywhere Docker does: it builds the
React SPA and serves the whole app (UI + streaming API) from a single port — `7860` by
default, or whatever `$PORT` the host injects.

Neither free tier below can host open-model *weights* (CPU only), so the app always calls
a hosted model API; `GTM_MODEL` alone picks which one. In both cases the host supplies
**no** model key — that's a separate, free signup with a model provider.

- **[Render](#render-docker)** — the primary deployment.
- **[Hugging Face Spaces](#hugging-face-spaces-free-alternative)** — free alternative and
  fallback, with an optional GitHub Action that keeps a Space mirrored automatically.

### Render (Docker)

**1. Create the service** — [dashboard.render.com](https://dashboard.render.com) →
**New → Web Service** → connect this GitHub repo. Render detects the `Dockerfile` and
picks the **Docker** runtime; leave the build and start commands **empty** (the image's
`CMD` handles both). Choose a region and the **Free** instance type.

**2. Add environment variables** — in the creation form's *Environment* section, or the
*Environment* tab afterwards. **Never commit `.env`**; on Render every value lives here.

| Variable | Value | Notes |
|---|---|---|
| `GTM_MODEL` | `gemini/gemini-2.5-flash` | LiteLLM `provider/name`. Also `groq/llama-3.3-70b-versatile`, `anthropic/claude-sonnet-4-20250514`. |
| `GEMINI_API_KEY` | `AIza…` | Required for `gemini/…` — [AI Studio](https://aistudio.google.com/apikey). |
| `GROQ_API_KEY` | `gsk_…` | Required for `groq/…` — [console.groq.com/keys](https://console.groq.com/keys). Safe to keep both keys set; `GTM_MODEL` alone selects the provider. |
| `GTM_MAX_TOKENS` | `4096` | Output ceiling, not a reservation. Raise only if answers truncate. |
| `GTM_PRODUCT_NAME` | `Acme Observability` | Optional — brands what the agents sell. |

For telemetry, add the variables from [Observability](#observability-optional) — same
names and values, entered here **without** the shell quoting. Nothing else to configure;
the image already ships the exporters.

> Telemetry carries prompt and response text — the account and deal details from
> `data.py`. Sample data today, but worth remembering before wiring in a real CRM.

**3. Create Web Service.** Render builds the image and boots it, then redeploys on every
push to the connected branch (auto-deploy is on by default). The app lands at
`https://<service-name>.onrender.com`.

**Things that bite on Render:**

- **Don't set `PORT` yourself.** Render injects it and the image honors `${PORT:-7860}`;
  overriding it breaks routing.
- **Don't set `GTM_LOCAL_BASE_URL` or `GTM_LOCAL_API_KEY`.** Any provider other than
  Anthropic and Gemini takes the local-model branch in `agent.py`, where those two vars
  are injected as `api_base`/`api_key` — which breaks Groq with a connection error or a
  misleading 401.
- **Free instances spin down** after ~15 minutes idle; the next request cold-starts
  (roughly 30–60s).
- **Free instances are memory-tight** and ADK + LiteLLM are heavy imports. A boot that
  dies with no Python traceback is usually the OOM killer — bump the instance size.
- **Verify from the logs:** the uvicorn startup line, plus
  `[observability] OTel enabled -> … (signals=traces+metrics+logs)` if you set the OTel
  vars. Seeing `OpenTelemetry SDK is not installed` instead means the build predates
  `requirements-otel.txt` being added to the `Dockerfile` — redeploy.

### Hugging Face Spaces (free, alternative)

The same image also runs as-is on a **Space** (Docker SDK), free CPU tier, no credit
card. A Space routes to `app_port` from the YAML front-matter at the very top of this
README (`7860`) — keep that block first in the file or the Space won't configure itself.

You need two free accounts, and they're unrelated: **Hugging Face** hosts the container
but does **not** supply a model key, so you also need a **model provider**. The
fewest-signups default below uses **Google Gemini** — its key comes from Google AI Studio
with your existing Google account, and the free tier is generous.

**1. Create the Space** — New → Space → **Docker** (blank template), then name it.
Requires a free [Hugging Face account](https://huggingface.co/join).

**2. Push this repo to the Space** — either add the Space as a git remote and push by
hand, or let the bundled GitHub Action do it on every push (see
[Auto-sync from GitHub](#auto-sync-from-github) below):

```bash
git remote add space https://huggingface.co/spaces/<you>/<space-name>
git push space main
```

**3. Set Secrets** — Space → Settings → *Variables and secrets*. **Never commit `.env`**;
the Dockerfile reads config from the environment the Space injects:

| Secret | Value |
|---|---|
| `GTM_MODEL` | `gemini/gemini-2.5-flash` |
| `GEMINI_API_KEY` | a free key from [AI Studio](https://aistudio.google.com/apikey) |

The Space rebuilds and boots on `7860`. The free tier **sleeps after inactivity** and
wakes on the next visit (first load takes a few seconds).

### Auto-sync from GitHub

`.github/workflows/sync-to-hf-space.yml` mirrors this repo into the Space on every push
to `main`/`master` (and on demand via *Actions → Run workflow*), so the Space rebuilds
itself and GitHub stays the single source of truth. Configure it once, in the **GitHub**
repo under *Settings → Secrets and variables → Actions*:

| Kind | Name | Value |
|---|---|---|
| Variable | `HF_SPACE` | `<owner>/<space-name>` — the Space's path |
| Variable | `HF_USER` | your Hugging Face username (the token's owner) |
| Secret | `HF_TOKEN` | an HF access token with **write** scope ([settings/tokens](https://huggingface.co/settings/tokens)) |

> `HF_TOKEN` here is a *GitHub* secret used only to push to the Space — unrelated to the
> `HF_TOKEN` *Space* secret you'd set for HF Inference under
> [Model backends](#model-backends-either-host) below.

**While `HF_SPACE`/`HF_USER` are unset the job skips**, so hosting on Render alone won't
leave a failed run on every push. That also makes a Space a one-step fallback: add the two
variables and the secret, and mirroring resumes on the next push.

Once configured, the workflow refuses to push if the Space front-matter is missing or
disagrees with the Dockerfile's port, or if anything that looks like a real secret
(`.env`, `*.pem`, `playbooks/private/`) has been committed — a Space can be public.

The sync is a **force push**: the Space mirrors this repo, so edits made in the Space's web
UI get overwritten on the next push. Change things here, not there.

### Model backends (either host)

Same image on Render or a Space — only the env vars change:

- **Groq** (hosted open Llama models, free tier): `GTM_MODEL=groq/llama-3.3-70b-versatile`,
  `GROQ_API_KEY=…` from [console.groq.com/keys](https://console.groq.com/keys) — needs a
  separate Groq signup.
- **Anthropic Claude** (best quality, paid): `GTM_MODEL=anthropic/claude-sonnet-4-20250514`, `ANTHROPIC_API_KEY=…`.
- **HF Inference** (open models, uses your HF account): `GTM_MODEL=huggingface/<repo-id>`,
  `HF_TOKEN=…` — pick a model with reliable function-calling, or delegation may misfire.

> Upgrade path: a paid GPU Space (or your own box) can run the open weights directly via
> Ollama — set `GTM_MODEL=ollama_chat/<tag>` and `GTM_LOCAL_BASE_URL`. The same image also
> runs anywhere Docker does: `docker build -t gtm-agent . && docker run -p 7860:7860 -e GTM_MODEL=… -e GEMINI_API_KEY=… gtm-agent`.

## License

MIT — see [LICENSE](LICENSE).
