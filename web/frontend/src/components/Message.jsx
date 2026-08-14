import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import AgentBadge from "./AgentBadge.jsx";
import { roleForAgent } from "../roles.js";

// One turn in the transcript. User messages sit right in a filled blue bubble;
// assistant messages sit left in a soft dark bubble. A role badge appears only
// when the coordinator delegated to a specialist (Sales / Pre-sales / CS), so
// the default coordinator chat stays clean while delegation still surfaces.
//
// A multi-agent turn produces one Message per agent (App.jsx starts a new one on
// each "agent" event), so each bubble carries exactly one agent's contribution:
//   `thought`     -- that agent's reasoning, behind a collapsed disclosure
//   `durationMs`  -- how long it took, measured server-side
//   `pending`     -- still streaming; shows a live indicator instead
//
// Optional `actions` render as inline buttons under an assistant message. Each is
// either a plain string, or `{ label, prompt }` -- where `prompt` is what gets sent
// to the agent. Prefer the object form: a label like "Yes, draft it" is meaningless
// on its own, and the agent only ever receives the message we send (seeded demo
// turns live in React state and are never transmitted), so a bare label arrives
// with nothing for "it" to refer to.
export default function Message({
  role,
  text,
  agent,
  pending,
  thought,
  durationMs,
  actions,
  onAction,
}) {
  const [showReasoning, setShowReasoning] = useState(false);

  if (role === "user") {
    return (
      <div className="msg msg-user">
        <div className="bubble bubble-user">{text}</div>
      </div>
    );
  }

  const r = roleForAgent(agent);
  // Badge every assistant message, coordinator included. It used to be hidden for
  // the coordinator to keep ordinary chat clean, but the coordinator also frames
  // multi-specialist answers -- and an unbadged bubble sitting under three badged
  // ones reads as "no idea who is talking to me".
  const showBadge = Boolean(agent);
  const duration = formatDuration(durationMs);

  // An agent that reasoned but never answered -- typically the coordinator working
  // out where to route. A full bubble with nothing inside it reads as a bug, so
  // collapse it to one line that still accounts for the time and keeps the
  // reasoning reachable.
  if (!text && !pending && (thought || duration)) {
    return (
      <div className="msg msg-assistant">
        <div className="msg-aside">
          <span className="msg-aside-role" style={{ color: r.accent }}>
            {r.label}
          </span>
          <span>deliberated{duration ? ` · ${duration}` : ""}</span>
          {thought ? (
            <button
              type="button"
              className="reasoning-toggle"
              onClick={() => setShowReasoning((v) => !v)}
              aria-expanded={showReasoning}
            >
              {showReasoning ? "▾" : "▸"} Reasoning
            </button>
          ) : null}
        </div>
        {thought && showReasoning ? (
          <div className="reasoning-body">{thought}</div>
        ) : null}
      </div>
    );
  }
  // The head row carries attribution on the left and this agent's state on the
  // right, so you can tell at a glance who is speaking and whether they're done.
  const showHead = showBadge || pending || duration;

  return (
    <div className="msg msg-assistant">
      {showHead && (
        <div className="msg-head">
          {showBadge ? <AgentBadge agent={agent} /> : <span />}
          {pending ? (
            <span className="msg-status msg-status-live" aria-label="Still answering">
              <span />
              <span />
              <span />
            </span>
          ) : duration ? (
            <span className="msg-status">✓ {duration}</span>
          ) : null}
        </div>
      )}
      <div
        className="bubble bubble-assistant"
        style={showBadge ? { borderLeft: `3px solid ${r.accent}` } : undefined}
      >
        {thought ? (
          <div className="reasoning">
            <button
              type="button"
              className="reasoning-toggle"
              onClick={() => setShowReasoning((v) => !v)}
              aria-expanded={showReasoning}
            >
              {showReasoning ? "▾" : "▸"} Reasoning
            </button>
            {showReasoning ? <div className="reasoning-body">{thought}</div> : null}
          </div>
        ) : null}

        {text ? (
          <div className="prose">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
          </div>
        ) : pending && !thought ? (
          <div className="typing" aria-label="Assistant is thinking">
            <span />
            <span />
            <span />
          </div>
        ) : null}

        {actions?.length ? (
          <div className="msg-actions">
            {actions.map((a, i) => {
              const label = typeof a === "string" ? a : a.label;
              const prompt = typeof a === "string" ? a : a.prompt || a.label;
              return (
                <button
                  key={label}
                  className={`msg-action${i === 0 ? " msg-action-primary" : ""}`}
                  onClick={() => onAction?.(prompt)}
                >
                  {label}
                </button>
              );
            })}
          </div>
        ) : null}
      </div>
    </div>
  );
}

// Sub-second answers read better in ms; anything longer in seconds.
function formatDuration(ms) {
  if (ms == null) return null;
  return ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(1)}s`;
}
