import Icon from "./Icons.jsx";

// Left rail of the GTM Hub shell: brand, the primary "New Deal" action, the
// role navigation (each role is its own workspace view), and a quiet footer
// with Settings / Support plus the live model + playbook-source indicators.
const NAV = [
  { key: "coordinator", label: "GTM Coordinator", icon: "robot" },
  { key: "sales", label: "Sales", icon: "dollar" },
  { key: "presales", label: "Pre-sales", icon: "compass" },
  { key: "cs", label: "Customer Success", icon: "heart" },
  { key: "analytics", label: "Analytics", icon: "bars" },
];

export default function Sidebar({ view, onNavigate, onNewDeal, meta }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark" aria-hidden="true">
          <Icon name="hub" size={22} />
        </div>
        <div className="brand-text">
          <div className="brand-name">GTM Hub</div>
          <div className="brand-sub">Enterprise Tier</div>
        </div>
      </div>

      <button className="new-deal" onClick={onNewDeal}>
        <Icon name="plus" size={18} />
        New Deal
      </button>

      <nav className="nav">
        {NAV.map((item) => (
          <button
            key={item.key}
            className={`nav-item${view === item.key ? " nav-active" : ""}`}
            onClick={() => onNavigate(item.key)}
            aria-current={view === item.key ? "page" : undefined}
          >
            <Icon name={item.icon} size={20} />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-foot">
        {meta && (
          <div className="runtime" title="Live model + playbook source">
            <span className="mono">{meta.model}</span>
            <span className={`source-pill source-${meta.playbook_source}`}>
              {meta.playbook_source} playbooks
            </span>
          </div>
        )}
        <div className="foot-links">
          <button className="foot-link" type="button">
            <Icon name="gear" size={18} />
            Settings
          </button>
          <button className="foot-link" type="button">
            <Icon name="lifebuoy" size={18} />
            Support
          </button>
        </div>
      </div>
    </aside>
  );
}
