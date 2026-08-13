import AgentBadge from "./AgentBadge.jsx";
import { roleForAgent } from "../roles.js";

// One turn in the transcript. User messages sit right in a filled blue bubble;
// assistant messages sit left in a soft dark bubble. A role badge appears only
// when the coordinator delegated to a specialist (Sales / Pre-sales / CS), so
// the default coordinator chat stays clean while delegation still surfaces.
// Optional `actions` render as inline buttons under an assistant message. Each is
// either a plain string, or `{ label, prompt }` — where `prompt` is what gets sent
// to the agent. Prefer the object form: a label like "Yes, draft it" is meaningless
// on its own, and the agent only ever receives the message we send (seeded demo
// turns live in React state and are never transmitted), so a bare label arrives
// with nothing for "it" to refer to.
export default function Message({ role, text, agent, pending, actions, onAction }) {
  if (role === "user") {
    return (
      <div className="msg msg-user">
        <div className="bubble bubble-user">{text}</div>
      </div>
    );
  }

  const r = roleForAgent(agent);
  const showBadge = agent && agent !== "gtm_coordinator";

  return (
    <div className="msg msg-assistant">
      {showBadge && (
        <div className="msg-head">
          <AgentBadge agent={agent} />
        </div>
      )}
      <div
        className="bubble bubble-assistant"
        style={showBadge ? { borderLeft: `3px solid ${r.accent}` } : undefined}
      >
        {text ? (
          <div className="prose">{text}</div>
        ) : pending ? (
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
