import { roleForAgent } from "../roles.js";

// A small chip naming the specialist that authored a reply, colored by role.
export default function AgentBadge({ agent, size = "sm" }) {
  const role = roleForAgent(agent);
  return (
    <span
      className={`badge badge-${size}`}
      style={{ color: role.accent, background: role.soft }}
    >
      <span className="badge-dot" style={{ background: role.accent }} />
      {role.label}
    </span>
  );
}
