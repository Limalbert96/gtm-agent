# Per-agent transcript for the GTM Coordinator chat

**Date:** 2026-08-13
**Status:** Approved, ready for implementation
**Scope:** `web/server.py`, `web/frontend/src/` — Coordinator view only

## Problem

A multi-agent turn renders as one undifferentiated wall of text. Asking

> "Meridian Health is At Risk with 5 days left: the technical get-well plan, the
> commercial impact if it slips a quarter, and the adoption risk we inherit if we win it
> anyway."

produces a single bubble, badged with whichever agent happened to answer last, opening
with the model's internal deliberation ("Okay, let me process this…") and rendering
`**bold**` and `###` as literal characters. Three separate defects, plus a fourth: there
is no signal that the turn has finished beyond the typing dots stopping.

### Root causes

| Symptom | Cause |
|---|---|
| Wall of text, literal `**` / `###` | `Message.jsx` renders `{text}` as a text node; no markdown parsing |
| All agents merge into one bubble | `stream_turn` emits `("agent", name)` on author change, but `App.jsx`'s `onAgent` calls `patchLast({agent})` — relabelling the *same* bubble while deltas keep appending |
| Reasoning leaks into the answer | ADK marks reasoning as `types.Part(text=…, thought=True)`; `_event_text()` concatenates every text part without checking the flag |
| No completion signal | Only the pending/typing indicator conveys state |

The third is a server bug, not a model quirk — the reasoning is cleanly separable.

## Decisions

1. **One bubble per agent.** Each contribution gets its own message, badge and accent.
2. **Reasoning in a collapsed `▸ Reasoning` disclosure**, per bubble — dropped from the
   answer body but still inspectable.
3. **Per-agent status plus a live status strip** above the composer naming who is working.

## Approach

Considered three splits of responsibility:

- **A — client infers boundaries.** Smallest change, but the client must time durations
  with its own clock and can't distinguish "finished" from "paused mid-stream."
- **B — server frames messages** with explicit `message_start`/`message_end`. Cleanest,
  but a larger protocol rewrite than the problem warrants.
- **C — server owns timing, client owns layout.** *Chosen.* Boundaries come from the
  existing `agent` event; the server adds `thought` and `agent_done {agent, ms}`. The
  server sits in the ADK event loop and knows real durations.

## Protocol

SSE events from `POST /api/chat/stream`:

| Event | Payload | Meaning |
|---|---|---|
| `agent` | `name` | New agent active → **message boundary** |
| `delta` | text | Append to the current bubble's answer |
| `replace` | text | Replace the current bubble's answer |
| `thought` | text | Append to the current bubble's reasoning |
| `agent_done` | `{agent, ms}` | That agent finished, with its duration |
| `final` | `{reply, agent}` | Turn complete |
| `error` | `{message}` | Failure; patches the active bubble only |

`thought` and `agent_done` are new. Existing events are unchanged, so an old client
degrades to current behaviour rather than breaking.

## Server changes (`web/server.py`)

- `_parts_text(event, *, thought)` — shared extractor filtering on `Part.thought`.
- `_event_text()` returns answer text only; `_event_thought()` returns reasoning.
- `stream_turn()`:
  - resets `sent` / `sent_thought` on agent change, so a new bubble starts empty;
  - emits `agent_done` for the outgoing agent before `agent` for the incoming one, and
    once more after the loop for the last agent;
  - suppresses `agent_done` for an agent that produced no answer and no reasoning, so an
    empty bubble never shows a duration.

## Client changes

- **`api.js`** — dispatch `thought` and `agent_done` to `onThought` / `onAgentDone`.
- **`App.jsx`** — `onAgent` **appends** a new assistant message instead of patching.
  Assistant entries become `{role, agent, text, thought, pending, durationMs}`.
  New `activeAgent` state drives the status strip; cleared on `final` and on error.
- **`Message.jsx`** — markdown rendering; a collapsed disclosure when `thought` is
  non-empty; per-bubble status (dots while pending → `✓ 6.2s`).
- **`CoordinatorView.jsx`** — status strip above the composer: `● Sales is working…`.
- **`styles.css`** — styles for the disclosure, per-bubble status, status strip, and
  markdown elements inside `.prose` (headings, lists, tables, code).

### Markdown

Add `react-markdown` + `remark-gfm`. The agents emit headings, bold, nested lists and
tables; a partial hand-rolled renderer would read worse than today's plain text until it
handled all of them. Cost ~40–50KB gzipped against a 56KB bundle.

## Data flow

```
user sends
  └─ coordinator bubble (pending)
       agent: presales_agent   → new bubble
       thought…                → collapsed block fills
       delta…                  → answer body fills
       agent_done {6200ms}     → bubble settles, ✓ 6.2s
       agent: sales_agent      → new bubble
       …
  final                        → status strip clears
```

## Error handling

- `error` patches only the active bubble; earlier completed bubbles are untouched.
- A stream that dies without `agent_done` is settled by `final` or stream close, so no
  bubble spins forever.
- Abort (navigation, cancel) marks pending bubbles interrupted rather than spinning.

## Edge cases

- **Coordinator answers alone** — a single plain bubble, no badge, no extra chrome.
- **Same agent active twice in one turn** — a second bubble, not a reopened first one.
  Simpler, and honest about what happened.
- **Reasoning with no answer** — bubble shows the disclosure and no body.
- **Seeded demo messages** (`COORDINATOR_SEED`) carry no `thought`/`durationMs`; the
  component must treat both as optional.

## Testing

The repo has no JS test framework, so:

- A node script replaying a recorded SSE fixture through the reducer, asserting three
  bubbles with the expected agents, bodies and reasoning separation.
- A `validate_offline.py` check for `_event_text` / `_event_thought` against stub parts —
  both are pure functions.
- `npm run build` for compilation, then manual verification against the running app.

## Out of scope

- Tool-call activity trail (considered and declined).
- The three static dashboard views (Sales / Pre-Sales / Customer Success).
- Any change to model selection, quota handling, or telemetry.
