import Icon from "./Icons.jsx";
import { CS_STATS, PRIORITY_ACCOUNTS, CS_PLAYBOOKS } from "../demoData.js";

const bandTone = { Poor: "bad", Fair: "warn", Good: "ok" };

// Customer Success workspace — the "CS Health Center": portfolio health,
// renewal risk and growth up top; a priority-accounts table and AI-suggested
// playbooks below. Static demo content.
export default function CSView() {
  const { portfolioHealth, renewalRisk, accountGrowth } = CS_STATS;

  return (
    <div className="view">
      <div className="view-head">
        <div>
          <h1 className="view-title">CS Health Center</h1>
          <p className="view-sub">
            Monitor account health, mitigate renewal risks, and identify expansion paths.
          </p>
        </div>
        <div className="view-actions">
          <button className="btn btn-ghost">
            <Icon name="filter" size={15} /> Filter
          </button>
        </div>
      </div>

      <div className="stat-row">
        <div className="card stat-card">
          <div className="card-head">
            <h2 className="card-title">
              <Icon name="trend" size={18} className="accent-green" /> Portfolio Health
            </h2>
            <span className="chip chip-ok">{portfolioHealth.delta}</span>
          </div>
          <div className="stat-big">
            {portfolioHealth.score}
            <span className="stat-unit"> / 100 Avg Score</span>
          </div>
          <div className="bar bar-gradient" />
          <div className="bar-legend">
            <span>Healthy</span>
            <span>At Risk</span>
          </div>
        </div>

        <div className="card stat-card">
          <div className="card-head">
            <h2 className="card-title">
              <Icon name="warn" size={18} className="accent-red" /> Renewal Risk
            </h2>
          </div>
          <div className="stat-big stat-red">{renewalRisk.arr}</div>
          <div className="stat-sub muted">{renewalRisk.sub}</div>
          <div className="risk-list">
            {renewalRisk.accounts.map((a) => (
              <div className="risk-row" key={a.name}>
                <span>{a.name}</span>
                <span className="risk-amt">{a.amount}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card stat-card">
          <div className="card-head">
            <h2 className="card-title">
              <Icon name="trend" size={18} className="accent-blue" /> Account Growth
            </h2>
            <Icon name="spark" size={16} className="accent-blue" />
          </div>
          <div className="stat-big">{accountGrowth.count}</div>
          <div className="stat-sub muted">{accountGrowth.sub}</div>
          <button className="btn btn-outline full">Review Opportunities</button>
        </div>
      </div>

      <div className="grid grid-main">
        <section className="card">
          <div className="card-head">
            <h2 className="card-title">Priority Accounts</h2>
            <a className="card-link" href="#accounts">
              View All <Icon name="arrow" size={14} />
            </a>
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>Account</th>
                <th>Health</th>
                <th>Last Touch</th>
                <th>Renewal</th>
                <th className="ta-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {PRIORITY_ACCOUNTS.map((a) => (
                <tr key={a.name}>
                  <td>
                    <div className="cell-strong">{a.name}</div>
                    <div className="cell-sub">{a.tier}</div>
                  </td>
                  <td>
                    <span className={`health health-${bandTone[a.band]}`}>
                      <span className="health-dot" />
                      {a.band} ({a.score})
                    </span>
                  </td>
                  <td>
                    <div className="cell-strong-sm">{a.lastTouch}</div>
                    <div className={`cell-sub ${a.lastTone === "warn" ? "warn" : ""}`}>
                      {a.lastKind}
                    </div>
                  </td>
                  <td className="cell-mono">{a.renewal}</td>
                  <td className="ta-right">
                    <button className="dots" aria-label="Actions">⋯</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <div className="col-stack">
          <section className="card">
            <div className="card-head">
              <h2 className="card-title">
                <Icon name="book" size={18} className="accent-blue" /> Suggested Playbooks
              </h2>
              <span className="chip chip-info">AI Triggered</span>
            </div>
            <div className="pb-list">
              {CS_PLAYBOOKS.map((p) => (
                <div className="pb" key={p.title}>
                  <div className="pb-head">
                    <span className="pb-title">{p.title}</span>
                    <button className="icon-round sm" aria-label="Run playbook">
                      <Icon name="play" size={16} />
                    </button>
                  </div>
                  <div className="pb-body">{p.body}</div>
                  <div className="pb-tags">
                    {p.tags.map((t) => (
                      <span className={`tag tag-${t.tone}`} key={t.label}>
                        {t.label}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            <button className="btn btn-outline full">View Playbook Library</button>
          </section>
        </div>
      </div>
    </div>
  );
}
