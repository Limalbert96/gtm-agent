// The three GTM roles (plus the coordinator) are the app's organizing idea, so
// each one carries a meaning-bearing accent color used everywhere: the agent
// badge, the lifecycle rail dots, the dashboard owner chips, and the chat
// header accent that shifts to whoever just answered. Color here is
// information, not decoration.
//
//   Coordinator      lavender — neutral orchestrator (the GTM Hub primary)
//   Sales            amber    — the commercial / money role
//   Pre-Sales        teal     — the technical role
//   Customer Success violet   — the post-sale / retention role
//
// Accents are tuned to read on the dark "GTM Hub" canvas; `soft` is a low-alpha
// tint of the same hue for chip/pill backgrounds.

export const ROLES = {
  coordinator: {
    key: "coordinator",
    label: "GTM Coordinator",
    short: "Coordinator",
    accent: "#a5b0f7",
    soft: "rgba(165, 176, 247, 0.14)",
  },
  sales: {
    key: "sales",
    label: "Sales",
    short: "AE",
    accent: "#e6a15a",
    soft: "rgba(230, 161, 90, 0.14)",
  },
  presales: {
    key: "presales",
    label: "Pre-sales",
    short: "SC / SE",
    accent: "#37c2ac",
    soft: "rgba(55, 194, 172, 0.14)",
  },
  customer_success: {
    key: "customer_success",
    label: "Customer Success",
    short: "TSM",
    accent: "#9b8cf5",
    soft: "rgba(155, 140, 245, 0.14)",
  },
};

// Map ADK agent names -> role key.
const AGENT_TO_ROLE = {
  gtm_coordinator: "coordinator",
  sales_agent: "sales",
  presales_agent: "presales",
  customer_success_agent: "customer_success",
};

// Map the lifecycle "primary_role" strings from the backend -> role key.
const PRIMARY_ROLE_TO_KEY = {
  Sales: "sales",
  "Pre-Sales": "presales",
  "Customer Success": "customer_success",
};

export function roleForAgent(agentName) {
  return ROLES[AGENT_TO_ROLE[agentName]] || ROLES.coordinator;
}

export function roleForPrimary(primaryRole) {
  return ROLES[PRIMARY_ROLE_TO_KEY[primaryRole]] || ROLES.coordinator;
}

// Two-letter initials for an owner/role avatar (e.g. "Pre-sales" -> "PS").
export function roleInitials(role) {
  const label = (role?.short || role?.label || "").replace(/[^A-Za-z ]/g, "");
  const words = label.split(/[\s/]+/).filter(Boolean);
  if (words.length >= 2) return (words[0][0] + words[1][0]).toUpperCase();
  return label.slice(0, 2).toUpperCase();
}
