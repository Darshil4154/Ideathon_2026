"""Module 4: Preventive Screen Check — USPSTF-based screening timeline."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.ai_engine import (
    build_screen_check_system_prompt,
    call_claude,
    extract_json,
    load_uspstf_guidelines,
)
from utils.pdf_generator import generate_screening_report_pdf
from utils.ui import hero, section_label

STATUS_COLORS = {
    "OVERDUE": "#B03A2E",
    "UPCOMING": "#D4AC0D",
    "ON_TRACK": "#1E8449",
    "NOT_APPLICABLE": "#808B96",
}


def _demo_profile() -> dict[str, Any]:
    return {
        "age": 52,
        "sex": "Female",
        "smoking": "Never smoked",
        "family_history": ["Diabetes", "Breast cancer"],
        "conditions": ["Prediabetes"],
    }


def _demo_analysis(profile: dict[str, Any]) -> dict[str, Any]:
    age = profile["age"]
    sex = profile["sex"].lower()
    family = [f.lower() for f in profile.get("family_history", [])]
    conditions = [c.lower() for c in profile.get("conditions", [])]

    guidelines = load_uspstf_guidelines()
    screenings: list[dict[str, Any]] = []
    for g in guidelines:
        if sex != "any" and g["sex"] != "any" and g["sex"] != sex:
            continue
        if not (g["age_min"] <= age <= g["age_max"]):
            continue
        # naive status heuristic for demo
        name = g["name"]
        status = "ON_TRACK"
        if name == "Type 2 Diabetes / Prediabetes Screening" and ("prediabetes" in conditions or "diabetes" in family):
            status = "OVERDUE"
        if name == "Breast Cancer Screening (Mammogram)" and "breast cancer" in family:
            status = "OVERDUE"
        if name == "Colorectal Cancer Screening" and age >= 45:
            status = "UPCOMING"
        if name == "Cholesterol (Lipid Panel)" and age >= 40:
            status = "UPCOMING"
        if name == "Blood Pressure Screening":
            status = "UPCOMING"
        if name == "Depression Screening":
            status = "ON_TRACK"
        if name == "Flu Vaccine":
            status = "UPCOMING"
        if name == "Bone Density (DEXA) Scan" and age < 65:
            continue
        if name == "Lung Cancer Screening (Low-dose CT)" and "smoking history" not in family:
            continue
        if name == "Abdominal Aortic Aneurysm Screening":
            continue

        screenings.append(
            {
                "name": name,
                "status": status,
                "due_date_relative": {
                    "OVERDUE": "Now",
                    "UPCOMING": "Within 6 months",
                    "ON_TRACK": "In 1 year",
                }.get(status, "When convenient"),
                "why_it_matters": _why_matters(name, profile),
                "where_to_go": _where_to_go(name),
            }
        )

    return {
        "screenings": screenings,
        "top_priority": (
            "Given your family history of diabetes and being prediabetic, **A1C and fasting glucose testing** is the "
            "#1 priority — it catches the shift from prediabetes to diabetes early. Your family history of breast cancer "
            "also makes an **updated mammogram** important."
        ),
        "lifestyle_notes": (
            "Walk 20-30 minutes a day most days, aim for mostly whole foods and fewer sugary drinks, and keep an eye on "
            "your blood pressure at home. Small consistent changes beat big short-lived ones."
        ),
    }


def _why_matters(name: str, profile: dict[str, Any]) -> str:
    meta = {
        "Type 2 Diabetes / Prediabetes Screening": "You already have prediabetes and a family history of diabetes — regular A1C tests catch the progression early when it's most reversible.",
        "Breast Cancer Screening (Mammogram)": "Family history of breast cancer raises your personal risk; screening finds cancer earlier when it's easier to treat.",
        "Colorectal Cancer Screening": "Colon cancer screening prevents cancer, not just catches it — polyps can be removed before turning cancerous.",
        "Cholesterol (Lipid Panel)": "Prediabetes often travels with high cholesterol; treating both together significantly lowers heart-attack risk.",
        "Blood Pressure Screening": "High blood pressure is silent but very treatable. Annual checks keep you ahead of it.",
        "Cervical Cancer Screening (Pap/HPV)": "Routine Pap/HPV catches precancerous changes years before cancer develops.",
        "Depression Screening": "Quick annual check-in so nothing slips under the radar while you manage other conditions.",
        "Flu Vaccine": "Reduces severe flu illness — especially useful with chronic conditions like prediabetes.",
    }
    return meta.get(name, "Recommended by USPSTF guidelines for patients like you.")


def _where_to_go(name: str) -> str:
    mapping = {
        "Type 2 Diabetes / Prediabetes Screening": "Brazos Valley Community Health Center — primary care can order A1C",
        "Breast Cancer Screening (Mammogram)": "Baylor Scott & White College Station or St. Joseph Health Bryan imaging",
        "Colorectal Cancer Screening": "Ask your BVCHC provider for a FIT kit (free/low-cost) or a referral",
        "Cholesterol (Lipid Panel)": "Any primary-care visit can include a fasting lipid panel",
        "Blood Pressure Screening": "Any BVCHC or Bluebonnet clinic visit",
        "Cervical Cancer Screening (Pap/HPV)": "Bluebonnet Community Health Center women's health",
        "Depression Screening": "Built into any BVCHC primary-care visit",
        "Flu Vaccine": "Any pharmacy (HEB, Walgreens, CVS) or BVCHC",
    }
    return mapping.get(name, "Brazos Valley Community Health Center")


def _run_analysis(profile: dict[str, Any]) -> dict[str, Any]:
    if st.session_state.get("demo_mode", False):
        return _demo_analysis(profile)
    try:
        raw = call_claude(
            build_screen_check_system_prompt(),
            f"Patient profile: {profile}",
            max_tokens=1800,
        )
        return extract_json(raw)
    except (RuntimeError, ValueError) as err:
        st.warning(f"Live analysis unavailable ({err}). Showing demo analysis.")
        return _demo_analysis(profile)


def _render_timeline(screenings: list[dict[str, Any]]) -> None:
    today = datetime.today()
    rows = []
    for idx, s in enumerate(screenings):
        status = s.get("status", "ON_TRACK")
        offset_days = {
            "OVERDUE": -30,
            "UPCOMING": 90,
            "ON_TRACK": 240,
            "NOT_APPLICABLE": 365,
        }.get(status, 180)
        start = today + timedelta(days=max(offset_days - 30, -45))
        end = today + timedelta(days=offset_days + 30)
        rows.append({
            "Screening": s.get("name", f"Screening {idx}"),
            "Start": start,
            "Finish": end,
            "Status": status,
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="Finish",
        y="Screening",
        color="Status",
        color_discrete_map=STATUS_COLORS,
    )
    fig.update_yaxes(autorange="reversed")
    fig.add_vline(x=today, line_dash="dash", line_color="#1B4F72")
    fig.update_layout(
        height=max(260, 50 * len(rows) + 80),
        margin=dict(t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render() -> None:
    hero(
        icon="🩺",
        title="Preventive Screen Check",
        subtitle="Tell me about you — I'll build a personalized USPSTF screening timeline.",
    )

    if st.button("🎬 Load demo profile"):
        st.session_state.screen_profile = _demo_profile()

    defaults = st.session_state.get("screen_profile", {})

    col1, col2, col3 = st.columns(3)
    age = col1.number_input("Age", min_value=0, max_value=120, value=int(defaults.get("age", 35)))
    sex = col2.selectbox("Sex assigned at birth", ["Female", "Male"], index=0 if defaults.get("sex", "Female") == "Female" else 1)
    smoking = col3.selectbox(
        "Smoking status",
        ["Never smoked", "Former smoker", "Current smoker"],
        index=["Never smoked", "Former smoker", "Current smoker"].index(defaults.get("smoking", "Never smoked")),
    )

    st.markdown("**Family history** (check all that apply)")
    fam_cols = st.columns(4)
    family_options = ["Heart disease", "Diabetes", "Breast cancer", "Colon cancer", "Prostate cancer", "Osteoporosis", "Stroke", "Smoking history"]
    family_default = set(defaults.get("family_history", []))
    family = []
    for i, opt in enumerate(family_options):
        if fam_cols[i % 4].checkbox(opt, value=opt in family_default, key=f"fam_{opt}"):
            family.append(opt)

    conditions_str = st.text_input(
        "Existing conditions (optional, comma-separated)",
        value=", ".join(defaults.get("conditions", [])),
        placeholder="e.g. Prediabetes, High blood pressure",
    )
    conditions = [c.strip() for c in conditions_str.split(",") if c.strip()]

    if st.button("🩺 Build my screening plan", type="primary"):
        profile = {
            "age": age,
            "sex": sex,
            "smoking": smoking,
            "family_history": family,
            "conditions": conditions,
        }
        with st.spinner("Building your personalized screening plan..."):
            st.session_state.screen_analysis = _run_analysis(profile)
            st.session_state.screen_profile_last = profile

    analysis = st.session_state.get("screen_analysis")
    if not analysis:
        return

    st.markdown("---")
    st.markdown("### 📅 Your screening timeline")
    _render_timeline(analysis.get("screenings", []))

    st.info(f"⭐ **Top priority:** {analysis.get('top_priority', '')}")

    screenings = analysis.get("screenings", [])
    grouped = {"OVERDUE": [], "UPCOMING": [], "ON_TRACK": []}
    for s in screenings:
        grouped.setdefault(s.get("status", "ON_TRACK"), []).append(s)

    group_meta = [
        ("OVERDUE", "🔴 Overdue", "mb-badge-danger", True),
        ("UPCOMING", "🟡 Upcoming", "mb-badge-warning", True),
        ("ON_TRACK", "🟢 On track", "mb-badge-ok", False),
    ]
    for key, label, badge_class, default_open in group_meta:
        items = grouped.get(key, [])
        if not items:
            continue
        with st.expander(f"{label} ({len(items)})", expanded=default_open):
            for s in items:
                st.markdown(
                    f"""
                    <div class='mb-card'>
                      <h4>{s.get('name', '')}</h4>
                      <p><b>When:</b> {s.get('due_date_relative', '')} · <b>Where:</b> {s.get('where_to_go', '')}</p>
                      <p class='mb-muted'>{s.get('why_it_matters', '')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.caption(f"💡 Lifestyle: {analysis.get('lifestyle_notes', '')}")

    profile = st.session_state.get("screen_profile_last", {})
    pdf_bytes = generate_screening_report_pdf(
        profile=profile,
        screenings=analysis.get("screenings", []),
        top_priority=analysis.get("top_priority", ""),
        lifestyle=analysis.get("lifestyle_notes", ""),
    )
    st.download_button(
        "⬇️ Download screening report (PDF)",
        data=pdf_bytes,
        file_name="MedBridge_Screening_Report.pdf",
        mime="application/pdf",
    )
