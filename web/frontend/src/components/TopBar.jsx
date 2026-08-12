import Icon from "./Icons.jsx";

// The persistent top bar: a global search field and the notification / help /
// settings / avatar cluster. Search is a controlled input so a view can filter
// off it later; the icon buttons are presentational for now.
export default function TopBar({ placeholder = "Search accounts, deals, or ask ADK…", search, onSearch }) {
  return (
    <header className="topbar">
      <div className="search">
        <Icon name="search" size={18} className="search-icon" />
        <input
          type="text"
          value={search}
          placeholder={placeholder}
          onChange={(e) => onSearch?.(e.target.value)}
          aria-label="Search"
        />
      </div>
      <div className="topbar-actions">
        <button className="top-icon" aria-label="Notifications">
          <span className="top-dot" />
          <Icon name="bell" size={20} />
        </button>
        <button className="top-icon" aria-label="Help">
          <Icon name="help" size={20} />
        </button>
        <button className="top-icon" aria-label="Settings">
          <Icon name="gear" size={20} />
        </button>
        <div className="avatar" aria-hidden="true">
          <span>AL</span>
        </div>
      </div>
    </header>
  );
}
