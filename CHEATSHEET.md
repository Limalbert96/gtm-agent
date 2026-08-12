# GTM Hub — Cheatsheet

Everything you need to run this day-to-day. **Paste commands one line at a time.
Never include a `# comment` on a command line** — zsh passes `#` as an argument and
breaks npm / vite / cd / uvicorn.

Repo root: `~/Documents/alim_workspace/gtm-agent`

---

## Start the app (the GTM Hub UI)

The frontend is already built, so day-to-day you only start the backend:

```bash
cd ~/Documents/alim_workspace/gtm-agent
```
```bash
uvicorn web.server:app --reload --port 8000
```

Open **http://localhost:8000**. Stop it with `Ctrl-C`. Restart it whenever you
change `.env` (it reads the model config at startup).

### Rebuild the frontend (only after changing UI code)

```bash
cd ~/Documents/alim_workspace/gtm-agent/web/frontend
```
```bash
npm run build
```

Reload the page. (`npm install` is only needed the first time or after dependency
changes. For live hot-reload while editing UI, use `npm run dev` on `:5173`.)

---

## Local AI (Ollama)

Ollama runs as a **background service** — you do **not** start it. An
`address already in use` on `:11434` just means it's already up.

```bash
ollama list          # models you have on disk
ollama ps            # models loaded in RAM right now (empty until a chat hits)
ollama run qwen3     # chat directly in the terminal to test a model (/bye to exit)
ollama stop qwen3    # unload from RAM now (auto-unloads after ~5 min idle)
ollama rm qwen3:32b  # delete a model from disk
```

---

## Switch which model the app uses

The model is set by **`GTM_MODEL` in `.env`** (not by Ollama). Edit it, then
restart uvicorn. The string after `ollama_chat/` must match an `ollama list` tag.

| Backend | `.env` line |
|---|---|
| Local Qwen 8B (current) | `GTM_MODEL=ollama_chat/qwen3` |
| Local Qwen 32B (better at delegation) | `GTM_MODEL=ollama_chat/qwen3:32b` |
| Local Qwen coder | `GTM_MODEL=ollama_chat/qwen3-code` |
| Hosted Claude | `GTM_MODEL=anthropic/claude-sonnet-4-20250514` + real `ANTHROPIC_API_KEY` |
| Google Gemini | `GTM_MODEL=gemini/gemini-2.5-pro` + `GEMINI_API_KEY` |

For local models also keep `GTM_LOCAL_BASE_URL=http://localhost:11434` (no `/v1`,
no trailing comment). Switching to a non-`anthropic/` model auto-bypasses the
internal gateway. To go back to gateway Claude, restore the
`GTM_USE_INTERNAL_GATEWAY` / `GTM_KEY_COMMAND` / `GTM_BASE_URL` lines.

### Confirm which model is live

```bash
curl -s localhost:8000/api/meta
```

Should report `"model":"ollama_chat/qwen3"`. It's also shown in the UI sidebar
footer. If it's wrong, uvicorn didn't reload — `Ctrl-C` and start it again.

---

## ADK dev UI (optional — for debugging agent hand-offs)

Separate app on `:8001`. Use it to watch whether `transfer_to_agent` fires as a
real tool call or leaks out as text.

```bash
cd ~/Documents/alim_workspace/gtm-agent
```
```bash
python3 -m google.adk.cli web --port 8001
```

Open **http://localhost:8001**, pick `gtm_agent`. (`adk web` also works if the
shortcut is on your PATH.) Not needed to run the GTM Hub UI.

---

## Troubleshooting

- **`EINVALIDTAGNAME` / `Could not resolve entry module "#/index.html"` / `cd: too
  many arguments`** — you pasted a `# comment` on a command line. Remove it.
- **`ModuleNotFoundError: No module named 'web'`** — you ran uvicorn from the wrong
  folder. `cd` to the repo root first.
- **Chat stalls with a literal `transfer_to_agent(agent_name="...")` bubble** — the
  local model failed to make the delegation tool call. Try `qwen3:32b`, or ask to
  make coordinator routing explicit in `agent.py`.
- **UI still shows the old model after editing `.env`** — restart uvicorn.
- **Broken `GTM_LOCAL_BASE_URL`** — remove any trailing `# comment`; the web
  server's `.env` reader keeps it as part of the value.

---

## Sanity check without a key or network

```bash
python validate_offline.py
```
