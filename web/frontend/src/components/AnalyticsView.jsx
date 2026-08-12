import Icon from "./Icons.jsx";
import {
  ANALYTICS_KPIS,
  PIPELINE_BY_STAGE,
  ARR_BY_CUSTOMER,
  HEALTH_DISTRIBUTION,
  FUNNEL,
} from "../demoData.js";

// Analytics workspace — a cross-role reporting surface rolled up over the same
// account roster the other views use (see demoData.js). Illustrative demo data;
// wire it to your warehouse or the agent's reporting tools for live numbers.
export default function AnalyticsView() {
  const healthTotal = HEALTH_DISTRIBUTION.reduce((s, h) => s + h.count, 0);

  return (
    <div className="view">
      <div className="view-head">
        <div>
          <h1 className="view-title">Analytics</h1>
          <p className="view-sub">Cross-role GTM reporting across all 8 accounts.</p>
        </div>
        <div className="view-actions">
          <button className="btn btn-ghost">
            <Icon name="calendar" size={15} /> This Quarter
          </button>
          <button className="btn btn-primary">
            <Icon name="doc" size={16} /> Export
          </button>
        </div>
      </div>

      <div className="kpi-row">
        {ANALYTICS_KPIS.map((k) => (
          <div className="kpi-card" key={k.label}>
            <div className="kpi-head">
              <span className="kpi-label">{k.label}</span>
              <Icon name={k.icon} size={18} className="kpi-icon" />
            </div>
            <div className="kpi-value">
              {k.value}
              {k.unit && <span className="kpi-unit"> {k.unit}</span>}
            </div>
            <div className={`kpi-sub ${k.tone === "up" ? "up" : "muted"}`}>{k.sub}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-main">
        <section className="card">
          <div className="card-head">
            <h2 className="card-title">
              <Icon name="bars" size={18} className="accent-blue" /> Pipeline by Stage
            </h2>
            <span className="chip chip-info">$3.0M open</span>
          </div>
          <div className="metric-list">
            {PIPELINE_BY_STAGE.map((s) => (
              <div className="metric-row" key={s.stage}>
                <span className="metric-name">
                  {s.stage} <span className="muted">· {s.count} deals</span>
                </span>
                <span className="metric-val">{s.value}</span>
                <div className="bar">
                  <span className={`bar-fill bar-${s.bar}`} style={{ width: `${s.pct}%` }} />
                </div>
              </div>
            ))}
          </div>

          <div className="card-divider" />

          <div className="card-head">
            <h2 className="card-title">
              <Icon name="filter" size={18} className="accent-blue" /> GTM Funnel
            </h2>
          </div>
          <div className="funnel">
            {FUNNEL.map((f) => (
              <div className="funnel-row" key={f.stage}>
                <span className="funnel-label">{f.stage}</span>
                <div className="funnel-track">
                  <span className="funnel-fill" style={{ width: `${f.pct}%` }}>
                    {f.count}
                  </span>
                </div>
                <span className="funnel-pct muted">{f.pct}%</span>
              </div>
            ))}
          </div>
        </section>

        <div className="col-stack">
          <section className="card">
            <div className="card-head">
              <h2 className="card-title">
                <Icon name="heart" size={18} className="accent-green" /> Portfolio Health
              </h2>
              <span className="chip chip-ok">{healthTotal} accounts</span>
            </div>
            <div className="stacked">
              {HEALTH_DISTRIBUTION.map((h) => (
                <span
                  key={h.band}
                  className={`seg-${h.seg}`}
                  style={{ width: `${(h.count / healthTotal) * 100}%` }}
                  title={`${h.band}: ${h.count}`}
                />
              ))}
            </div>
            <div className="legend-row">
              {HEALTH_DISTRIBUTION.map((h) => (
                <span className="legend-item" key={h.band}>
                  <span className={`legend-dot seg-${h.seg}`} />
                  {h.band} ({h.count})
                </span>
              ))}
            </div>
          </section>

          <section className="card">
            <div className="card-head">
              <h2 className="card-title">
                <Icon name="dollar" size={18} className="accent-blue" /> ARR by Customer
              </h2>
            </div>
            <div className="metric-list">
              {ARR_BY_CUSTOMER.map((a) => (
                <div className="metric-row" key={a.name}>
                  <span className="metric-name">{a.name}</span>
                  <span className="metric-val">{a.value}</span>
                  <div className="bar">
                    <span className={`bar-fill bar-${a.bar}`} style={{ width: `${a.pct}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
