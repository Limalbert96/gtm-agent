import { useState } from "react";
import Icon from "./Icons.jsx";
import { SALES_KPIS, SALES_AGENT_INSIGHT, SALES_COLUMNS } from "../demoData.js";

// Sales workspace — "GTM Intelligence" deal board: a KPI strip (with an agent
// insight card) over a stage-based kanban of live deals. Static demo content.
export default function SalesView() {
  const [tab, setTab] = useState("board");

  return (
    <div className="view">
      <div className="view-head">
        <div className="head-titles">
          <h1 className="view-title">GTM Intelligence</h1>
          <div className="tabs">
            <button
              className={`tab${tab === "board" ? " tab-active" : ""}`}
              onClick={() => setTab("board")}
            >
              Deal Board
            </button>
            <button
              className={`tab${tab === "forecast" ? " tab-active" : ""}`}
              onClick={() => setTab("forecast")}
            >
              Forecast
            </button>
          </div>
        </div>
      </div>

      <div className="kpi-row">
        {SALES_KPIS.map((k) => (
          <div className="kpi-card" key={k.label}>
            <div className="kpi-head">
              <span className="kpi-label">{k.label}</span>
              <Icon name={k.icon} size={18} className="kpi-icon" />
            </div>
            <div className="kpi-value">
              {k.value}
              {k.unit && <span className="kpi-unit"> {k.unit}</span>}
            </div>
            {k.bar != null ? (
              <div className="kpi-foot">
                <div className="bar">
                  <span className="bar-fill bar-green" style={{ width: `${k.bar}%` }} />
                </div>
                <span className="kpi-sub muted">{k.sub}</span>
              </div>
            ) : (
              <div className={`kpi-sub ${k.tone === "up" ? "up" : "muted"}`}>{k.sub}</div>
            )}
          </div>
        ))}
        <div className="kpi-card kpi-insight">
          <div className="kpi-head">
            <span className="kpi-label">
              <Icon name="spark" size={15} className="accent-blue" /> Agent Insight
            </span>
          </div>
          <p className="insight-text">{SALES_AGENT_INSIGHT}</p>
        </div>
      </div>

      {tab === "board" ? (
        <div className="board">
          {SALES_COLUMNS.map((col) => (
            <section className="board-col" key={col.key}>
              <div className="board-col-head">
                <span className="board-col-name">
                  <span className={`dot dot-${col.dot}`} />
                  {col.name}
                  <span className="count">{col.count}</span>
                </span>
                <span className="board-col-total">{col.total}</span>
              </div>
              <div className="board-col-body">
                {col.deals.map((d) => (
                  <div
                    className={`deal${d.highlight ? " deal-hot" : ""}`}
                    key={d.name}
                  >
                    <div className="deal-top">
                      <span className="deal-name">
                        <span className="code">{d.code}</span>
                        {d.name}
                      </span>
                      {d.agent && <Icon name="spark" size={15} className="accent-blue" />}
                    </div>
                    <div className="deal-amount">{d.amount}</div>
                    {d.tags && (
                      <div className="deal-tags">
                        {d.tags.map((t, i) => (
                          <span className={`tag${i === 0 ? " tag-strong" : ""}`} key={t}>
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                    {d.progress != null && (
                      <div className="deal-progress">
                        <div className="bar">
                          <span className="bar-fill bar-blue" style={{ width: `${d.progress}%` }} />
                        </div>
                        <span className="deal-progress-pct">{d.progress}%</span>
                      </div>
                    )}
                    <div className="deal-foot">
                      <span className="owner">
                        <span className="avatar-sm avatar-slate">
                          {d.owner.split(" ").map((w) => w[0]).join("").slice(0, 2)}
                        </span>
                        {d.owner}
                      </span>
                      {d.status ? (
                        <span className={`status status-${d.statusTone}`}>
                          <Icon name={d.statusTone === "ok" ? "check" : "warn"} size={14} />
                          {d.status}
                        </span>
                      ) : (
                        <span className="deal-due">
                          <Icon name="calendar" size={13} /> {d.due}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          ))}
        </div>
      ) : (
        <div className="placeholder">
          <Icon name="trend" size={26} />
          <p>Forecast view — pipeline projection and weighted commit land here.</p>
        </div>
      )}
    </div>
  );
}
