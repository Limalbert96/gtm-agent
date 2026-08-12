import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import TopBar from "./components/TopBar.jsx";
import CoordinatorView from "./components/CoordinatorView.jsx";
import SalesView from "./components/SalesView.jsx";
import PresalesView from "./components/PresalesView.jsx";
import CSView from "./components/CSView.jsx";
import AnalyticsView from "./components/AnalyticsView.jsx";
import { getMeta, uploadFile, streamChat } from "./api.js";
import { COORDINATOR_SEED } from "./demoData.js";

// One session per page load; the backend keeps multi-turn context keyed by it.
const SESSION_ID =
  (crypto.randomUUID && crypto.randomUUID()) ||
  `web-${Date.now()}-${Math.random().toString(16).slice(2)}`;

// Per-view search placeholder for the top bar.
const SEARCH_PLACEHOLDER = {
  coordinator: "Search accounts, deals, or ask ADK…",
  sales: "Search deals, accounts, or owners…",
  presales: "Search POCs, Criteria…",
  cs: "Search accounts…",
  analytics: "Search reports…",
};

export default function App() {
  const [view, setView] = useState("coordinator");
  const [search, setSearch] = useState("");
  const [meta, setMeta] = useState(null);

  // Chat state (the Coordinator view is the one functional, streaming surface).
  const [messages, setMessages] = useState(COORDINATOR_SEED);
  const [busy, setBusy] = useState(false);
  const [attachment, setAttachment] = useState(null); // { filename, chars, file_text }

  useEffect(() => {
    getMeta().then(setMeta).catch(() => {});
  }, []);

  // Update just the last (assistant) message immutably.
  const patchLast = (patch) =>
    setMessages((prev) => {
      if (!prev.length) return prev;
      const next = prev.slice();
      const last = { ...next[next.length - 1] };
      Object.assign(last, typeof patch === "function" ? patch(last) : patch);
      next[next.length - 1] = last;
      return next;
    });

  const handleAttach = async (file) => {
    try {
      const res = await uploadFile(file);
      setAttachment(res);
    } catch {
      setAttachment({ filename: file.name, chars: 0, file_text: "", error: true });
    }
  };

  const handleSend = async (text) => {
    if (busy || !text) return;
    setBusy(true);

    const fileText = attachment?.file_text || null;
    setMessages((prev) => [
      ...prev,
      { role: "user", text },
      { role: "assistant", text: "", agent: "gtm_coordinator", pending: true },
    ]);
    const usedAttachment = attachment;
    setAttachment(null);

    try {
      await streamChat(
        {
          session_id: SESSION_ID,
          message: text,
          account_id: null,
          file_text: fileText,
        },
        {
          onAgent: (name) => patchLast({ agent: name }),
          onDelta: (chunk) =>
            patchLast((last) => ({ text: (last.text || "") + chunk, pending: false })),
          onReplace: (full) => patchLast({ text: full, pending: false }),
          onFinal: (data) =>
            patchLast({ text: data.reply, agent: data.agent, pending: false }),
          onError: (msg) => patchLast({ text: `⚠︎ ${msg}`, pending: false }),
        }
      );
    } catch (e) {
      patchLast({
        text: `⚠︎ Couldn't reach the assistant (${e.message}). Is the server running?`,
        pending: false,
      });
      if (usedAttachment) setAttachment(usedAttachment);
    } finally {
      setBusy(false);
    }
  };

  // "New Deal" starts a fresh coordinator conversation.
  const handleNewDeal = () => {
    setMessages([]);
    setView("coordinator");
  };

  const renderView = () => {
    switch (view) {
      case "sales":
        return <SalesView />;
      case "presales":
        return <PresalesView />;
      case "cs":
        return <CSView />;
      case "analytics":
        return <AnalyticsView />;
      case "coordinator":
      default:
        return (
          <CoordinatorView
            messages={messages}
            busy={busy}
            onSend={handleSend}
            onAction={handleSend}
            attachment={attachment}
            onAttach={handleAttach}
            onClearAttachment={() => setAttachment(null)}
          />
        );
    }
  };

  return (
    <div className="shell">
      <Sidebar view={view} onNavigate={setView} onNewDeal={handleNewDeal} meta={meta} />
      <div className="main">
        <TopBar
          placeholder={SEARCH_PLACEHOLDER[view]}
          search={search}
          onSearch={setSearch}
        />
        <div className="view-scroll">{renderView()}</div>
      </div>
    </div>
  );
}
