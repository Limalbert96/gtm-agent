// A small, dependency-free inline-SVG icon set. Keeping icons local (rather than
// pulling an icon library) means the SPA builds with no extra network fetch and
// every glyph inherits `currentColor`, so role/theme colors flow through via CSS.
//
// Usage: <Icon name="rocket" /> or <Icon name="search" size={18} />

const PATHS = {
  // Brand: linked nodes (a small GTM "network"/hub mark).
  hub: (
    <>
      <circle cx="6" cy="6" r="2.4" />
      <circle cx="18" cy="6" r="2.4" />
      <circle cx="12" cy="18" r="2.4" />
      <path d="M7.6 7.4 10.6 16M16.4 7.4 13.4 16M8 6h8" />
    </>
  ),
  // Nav
  grid: (
    <>
      <rect x="3.5" y="3.5" width="7" height="7" rx="1.4" />
      <rect x="13.5" y="3.5" width="7" height="7" rx="1.4" />
      <rect x="3.5" y="13.5" width="7" height="7" rx="1.4" />
      <rect x="13.5" y="13.5" width="7" height="7" rx="1.4" />
    </>
  ),
  compass: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="m15.5 8.5-2 5-5 2 2-5z" />
    </>
  ),
  dollar: (
    <>
      <path d="M12 3.5v17" />
      <path d="M15.8 7.2c-.9-1-2.2-1.5-3.8-1.5-2.2 0-3.8 1.1-3.8 2.9 0 4.3 8 1.9 8 6.2 0 1.9-1.8 3-4.2 3-1.8 0-3.3-.6-4.2-1.7" />
    </>
  ),
  heart: (
    <path d="M12 20s-7-4.3-7-9.3C5 8 6.9 6 9.2 6c1.4 0 2.4.7 2.8 1.4C12.4 6.7 13.4 6 14.8 6 17.1 6 19 8 19 10.7c0 5-7 9.3-7 9.3Z" />
  ),
  bars: (
    <>
      <path d="M4 20h16" />
      <rect x="6" y="11" width="3" height="6" rx="0.6" />
      <rect x="11" y="7" width="3" height="10" rx="0.6" />
      <rect x="16" y="13" width="3" height="4" rx="0.6" />
    </>
  ),
  gear: (
    <>
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2.5v2.2M12 19.3v2.2M4.6 4.6l1.6 1.6M17.8 17.8l1.6 1.6M2.5 12h2.2M19.3 12h2.2M4.6 19.4l1.6-1.6M17.8 6.2l1.6-1.6" />
    </>
  ),
  lifebuoy: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <circle cx="12" cy="12" r="3.2" />
      <path d="m6 6 3.7 3.7M14.3 14.3 18 18M18 6l-3.7 3.7M9.7 14.3 6 18" />
    </>
  ),
  // Top bar
  search: (
    <>
      <circle cx="11" cy="11" r="6.5" />
      <path d="m20 20-3.6-3.6" />
    </>
  ),
  bell: (
    <>
      <path d="M6.5 9.5a5.5 5.5 0 0 1 11 0c0 4 1.5 5.5 1.5 5.5H5s1.5-1.5 1.5-5.5Z" />
      <path d="M10 18.5a2 2 0 0 0 4 0" />
    </>
  ),
  help: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M9.6 9.4a2.5 2.5 0 0 1 4.9.6c0 1.7-2.5 2-2.5 3.5" />
      <circle cx="12" cy="17" r="0.6" fill="currentColor" stroke="none" />
    </>
  ),
  // Cards / actions
  rocket: (
    <>
      <path d="M13.5 4.5c3.5-1 6 1.5 5 5-.7 2.5-3.4 5.2-6.5 6.8L9 14.5c1.6-3.1 4.3-5.8 6.8-6.5" />
      <path d="M9 14.5 6.5 12M6 15c-1.5.6-2 3-2 3s2.4-.5 3-2" />
      <circle cx="14.5" cy="9.5" r="1.2" />
    </>
  ),
  users: (
    <>
      <circle cx="9" cy="8" r="3" />
      <path d="M3.5 19a5.5 5.5 0 0 1 11 0" />
      <path d="M15.5 5.6a3 3 0 0 1 0 5.8M17 19a5.5 5.5 0 0 0-2.2-4.4" />
    </>
  ),
  doc: (
    <>
      <path d="M6.5 3.5h7L18 8v12.5H6.5Z" />
      <path d="M13 3.5V8h5M9 12.5h6M9 15.5h6" />
    </>
  ),
  plus: <path d="M12 5v14M5 12h14" />,
  arrow: <path d="M5 12h13m-5-5 5 5-5 5" />,
  check: <path d="m5 12.5 4 4 10-10" />,
  warn: (
    <>
      <path d="M12 4.5 3.5 19h17L12 4.5Z" />
      <path d="M12 10v4" />
      <circle cx="12" cy="16.6" r="0.6" fill="currentColor" stroke="none" />
    </>
  ),
  spark: (
    <path d="M12 3.5 13.7 9l5.3 1.7-5.3 1.7L12 20l-1.7-5.6L5 12.7 10.3 11 12 3.5Z" />
  ),
  send: (
    <path d="M4.5 11.8 20 5l-4.2 15.2-4.3-6-5.2-1.9-1.8-.5Z M11.5 14.2 20 5" />
  ),
  paperclip: (
    <path d="M18 8.5 10.6 16a3 3 0 0 1-4.2-4.2l7-7a4.5 4.5 0 0 1 6.4 6.4l-7.2 7.2a6 6 0 0 1-8.5-8.5" />
  ),
  // Coordinator / dashboards
  robot: (
    <>
      <rect x="4.5" y="8.5" width="15" height="10" rx="2.4" />
      <path d="M12 4.5v4" />
      <circle cx="12" cy="4" r="1.1" fill="currentColor" stroke="none" />
      <circle cx="9" cy="13" r="1.1" fill="currentColor" stroke="none" />
      <circle cx="15" cy="13" r="1.1" fill="currentColor" stroke="none" />
      <path d="M2.8 12v3M21.2 12v3" />
    </>
  ),
  flag: (
    <>
      <path d="M6 21V4" />
      <path d="M6 4.5h11l-2.2 3.5L17 12H6" />
    </>
  ),
  clock: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7.5V12l3 2" />
    </>
  ),
  calendar: (
    <>
      <rect x="4" y="5.5" width="16" height="15" rx="2" />
      <path d="M4 9.5h16M8.5 3.5v4M15.5 3.5v4" />
    </>
  ),
  play: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M10 8.8 15.5 12 10 15.2Z" fill="currentColor" stroke="none" />
    </>
  ),
  book: (
    <>
      <path d="M5 4.5h9a3 3 0 0 1 3 3v12H8a3 3 0 0 1-3-3Z" />
      <path d="M17 7.5h2v12H8a3 3 0 0 0-3 3" />
    </>
  ),
  filter: <path d="M4 6h16l-6 7v5l-4 2v-7L4 6Z" />,
  link: (
    <>
      <path d="M10 13.5a3.5 3.5 0 0 0 5 0l2.5-2.5a3.5 3.5 0 0 0-5-5L11 7.5" />
      <path d="M14 10.5a3.5 3.5 0 0 0-5 0L6.5 13a3.5 3.5 0 0 0 5 5L13 16.5" />
    </>
  ),
  trend: <path d="M4 15l4.5-4.5 3 3L20 6m0 0h-4m4 0v4" />,
  radio: <circle cx="12" cy="12" r="7.5" />,
};

export default function Icon({ name, size = 20, className = "", strokeWidth = 1.7 }) {
  const body = PATHS[name];
  if (!body) return null;
  return (
    <svg
      className={`icon ${className}`}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {body}
    </svg>
  );
}
