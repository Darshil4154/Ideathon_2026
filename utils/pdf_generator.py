"""PDF generation for recovery plans, screening reports, and insurance summaries."""

from __future__ import annotations

from io import BytesIO

from fpdf import FPDF


class _MedBridgePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(27, 79, 114)
        self.cell(0, 10, "MedBridge AI", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "Your AI Healthcare Copilot", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(120, 120, 120)
        self.cell(
            0,
            8,
            "MedBridge AI is not a substitute for professional medical advice.",
            align="C",
        )


def _sanitize(text: str) -> str:
    """Strip characters that the default FPDF latin-1 font cannot encode."""
    if text is None:
        return ""
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _render_document(title: str, body: str) -> bytes:
    pdf = _MedBridgePDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.multi_cell(0, 8, _sanitize(title))
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 11)
    for paragraph in body.split("\n"):
        if not paragraph.strip():
            pdf.ln(3)
            continue
        pdf.multi_cell(0, 6, _sanitize(paragraph))
    output = pdf.output(dest="S")
    # fpdf2 returns bytearray; normalize to bytes
    if isinstance(output, (bytearray, bytes)):
        return bytes(output)
    return output.encode("latin-1")


def generate_recovery_plan_pdf(plan: dict) -> bytes:
    lines = [f"Condition: {plan.get('condition', '')}", "", plan.get("overview", ""), ""]
    for phase in plan.get("phases", []):
        lines.append(phase.get("label", ""))
        lines.append(f"  Activity: {phase.get('activity', '')}")
        lines.append(f"  Diet: {phase.get('diet', '')}")
        meds = phase.get("medications", [])
        if meds:
            lines.append("  Medications:")
            for med in meds:
                lines.append(f"    - {med.get('name', '')} {med.get('dose', '')} — {med.get('schedule', '')}")
        red_flags = phase.get("red_flags", [])
        if red_flags:
            lines.append("  Watch for: " + "; ".join(red_flags))
        lines.append("")
    lines.append(f"Follow-up: {plan.get('follow_up', '')}")
    lines.append("")
    lines.append("Emergency symptoms — call 911:")
    for sym in plan.get("emergency_symptoms", []):
        lines.append(f"  - {sym}")
    return _render_document("Your Recovery Plan", "\n".join(lines))


def generate_application_summary_pdf(summary_text: str) -> bytes:
    return _render_document("Insurance Application Pre-fill Summary", summary_text)


def generate_screening_report_pdf(profile: dict, screenings: list[dict], top_priority: str, lifestyle: str) -> bytes:
    lines = ["PATIENT PROFILE", "-" * 60]
    for key, value in profile.items():
        lines.append(f"  {key}: {value}")
    lines.append("")
    lines.append("RECOMMENDED SCREENINGS")
    lines.append("-" * 60)
    for s in screenings:
        lines.append(f"[{s.get('status', '')}] {s.get('name', '')}")
        lines.append(f"   Due: {s.get('due_date_relative', '')}")
        lines.append(f"   Why: {s.get('why_it_matters', '')}")
        lines.append(f"   Where: {s.get('where_to_go', '')}")
        lines.append("")
    lines.append("TOP PRIORITY")
    lines.append("-" * 60)
    lines.append(top_priority)
    lines.append("")
    lines.append("LIFESTYLE NOTES")
    lines.append("-" * 60)
    lines.append(lifestyle)
    return _render_document("Preventive Screening Report", "\n".join(lines))
