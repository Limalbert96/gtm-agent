import Icon from "./Icons.jsx";
import { VALIDATIONS, SA_UTILIZATION, CRITERIA_TEMPLATES } from "../demoData.js";

// Pre-sales workspace — the "Solution Dashboard": active POV/validation tracking
// on the left, solutions-architect utilization and reusable criteria templates
// on the right. Static demo content (see demoData.js).
export default function PresalesView() {
  return (
    <div className="view">
      <div className="view-head">
        <div>
          <h1 className="view-title">Solution Dashboard</h1>
          <p className="view-sub">Active Proof of Concepts &amp; Resource Allocation</p>
        </div>
        <div className="view-actions">
          <button className="btn btn-ghost">Export Report</button>
          <button className="btn btn-primary">
            <Icon name="plus" size={16} /> New POC
          </button>
        </div>
      </div>

      <div className="grid grid-main">
        <section className="card">
          <div className="card-head">
            <h2 className="card-title">
              <Icon name="rocket" size={18} className="accent-blue" /> Active Validations
            </h2>
            <a className="card-link" href="#validations">View All</a>
          </div>

          <table className="table">
            <thead>
              <tr>
                <th>Account / Deal</th>
                <th>Phase</th>
                <th>Health</th>
                <th>Architect</th>
                <th className="ta-right">Target Close</th>
              </tr>
            </thead>
            <tbody>
              {VALIDATIONS.map((v) => (
                <tr key={v.account}>
                  <td>
                    <div className="cell-strong">{v.account}</div>
                    <div className="cell-sub">
                      <Icon name="link" size={13} /> {v.deal}
                    </div>
                  </td>
                  <td>
                    <span className="pill">{v.phase}</span>
                  </td>
                  <td>
                    <span className={`status status-${v.healthTone}`}>
                      <Icon
                        name={v.healthTone === "ok" ? "check" : v.healthTone === "warn" ? "warn" : "clock"}
                        size={15}
                      />
                      {v.health}
                    </span>
                  </td>
                  <td>
                    <span className="owner">
                      <span className={`avatar-sm avatar-${v.avatar}`}>{v.initials}</span>
                      {v.architect}
                    </span>
                  </td>
                  <td className="ta-right cell-mono">{v.close}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <div className="col-stack">
          <section className="card">
            <div className="card-head">
              <h2 className="card-title">
                <Icon name="users" size={18} className="accent-blue" /> SA Utilization
              </h2>
            </div>
            <div className="util-list">
              {SA_UTILIZATION.map((s) => (
                <div className="util-row" key={s.name}>
                  <div className="util-head">
                    <span className="util-name">
                      {s.name} <span className="util-count">({s.active} Active)</span>
                    </span>
                    <span className="util-pct">{s.pct}%</span>
                  </div>
                  <div className="bar">
                    <span
                      className={`bar-fill ${s.pct >= 75 ? "bar-blue" : "bar-green"}`}
                      style={{ width: `${s.pct}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="card">
            <div className="card-head">
              <h2 className="card-title">
                <Icon name="doc" size={18} className="accent-blue" /> Criteria Templates
              </h2>
              <button className="icon-round" aria-label="Add template">
                <Icon name="plus" size={16} />
              </button>
            </div>
            <div className="template-list">
              {CRITERIA_TEMPLATES.map((t) => (
                <div className="template" key={t.title}>
                  <div className="template-title">{t.title}</div>
                  <div className="template-body">{t.body}</div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
