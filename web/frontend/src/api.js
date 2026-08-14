// Thin client for the FastAPI backend (web/server.py). All calls are relative,
// so they work both under `vite dev` (proxied to :8000) and when the built SPA
// is served by FastAPI itself.

export async function getMeta() {
  const r = await fetch("/api/meta");
  if (!r.ok) throw new Error(`meta ${r.status}`);
  return r.json();
}

export async function getAccounts() {
  const r = await fetch("/api/accounts");
  if (!r.ok) throw new Error(`accounts ${r.status}`);
  const data = await r.json();
  return data.accounts || [];
}

export async function getLifecycle() {
  const r = await fetch("/api/lifecycle");
  if (!r.ok) throw new Error(`lifecycle ${r.status}`);
  const data = await r.json();
  return data.lifecycle || [];
}

export async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);
  const r = await fetch("/api/upload", { method: "POST", body: form });
  if (!r.ok) throw new Error(`upload ${r.status}`);
  return r.json(); // { file_text, filename, chars }
}

// Stream one chat turn over SSE. `handlers` may define:
//   onAgent(name), onDelta(text), onReplace(text), onFinal({reply, agent}), onError(msg)
// Returns a promise that resolves when the stream completes.
export async function streamChat(body, handlers, signal) {
  const r = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (!r.ok || !r.body) throw new Error(`chat stream ${r.status}`);

  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  const dispatch = (event, dataRaw) => {
    let data;
    try {
      data = JSON.parse(dataRaw);
    } catch {
      data = dataRaw;
    }
    if (event === "agent") handlers.onAgent?.(data);
    else if (event === "delta") handlers.onDelta?.(data);
    else if (event === "replace") handlers.onReplace?.(data);
    // Reasoning arrives on its own event so the UI can tuck it behind a
    // disclosure instead of prepending it to the answer.
    else if (event === "thought") handlers.onThought?.(data);
    // { agent, ms } -- the server times each agent; the client only renders it.
    else if (event === "agent_done") handlers.onAgentDone?.(data);
    else if (event === "final") handlers.onFinal?.(data);
    else if (event === "error") handlers.onError?.(data?.message || String(data));
  };

  // Parse the SSE stream frame by frame ("event:" + "data:" separated by \n\n).
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let sep;
    while ((sep = buffer.indexOf("\n\n")) !== -1) {
      const frame = buffer.slice(0, sep);
      buffer = buffer.slice(sep + 2);

      let event = "message";
      const dataLines = [];
      for (const line of frame.split("\n")) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
      }
      if (dataLines.length) dispatch(event, dataLines.join("\n"));
    }
  }
}
