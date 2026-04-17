import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000";
const C   = { ink: "#1A1A2E", saffron: "#E8871A", gold: "#F5A623", cream: "#FDF6EC", muted: "#A08060", green: "#2D7A4F" };

const STAGES = [
  { key: "ingest",      label: "Receiving files",         pct: 5  },
  { key: "ocr",         label: "Reading ledger images",   pct: 30 },
  { key: "voice",       label: "Transcribing voice notes",pct: 50 },
  { key: "upi",         label: "Parsing UPI screenshots", pct: 65 },
  { key: "reconstruct", label: "Reconstructing history",  pct: 80 },
  { key: "report",      label: "Generating credit report",pct: 95 },
];

function DropZone({ label, accept, files, setFiles, emoji }) {
  const [dragging, setDragging] = useState(false);

  const handleDrop = useCallback(e => {
    e.preventDefault();
    setDragging(false);
    const dropped = Array.from(e.dataTransfer.files).filter(f => {
      const ext = f.name.split(".").pop().toLowerCase();
      return accept.includes(ext);
    });
    setFiles(prev => [...prev, ...dropped]);
  }, [accept, setFiles]);

  const handleChange = e => setFiles(prev => [...prev, ...Array.from(e.target.files)]);

  return (
    <div
      onDragOver={e => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      style={{
        border: `2px dashed ${dragging ? C.saffron : C.muted}`,
        borderRadius: "6px",
        padding: "1.5rem",
        textAlign: "center",
        background: dragging ? "#FFF3E0" : C.cream,
        cursor: "pointer",
        transition: "all 0.2s",
        flex: 1,
        minWidth: "200px",
      }}
    >
      <div style={{ fontSize: "2rem" }}>{emoji}</div>
      <div style={{ fontWeight: 700, color: C.ink, marginTop: "0.4rem" }}>{label}</div>
      <div style={{ fontSize: "0.8rem", color: C.muted, margin: "0.3rem 0 0.8rem" }}>
        Drag & drop or click to browse
      </div>
      <label style={{ background: C.saffron, color: C.ink, padding: "0.4rem 1rem", borderRadius: "3px", fontSize: "0.8rem", fontWeight: 700, cursor: "pointer" }}>
        Browse Files
        <input type="file" multiple accept={accept.map(e => `.${e}`).join(",")} onChange={handleChange} style={{ display: "none" }} />
      </label>
      {files.length > 0 && (
        <div style={{ marginTop: "0.8rem" }}>
          {files.map((f, i) => (
            <div key={i} style={{ fontSize: "0.78rem", color: C.green, marginTop: "0.2rem" }}>
              ✓ {f.name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ProgressBar({ pct }) {
  return (
    <div style={{ background: "#ddd", borderRadius: "99px", height: "8px", width: "100%", margin: "0.8rem 0" }}>
      <div style={{ background: C.saffron, width: `${pct}%`, height: "100%", borderRadius: "99px", transition: "width 0.5s ease" }} />
    </div>
  );
}

export default function Upload() {
  const navigate = useNavigate();
  const [ledgerFiles, setLedgerFiles]  = useState([]);
  const [voiceFiles,  setVoiceFiles]   = useState([]);
  const [upiFiles,    setUpiFiles]     = useState([]);
  const [status, setStatus]            = useState(null); // null | "uploading" | "processing" | "done" | "error"
  const [stage,  setStage]             = useState("");
  const [progress, setProgress]        = useState(0);
  const [message, setMessage]          = useState("");
  const [error,  setError]             = useState("");

  const totalFiles = ledgerFiles.length + voiceFiles.length + upiFiles.length;

  const pollStatus = (jobId) => {
    const interval = setInterval(async () => {
      try {
        const { data } = await axios.get(`${API}/api/v1/status/${jobId}`);
        setStage(data.stage);
        setProgress(data.progress);
        setMessage(data.message);

        if (data.status === "complete") {
          clearInterval(interval);
          setStatus("done");
          setTimeout(() => navigate(`/report/${jobId}`), 800);
        } else if (data.status === "failed") {
          clearInterval(interval);
          setStatus("error");
          setError(data.message);
        }
      } catch {
        clearInterval(interval);
        setStatus("error");
        setError("Lost connection to server.");
      }
    }, 1500);
  };

  const handleSubmit = async () => {
    if (totalFiles === 0) return;
    setStatus("uploading");
    setProgress(5);
    setMessage("Uploading files...");

    const form = new FormData();
    ledgerFiles.forEach(f => form.append("ledger_images",   f));
    voiceFiles.forEach( f => form.append("voice_notes",     f));
    upiFiles.forEach(   f => form.append("upi_screenshots", f));

    try {
      const { data } = await axios.post(`${API}/api/v1/upload`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setStatus("processing");
      pollStatus(data.job_id);
    } catch (e) {
      setStatus("error");
      setError(e.response?.data?.detail || "Upload failed.");
    }
  };

  const currentStageLabel = STAGES.find(s => s.key === stage)?.label || message;

  return (
    <div style={{ minHeight: "100vh", background: C.ink }}>

      {/* Header */}
      <div style={{ background: C.saffron, padding: "1rem 2rem", display: "flex", alignItems: "center", gap: "1rem" }}>
        <a href="/" style={{ color: C.ink, fontWeight: 800, fontSize: "1.2rem", textDecoration: "none" }}>KhataLoan</a>
        <span style={{ color: C.ink, opacity: 0.6 }}>/ Upload</span>
      </div>

      <div style={{ maxWidth: "820px", margin: "0 auto", padding: "2.5rem 1.5rem" }}>
        <h1 style={{ color: "#fff", fontSize: "1.8rem", marginBottom: "0.5rem" }}>Upload Your Financial Records</h1>
        <p style={{ color: C.muted, marginBottom: "2rem" }}>
          Upload any combination — even a single ledger photo is enough to start.
        </p>

        {/* Drop zones */}
        {!status && (
          <>
            <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "2rem" }}>
              <DropZone label="Ledger Photos"       emoji="📒" accept={["jpg","jpeg","png","webp"]} files={ledgerFiles} setFiles={setLedgerFiles} />
              <DropZone label="Voice Notes"         emoji="🎙️" accept={["mp3","wav","m4a","ogg","webm"]} files={voiceFiles}  setFiles={setVoiceFiles}  />
              <DropZone label="UPI Screenshots"     emoji="📱" accept={["jpg","jpeg","png","webp"]} files={upiFiles}    setFiles={setUpiFiles}    />
            </div>

            <button
              onClick={handleSubmit}
              disabled={totalFiles === 0}
              style={{
                background: totalFiles > 0 ? C.saffron : "#555",
                color: C.ink, border: "none", borderRadius: "4px",
                padding: "0.9rem 2.5rem", fontSize: "1rem", fontWeight: 700,
                cursor: totalFiles > 0 ? "pointer" : "not-allowed", width: "100%",
              }}
            >
              {totalFiles > 0 ? `Generate Credit Profile (${totalFiles} file${totalFiles > 1 ? "s" : ""})` : "Add at least one file to continue"}
            </button>
          </>
        )}

        {/* Processing state */}
        {(status === "uploading" || status === "processing") && (
          <div style={{ background: "#1E1E38", border: `1px solid ${C.saffron}`, borderRadius: "6px", padding: "2.5rem", textAlign: "center" }}>
            <div style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>⚙️</div>
            <h2 style={{ color: "#fff", marginBottom: "0.5rem" }}>Processing Your Records</h2>
            <p style={{ color: C.muted, marginBottom: "1.5rem" }}>{currentStageLabel}</p>
            <ProgressBar pct={progress} />
            <div style={{ fontSize: "0.85rem", color: C.gold, marginTop: "0.5rem" }}>{progress}% complete</div>

            <div style={{ display: "flex", justifyContent: "center", gap: "1rem", flexWrap: "wrap", marginTop: "2rem" }}>
              {STAGES.map(s => (
                <div key={s.key} style={{ fontSize: "0.78rem", color: s.key === stage ? C.saffron : progress > s.pct ? C.green : "#555", fontWeight: s.key === stage ? 700 : 400 }}>
                  {progress > s.pct ? "✓" : s.key === stage ? "→" : "·"} {s.label}
                </div>
              ))}
            </div>
          </div>
        )}

        {status === "done" && (
          <div style={{ background: "#1E2E1E", border: `1px solid ${C.green}`, borderRadius: "6px", padding: "2rem", textAlign: "center", color: "#fff" }}>
            <div style={{ fontSize: "3rem" }}>✅</div>
            <h2 style={{ color: C.green }}>Credit Profile Ready!</h2>
            <p style={{ color: C.muted }}>Redirecting to your report...</p>
          </div>
        )}

        {status === "error" && (
          <div style={{ background: "#2E1A1A", border: "1px solid #C0392B", borderRadius: "6px", padding: "2rem", textAlign: "center", color: "#fff" }}>
            <div style={{ fontSize: "2rem" }}>❌</div>
            <h2 style={{ color: "#E74C3C" }}>Processing Failed</h2>
            <p style={{ color: C.muted }}>{error}</p>
            <button onClick={() => { setStatus(null); setError(""); }} style={{ background: C.saffron, border: "none", padding: "0.6rem 1.5rem", borderRadius: "4px", fontWeight: 700, cursor: "pointer", marginTop: "1rem" }}>
              Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
