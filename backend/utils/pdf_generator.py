"""
pdf_generator.py
────────────────
Generates a professional PDF credit report using ReportLab.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

OUTPUT_DIR = "data/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Brand colours
SAFFRON = colors.HexColor("#E8871A")
INK     = colors.HexColor("#1A1A2E")
GREEN   = colors.HexColor("#2D7A4F")
RED     = colors.HexColor("#C0392B")
CREAM   = colors.HexColor("#FDF6EC")
MUTED   = colors.HexColor("#A08060")


def generate_pdf(report: dict, job_id: str) -> str:
    """Generate a PDF credit report and return the file path."""
    path = os.path.join(OUTPUT_DIR, f"khataloan_{job_id[:8]}.pdf")
    doc  = SimpleDocTemplate(path, pagesize=A4,
                             leftMargin=2*cm, rightMargin=2*cm,
                             topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    story  = []

    # ── Header ──────────────────────────────────────────────
    title_style = ParagraphStyle("title", fontSize=22, textColor=INK,
                                  fontName="Helvetica-Bold", spaceAfter=4)
    sub_style   = ParagraphStyle("sub",   fontSize=11, textColor=MUTED,
                                  fontName="Helvetica", spaceAfter=12)

    story.append(Paragraph("KhataLoan", title_style))
    story.append(Paragraph("MSME Credit Profile Report", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=SAFFRON))
    story.append(Spacer(1, 0.4*cm))

    # ── Report metadata ──────────────────────────────────────
    meta_style = ParagraphStyle("meta", fontSize=9, textColor=MUTED, fontName="Helvetica")
    story.append(Paragraph(f"Report ID: {job_id[:8].upper()}   |   Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}", meta_style))
    story.append(Paragraph(f"Analysis Period: {report.get('metrics', {}).get('analysis_period', 'N/A')}", meta_style))
    story.append(Spacer(1, 0.5*cm))

    # ── Credit score box ─────────────────────────────────────
    metrics = report.get("metrics", {})
    score   = metrics.get("creditworthiness_score", 0)
    risk    = metrics.get("risk_level", "UNKNOWN")
    risk_color = GREEN if risk == "LOW" else colors.orange if risk == "MEDIUM" else RED

    score_data = [[
        Paragraph(f"<b>{score}</b>", ParagraphStyle("sc", fontSize=36, textColor=INK, fontName="Helvetica-Bold", alignment=TA_CENTER)),
        Paragraph(f"<b>{risk} RISK</b>", ParagraphStyle("risk", fontSize=14, textColor=risk_color, fontName="Helvetica-Bold", alignment=TA_CENTER)),
        Paragraph(f"<b>₹{metrics.get('recommended_loan_limit', 0):,.0f}</b><br/><font size=9 color='grey'>Recommended Loan Limit</font>",
                  ParagraphStyle("loan", fontSize=16, textColor=INK, fontName="Helvetica-Bold", alignment=TA_CENTER)),
    ]]

    score_table = Table(score_data, colWidths=[5*cm, 5*cm, 7*cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CREAM),
        ("BOX",        (0, 0), (-1, -1), 1, SAFFRON),
        ("LINEBEFORE",  (1, 0), (1, -1), 0.5, MUTED),
        ("LINEBEFORE",  (2, 0), (2, -1), 0.5, MUTED),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING",(0,0), (-1, -1), 12),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Key Metrics ──────────────────────────────────────────
    h2 = ParagraphStyle("h2", fontSize=13, textColor=INK, fontName="Helvetica-Bold", spaceAfter=6)
    story.append(Paragraph("Financial Metrics", h2))

    metric_rows = [
        ["Monthly Average Revenue",  f"₹{metrics.get('monthly_avg_revenue', 0):,.2f}"],
        ["Monthly Average Expenses", f"₹{metrics.get('monthly_avg_expenses', 0):,.2f}"],
        ["Net Monthly Surplus",      f"₹{metrics.get('net_monthly_surplus', 0):,.2f}"],
        ["Debt Service Coverage Ratio (DSCR)", f"{metrics.get('dscr', 0):.2f}"],
    ]

    metric_table = Table(metric_rows, colWidths=[10*cm, 7*cm])
    metric_table.setStyle(TableStyle([
        ("FONTNAME",    (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME",    (0, 0), (0, -1),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("TEXTCOLOR",   (0, 0), (0, -1),  INK),
        ("TEXTCOLOR",   (1, 0), (1, -1),  INK),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, CREAM]),
        ("TOPPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0,0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("BOX",         (0, 0), (-1, -1), 0.5, MUTED),
        ("INNERGRID",   (0, 0), (-1, -1), 0.3, MUTED),
    ]))
    story.append(metric_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Narrative ────────────────────────────────────────────
    story.append(Paragraph("Credit Assessment", h2))
    body = ParagraphStyle("body", fontSize=10, textColor=INK, fontName="Helvetica",
                           leading=16, spaceAfter=8)
    story.append(Paragraph(report.get("narrative", ""), body))
    story.append(Spacer(1, 0.3*cm))

    # ── Missing data flags ───────────────────────────────────
    flags = report.get("missing_data_flags", [])
    if flags:
        story.append(Paragraph("Data Gaps & Flags", h2))
        flag_style = ParagraphStyle("flag", fontSize=9, textColor=RED, fontName="Helvetica",
                                     leftIndent=10, spaceAfter=3)
        for flag in flags:
            story.append(Paragraph(f"⚠ {flag}", flag_style))
        story.append(Spacer(1, 0.3*cm))

    # ── Transaction summary ──────────────────────────────────
    txns = report.get("transactions", [])[:20]  # Show first 20
    if txns:
        story.append(Paragraph(f"Transaction Summary (showing {len(txns)} of {len(report.get('transactions', []))})", h2))
        txn_header = [["Date", "Party", "Amount (₹)", "Type", "Category"]]
        txn_rows = []
        for t in txns:
            txn_rows.append([
                t.get("date", "—") or "—",
                (t.get("party") or "—")[:20],
                f"{t.get('amount', 0):,.0f}",
                t.get("type", "").upper(),
                t.get("category", "other"),
            ])

        txn_table = Table(txn_header + txn_rows, colWidths=[3*cm, 5*cm, 3*cm, 2.5*cm, 3.5*cm])
        txn_table.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0),  INK),
            ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CREAM]),
            ("TOPPADDING",  (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",(0,0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("BOX",         (0, 0), (-1, -1), 0.5, MUTED),
            ("INNERGRID",   (0, 0), (-1, -1), 0.2, MUTED),
        ]))
        story.append(txn_table)

    # ── Footer ───────────────────────────────────────────────
    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=SAFFRON))
    footer = ParagraphStyle("footer", fontSize=8, textColor=MUTED, fontName="Helvetica",
                             alignment=TA_CENTER, spaceBefore=6)
    story.append(Paragraph(
        "Generated by KhataLoan · From Bahi-Khata to Bank Loan · "
        "This report is AI-generated and should be reviewed by a qualified credit officer.",
        footer
    ))

    doc.build(story)
    return path
