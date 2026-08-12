import { useRef, useState } from "react";
import Icon from "./Icons.jsx";

// The message box: a growing textarea, an attach control, and a send button.
// Enter sends; Shift+Enter makes a newline. Attachments are extracted to text
// by the backend and travel with the next message.
export default function Composer({
  onSend,
  disabled,
  attachment,
  onAttach,
  onClearAttachment,
  placeholder = "Ask ADK for insights, commands, or data…",
}) {
  const [value, setValue] = useState("");
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef(null);
  const taRef = useRef(null);

  const grow = (el) => {
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 200) + "px";
  };

  const send = () => {
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue("");
    if (taRef.current) taRef.current.style.height = "auto";
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const pickFile = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await onAttach(file);
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  return (
    <div className="composer">
      {attachment && (
        <div className="attach-chip">
          <span className="attach-name">{attachment.filename}</span>
          <span className="attach-meta">{attachment.chars.toLocaleString()} chars</span>
          <button className="attach-x" onClick={onClearAttachment} aria-label="Remove attachment">
            ×
          </button>
        </div>
      )}
      <div className="composer-row">
        <button
          className="icon-btn"
          onClick={() => fileRef.current?.click()}
          disabled={disabled || uploading}
          title="Attach a document (transcript, RFP, notes)"
          aria-label="Attach a document"
        >
          {uploading ? "…" : <Icon name="paperclip" size={18} />}
        </button>
        <input
          ref={fileRef}
          type="file"
          className="visually-hidden"
          onChange={pickFile}
          accept=".txt,.md,.csv,.json,.log,.pdf,.docx"
        />
        <textarea
          ref={taRef}
          rows={1}
          value={value}
          placeholder={placeholder}
          onChange={(e) => {
            setValue(e.target.value);
            grow(e.target);
          }}
          onKeyDown={onKeyDown}
          disabled={disabled}
        />
        <button
          className="send-btn"
          onClick={send}
          disabled={disabled || !value.trim()}
          aria-label="Send"
        >
          <Icon name="send" size={20} />
        </button>
      </div>
    </div>
  );
}
