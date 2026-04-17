import { useNavigate } from "react-router-dom";

const C = { ink: "#1A1A2E", saffron: "#E8871A", gold: "#F5A623", cream: "#FDF6EC", muted: "#A08060" };

export default function Home() {
  const navigate = useNavigate();

  return (
    <div style={{ minHeight: "100vh", background: C.ink, color: "#fff", display: "flex", flexDirection: "column" }}>

      {/* Nav */}
      <nav style={{ padding: "1.2rem 2rem", display: "flex", alignItems: "center", borderBottom: `2px solid ${C.saffron}` }}>
        <span style={{ fontSize: "1.4rem", fontWeight: 700, color: C.saffron }}>KhataLoan</span>
        <span style={{ marginLeft: "0.75rem", fontSize: "0.8rem", color: C.muted, paddingTop: "2px" }}>
          📒 → 🏦
        </span>
      </nav>

      {/* Hero */}
      <main style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "3rem 1rem", textAlign: "center" }}>
        <div style={{ background: C.saffron, color: C.ink, fontSize: "0.75rem", fontWeight: 700, padding: "0.3rem 1rem", borderRadius: "2px", letterSpacing: "1.5px", marginBottom: "1.5rem" }}>
          GENERATIVE AI · HACK & BREAK
        </div>

        <h1 style={{ fontSize: "clamp(2.5rem, 6vw, 4.5rem)", fontWeight: 800, lineHeight: 1.1, margin: "0 0 1rem" }}>
          From Bahi-Khata<br />
          <span style={{ color: C.saffron }}>to Bank Loan.</span>
        </h1>

        <p style={{ fontSize: "1.15rem", color: C.muted, maxWidth: "560px", lineHeight: 1.7, margin: "0 0 2.5rem" }}>
          Upload photos of your handwritten ledger, voice notes in any Indian language,
          or UPI screenshots. We reconstruct your financial history and generate a
          bank-ready credit profile — in under 5 minutes.
        </p>

        <button
          onClick={() => navigate("/upload")}
          style={{
            background: C.saffron, color: C.ink, border: "none", borderRadius: "4px",
            padding: "0.9rem 2.5rem", fontSize: "1.05rem", fontWeight: 700,
            cursor: "pointer", transition: "opacity 0.2s",
          }}
          onMouseOver={e => e.target.style.opacity = 0.85}
          onMouseOut={e => e.target.style.opacity = 1}
        >
          Get Your Credit Profile →
        </button>

        {/* Stats */}
        <div style={{ display: "flex", gap: "3rem", marginTop: "4rem", flexWrap: "wrap", justifyContent: "center" }}>
          {[
            { val: "63M", label: "MSMEs in India" },
            { val: "84%", label: "Without formal credit" },
            { val: "₹25L Cr", label: "Credit gap [RBI]" },
            { val: "<5 min", label: "Profile generation" },
          ].map(s => (
            <div key={s.val} style={{ textAlign: "center" }}>
              <div style={{ fontSize: "2rem", fontWeight: 800, color: C.gold }}>{s.val}</div>
              <div style={{ fontSize: "0.8rem", color: C.muted, marginTop: "0.2rem" }}>{s.label}</div>
            </div>
          ))}
        </div>
      </main>

      {/* How it works */}
      <section style={{ background: "#12122A", padding: "3rem 2rem" }}>
        <h2 style={{ textAlign: "center", fontSize: "1.4rem", color: "#fff", marginBottom: "2rem" }}>
          How It Works
        </h2>
        <div style={{ display: "flex", gap: "1.5rem", justifyContent: "center", flexWrap: "wrap", maxWidth: "900px", margin: "0 auto" }}>
          {[
            { num: "1", title: "Upload", desc: "Ledger photos, voice notes, or UPI screenshots — any combination works" },
            { num: "2", title: "AI Reads", desc: "GPT-4o Vision reads handwritten text. Whisper transcribes your voice notes" },
            { num: "3", title: "Reconstruct", desc: "Our agent deduplicates, categorises, and fills gaps in your history" },
            { num: "4", title: "Report", desc: "Download a bank-ready credit profile PDF in under 5 minutes" },
          ].map(step => (
            <div key={step.num} style={{ background: "#1E1E38", border: `1px solid ${C.saffron}`, borderRadius: "4px", padding: "1.5rem", width: "200px" }}>
              <div style={{ fontSize: "2rem", fontWeight: 800, color: C.saffron }}>{step.num}</div>
              <div style={{ fontWeight: 700, margin: "0.5rem 0 0.4rem", color: "#fff" }}>{step.title}</div>
              <div style={{ fontSize: "0.85rem", color: C.muted, lineHeight: 1.6 }}>{step.desc}</div>
            </div>
          ))}
        </div>
      </section>

      <footer style={{ background: C.saffron, padding: "0.7rem", textAlign: "center", fontSize: "0.8rem", color: C.ink, fontWeight: 600 }}>
        KhataLoan · Built for Hack & Break Innovation Challenge
      </footer>
    </div>
  );
}
