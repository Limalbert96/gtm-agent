import { useEffect, useRef } from "react";
import Icon from "./Icons.jsx";
import Message from "./Message.jsx";
import Composer from "./Composer.jsx";
import { STRATEGIC_OVERVIEW, NEXT_STEPS } from "../demoData.js";
import { roleForAgent } from "../roles.js";

// GTM Coordinator workspace — the one *functional* view: the real streaming ADK
// assistant ("ADK Intelligence"), flanked by a Strategic Overview + Next Steps
// rail (static demo). The coordinator delegates to the specialist agents; when
// one answers, its role badge appears on that message.
export default function CoordinatorView({
  messages,
  busy,
  activeAgent,
  onSend,
  onAction,
  attachment,
  onAttach,
  onClearAttachment,
}) {
  const scrollRef = useRef(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, busy]);

  return (
    <div className="view coordinator">
      <div className="view-head">
        <div className="head-titles">
          <h1 className="view-title">
            Coordinator Workspace
            <span className="chip chip-info chip-glow">
              <Icon name="spark" size={14} /> ADK Active
            </span>
          </h1>
          <p className="view-sub">Overview of GTM alignment and active automations.</p>
        </div>
        <div className="view-actions">
          <button className="btn btn-ghost">Export Report</button>
        </div>
      </div>

      <div className="coord-grid">
        <section className="card chat-card">
          <div className="agent-head">
            <div className="agent-avatar">
              <Icon name="robot" size={22} />
            </div>
            <div>
              <div className="agent-name">ADK Intelligence</div>
              <div className="agent-role">GTM Insights &amp; Automation Agent</div>
            </div>
          </div>

          <div className="transcript" ref={scrollRef}>
            <div className="messages">
              {messages.map((m, i) => (
                <Message
                  key={i}
                  role={m.role}
                  text={m.text}
                  agent={m.agent}
                  pending={m.pending}
                  thought={m.thought}
                  durationMs={m.durationMs}
                  actions={m.actions}
                  onAction={onAction}
                />
              ))}
            </div>
          </div>

          {/* Who is answering right now. A three-role turn can take half a minute,
              so naming the working agent is the difference between "thinking" and
              "stuck". Cleared when the turn ends. */}
          {activeAgent ? (
            <div className="agent-status" aria-live="polite">
              <span
                className="agent-status-dot"
                style={{ background: roleForAgent(activeAgent).accent }}
              />
              {roleForAgent(activeAgent).label} is working…
            </div>
          ) : null}

          <Composer
            onSend={onSend}
            disabled={busy}
            attachment={attachment}
            onAttach={onAttach}
            onClearAttachment={onClearAttachment}
            placeholder="Ask ADK for insights, commands, or data…"
          />
        </section>

        <aside className="coord-rail">
          <section className="card">
            <div className="card-head">
              <h2 className="card-title">Strategic Overview</h2>
              <Icon name="trend" size={18} className="accent-blue" />
            </div>
            <div className="overview-list">
              {STRATEGIC_OVERVIEW.map((o) => (
                <div className="overview-row" key={o.label}>
                  <div className="overview-head">
                    <span className="overview-label">{o.label}</span>
                    <span className={`overview-delta tone-${o.tone}`}>{o.delta}</span>
                  </div>
                  <div className="bar">
                    <span className={`bar-fill bar-${o.bar}`} style={{ width: `${o.pct}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="card">
            <div className="card-head">
              <h2 className="card-title">
                Next Steps <span className="count count-alert">{NEXT_STEPS.length}</span>
              </h2>
            </div>
            <div className="steps-list">
              {NEXT_STEPS.map((s) => (
                <div className="step" key={s.title}>
                  <Icon name="radio" size={18} className="step-radio" />
                  <div>
                    <div className="step-title">{s.title}</div>
                    <div className={`step-meta ${s.tone === "warn" ? "warn" : "muted"}`}>
                      {s.meta}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}
