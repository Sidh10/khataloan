import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000";
const C   = { ink: "#1A1A2E", saffron: "#E8871A", gold: "#F5A623", cream: "#FDF6EC", muted: "#A08060", green: "#2D7A4F", red: "#C0392B" };

function MetricCard({ label, value, sub, color }) {
  return (
    <div style={{ background: "#1E1E38", border: `1px solid ${color || C.saffron}`, borderRadius: "6px", padding: "1.2rem", flex: 1, minWidth: "160px" }}>
      <div style={{ fontSize: "1.8rem", fontWeight: 800, color: color || C.gold }}>{value}</div>
      <div style={{ fontWeight: 700, color: "#fff", marginTop: "0.25rem", fontSize: "0.9rem" }}>{label}</div>
      {sub && <div style={{ fontSize: "0.75rem", color: C.muted, marginTop: "0.2rem" }}>{sub}</div>}
    </div>
  );
}

export default function Report() {
  const { id }          = useParams();
  const navigate        = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState("");

  useEffect(() => {
    axios.get(`${API}/api/v1/report/${id}`)
      .then(r => { setReport(r.data); setLoading(false); })
      .catch(e => { setError(e.response?.data?.detail || "Failed to load report."); setLoading(false); });
  }, [id]);

  if (loading) return (
    <div style={{ minHeight: "100vh", background: C.ink, display: "flex", alignItems: "center", justifyContent: "center", color: C.gold, fontSize: "1.2rem" }}>
      Loading your credit profile...
    </div>
  );

  if (error) return (
    <div style={{ minHeight: "100vh", background: C.ink, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", color: "#fff" }}>
      <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>❌</div>
      <p style={{ color: C.muted }}>{error}</p>
      <button onClick={() => navigate("/upload")} style={{ background: C.saffron, border: "none", padding: "0.6rem 1.5rem", borderRadius: "4px", fontWeight: 700, cursor: "pointer", marginTop: "1rem" }}>
        Try Again
      </button>
    </div>
  );

  const metrics   = report.metrics || {};
  const score     = metrics.creditworthiness_score ?? 0;
  const risk      = metrics.risk_level ?? "UNKNOWN";
  const riskColor = risk === "LOW" ? C.green : risk === "MEDIUM" ? C.gold : C.red;
  const txns      = report.transactions || [];

  // Prepare chart data — group by month
  const monthlyMap = {};
  txns.forEach(t => {
    const m = (t.date || "").slice(0, 7);
    if (!m) return;
    if (!monthlyMap[m]) monthlyMap[m] = { month: m, revenue: 0, expenses: 0 };
    if (t.type === "credit") monthlyMap[m].revenue  += t.amount;
    else                     monthlyMap[m].expenses += t.amount;
  });
  const chartData = Object.values(monthlyMap).sort((a, b) => a.month.localeCompare(b.month)).slice(-12);

  return (
    <div style={{ minHeight: "100vh", background: C.ink }}>

      {/* Header */}
      <div style={{ background: C.saffron, padding: "1rem 2rem", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <a href="/" style={{ color: C.ink, fontWeight: 800, fontSize: "1.2rem", textDecoration: "none" }}>KhataLoan</a>
          <span style={{ color: C.ink, opacity: 0.6 }}>/ Credit Report</span>
        </div>
        <a href={`${API}/api/v1/report/${id}/pdf`} target="_blank" rel="noreferrer"
          style={{ background: C.ink, color: "#fff", padding: "0.5rem 1.2rem", borderRadius: "4px", fontSize: "0.85rem", fontWeight: 700, textDecoration: "none" }}>
          ⬇ Download PDF
        </a>
      </div>

      <div style={{ maxWidth: "960px", margin: "0 auto", padding: "2rem 1.5rem" }}>

        <h1 style={{ color: "#fff", marginBottom: "0.3rem" }}>
          {report.business_name || "Your Business"} — Credit Profile
        </h1>
        <p style={{ color: C.muted, marginBottom: "2rem" }}>Analysis Period: {metrics.analysis_period || "N/A"}</p>

        {/* Score + Risk + Loan */}
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "2rem" }}>
          <MetricCard label="Credit Score"           value={score}                    sub="Out of 100"              color={riskColor} />
          <MetricCard label="Risk Level"             value={risk}                     sub="Based on DSCR & history"  color={riskColor} />
          <MetricCard label="Recommended Loan"       value={`₹${(metrics.recommended_loan_limit || 0).toLocaleString("en-IN")}`} sub="Maximum suggested limit" color={C.saffron} />
          <MetricCard label="DSCR"                   value={metrics.dscr ?? "—"}      sub="Debt service coverage"    color={C.gold}    />
        </div>

        {/* Narrative */}
        <div style={{ background: "#1E1E38", border: `1px solid ${C.saffron}`, borderRadius: "6px", padding: "1.5rem", marginBottom: "2rem" }}>
          <h2 style={{ color: C.saffron, fontSize: "1rem", marginBottom: "0.8rem", textTransform: "uppercase", letterSpacing: "1px" }}>Credit Assessment</h2>
          <p style={{ color: "#ddd", lineHeight: 1.8, margin: 0 }}>{report.narrative}</p>
        </div>

        {/* Key metrics row */}
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "2rem" }}>
          <MetricCard label="Avg Monthly Revenue"  value={`₹${(metrics.monthly_avg_revenue  || 0).toLocaleString("en-IN")}`} color={C.green}   />
          <MetricCard label="Avg Monthly Expenses" value={`₹${(metrics.monthly_avg_expenses || 0).toLocaleString("en-IN")}`} color={C.red}     />
          <MetricCard label="Net Monthly Surplus"  value={`₹${(metrics.net_monthly_surplus  || 0).toLocaleString("en-IN")}`} color={C.saffron} />
        </div>

        {/* Revenue chart */}
        {chartData.length > 0 && (
          <div style={{ background: "#1E1E38", border: `1px solid #333`, borderRadius: "6px", padding: "1.5rem", marginBottom: "2rem" }}>
            <h2 style={{ color: C.saffron, fontSize: "1rem", marginBottom: "1rem", textTransform: "uppercase", letterSpacing: "1px" }}>Monthly Revenue vs Expenses</h2>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="month" tick={{ fill: C.muted, fontSize: 11 }} />
                <YAxis tick={{ fill: C.muted, fontSize: 11 }} tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
                <Tooltip formatter={v => `₹${v.toLocaleString("en-IN")}`} contentStyle={{ background: C.ink, border: `1px solid ${C.saffron}`, color: "#fff" }} />
                <Bar dataKey="revenue"  fill={C.saffron} name="Revenue"  radius={[3,3,0,0]} />
                <Bar dataKey="expenses" fill="#4A3020"   name="Expenses" radius={[3,3,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Data gaps */}
        {report.missing_data_flags?.length > 0 && (
          <div style={{ background: "#2E1A1A", border: `1px solid ${C.red}`, borderRadius: "6px", padding: "1.2rem", marginBottom: "2rem" }}>
            <h2 style={{ color: C.red, fontSize: "1rem", marginBottom: "0.6rem" }}>⚠ Data Gaps & Flags</h2>
            {report.missing_data_flags.map((f, i) => (
              <div key={i} style={{ color: "#ddd", fontSize: "0.88rem", marginTop: "0.3rem" }}>• {f}</div>
            ))}
          </div>
        )}

        {/* Transactions table */}
        {txns.length > 0 && (
          <div style={{ background: "#1E1E38", border: "1px solid #333", borderRadius: "6px", padding: "1.5rem" }}>
            <h2 style={{ color: C.saffron, fontSize: "1rem", marginBottom: "1rem", textTransform: "uppercase", letterSpacing: "1px" }}>
              Transactions ({txns.length})
            </h2>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
                <thead>
                  <tr style={{ background: C.ink }}>
                    {["Date", "Party", "Amount", "Type", "Category", "Source"].map(h => (
                      <th key={h} style={{ padding: "0.6rem 0.8rem", textAlign: "left", color: C.gold, fontWeight: 700, whiteSpace: "nowrap" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {txns.slice(0, 30).map((t, i) => (
                    <tr key={i} style={{ background: i % 2 === 0 ? "#252540" : "#1E1E38" }}>
                      <td style={{ padding: "0.5rem 0.8rem", color: "#ccc" }}>{t.date || "—"}</td>
                      <td style={{ padding: "0.5rem 0.8rem", color: "#ccc" }}>{t.party || "—"}</td>
                      <td style={{ padding: "0.5rem 0.8rem", color: t.type === "credit" ? C.green : C.red, fontWeight: 600 }}>
                        {t.type === "credit" ? "+" : "-"}₹{(t.amount || 0).toLocaleString("en-IN")}
                      </td>
                      <td style={{ padding: "0.5rem 0.8rem", color: t.type === "credit" ? C.green : C.red }}>{t.type}</td>
                      <td style={{ padding: "0.5rem 0.8rem", color: C.muted }}>{t.category}</td>
                      <td style={{ padding: "0.5rem 0.8rem", color: C.muted }}>{t.source}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {txns.length > 30 && <p style={{ color: C.muted, fontSize: "0.8rem", marginTop: "0.8rem" }}>Showing 30 of {txns.length} transactions. Download the PDF for the full report.</p>}
            </div>
          </div>
        )}

        <div style={{ textAlign: "center", marginTop: "2rem" }}>
          <button onClick={() => navigate("/upload")} style={{ background: "transparent", border: `1px solid ${C.saffron}`, color: C.saffron, padding: "0.6rem 1.5rem", borderRadius: "4px", cursor: "pointer", fontWeight: 600 }}>
            ← Process Another Business
          </button>
        </div>
      </div>
    </div>
  );
}
