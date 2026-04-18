"""Module 5: Recovery Coach — turns discharge instructions into a daily plan."""

from __future__ import annotations

from typing import Any

import streamlit as st

from utils.ai_engine import (
    build_recovery_coach_system_prompt,
    call_claude,
    extract_json,
)
from utils.pdf_generator import generate_recovery_plan_pdf
from utils.ui import hero, section_label

SAMPLE_DISCHARGE = """DISCHARGE INSTRUCTIONS — St. Joseph Health Bryan

Patient: John Smith, 64 y/o male
Admitting diagnosis: Community-acquired pneumonia (right lower lobe)
Length of stay: 3 days

MEDICATIONS AT DISCHARGE:
1. Amoxicillin-clavulanate 875mg-125mg — 1 tablet by mouth twice daily for 7 days
2. Azithromycin 250mg — 1 tablet by mouth once daily for 4 more days
3. Guaifenesin 400mg — 1 tablet every 4 hours as needed for cough
4. Acetaminophen 500mg — up to every 6 hours for fever or aches (max 3000mg/day)

ACTIVITY:
- Rest for the first 3 days. Short walks around the house OK.
- Avoid strenuous activity for 2 weeks.
- Gradually increase walking distance after day 4 as tolerated.

DIET:
- Drink at least 8 glasses of water per day.
- Eat regular, nutritious meals.
- Avoid alcohol for 14 days.

WATCH FOR:
- Fever above 101°F returning
- Worsening shortness of breath
- Chest pain
- Coughing up blood
- Confusion

FOLLOW-UP:
- See your primary care physician in 7-10 days.
- Chest X-ray in 6 weeks to confirm resolution.

If you experience any emergency symptoms, call 911 immediately."""


def _demo_plan() -> dict[str, Any]:
    return {
        "condition": "Community-acquired pneumonia (recovery)",
        "overview": (
            "You are recovering from a lung infection. The first few days are about rest and fluids "
            "while your antibiotics do their job. Energy should slowly return over two weeks."
        ),
        "phases": [
            {
                "label": "Day 1-3 · Rest phase",
                "days": "1-3",
                "medications": [
                    {"name": "Amoxicillin-clavulanate", "dose": "875/125 mg", "schedule": "Twice daily (morning + evening) with food"},
                    {"name": "Azithromycin", "dose": "250 mg", "schedule": "Once daily, same time each day"},
                    {"name": "Guaifenesin", "dose": "400 mg", "schedule": "Every 4 hours as needed for cough"},
                    {"name": "Acetaminophen", "dose": "500 mg", "schedule": "Every 6 hours as needed for fever/aches (max 3000 mg/day)"},
                ],
                "activity": "Rest in bed or a chair. Short walks to the bathroom/kitchen only.",
                "diet": "Clear fluids + light meals. Aim for 8+ glasses of water. No alcohol.",
                "red_flags": ["Fever above 101°F returning", "Shortness of breath worsening", "Chest pain", "Coughing up blood"],
            },
            {
                "label": "Day 4-7 · Light activity phase",
                "days": "4-7",
                "medications": [
                    {"name": "Amoxicillin-clavulanate", "dose": "875/125 mg", "schedule": "Continue twice daily through day 7"},
                    {"name": "Guaifenesin", "dose": "400 mg", "schedule": "As needed for cough"},
                ],
                "activity": "Short walks 5-10 minutes, 2-3× a day. Avoid stairs if breathless.",
                "diet": "Regular meals — protein and vegetables to rebuild strength.",
                "red_flags": ["Fever returns", "Cough getting worse instead of better", "New confusion"],
            },
            {
                "label": "Day 8-14 · Gradual return to normal",
                "days": "8-14",
                "medications": [
                    {"name": "Acetaminophen", "dose": "500 mg", "schedule": "Only if needed for lingering aches"},
                ],
                "activity": "Normal daily activities. Add 20-30 minute walks. Avoid heavy lifting until week 3.",
                "diet": "Normal diet. Still no alcohol until day 14.",
                "red_flags": ["Fatigue not improving at all", "Any return of fever or productive cough"],
            },
        ],
        "follow_up": "Primary care visit in 7-10 days. Chest X-ray at 6 weeks to confirm lungs have cleared.",
        "emergency_symptoms": [
            "Severe shortness of breath",
            "Chest pain",
            "Coughing up blood",
            "Confusion or unable to stay awake",
            "Blue lips or fingertips",
        ],
    }


def _run_plan(discharge_text: str) -> dict[str, Any]:
    if st.session_state.get("demo_mode", False):
        return _demo_plan()
    try:
        raw = call_claude(build_recovery_coach_system_prompt(), discharge_text, max_tokens=2200)
        return extract_json(raw)
    except (RuntimeError, ValueError) as err:
        st.warning(f"Live analysis unavailable ({err}). Showing demo plan.")
        return _demo_plan()


def _checkin_response(status: str) -> str:
    return {
        "Better": "Great news. Keep the same routine — steady improvement is the goal. Stay on your medications until they're finished even if you feel back to normal.",
        "Same": "Recovery can plateau for a day or two — that's normal. Keep resting and hydrating. If you're still in the same spot in 48 hours, call your clinic.",
        "Worse": "Please call your doctor today. If you have any of the emergency symptoms listed below, call 911 — don't wait.",
        "New symptoms": "Write down what's new and when it started, then call your doctor. If it's on the emergency list (chest pain, severe shortness of breath, coughing blood, confusion), call 911 now.",
    }.get(status, "Tell me a bit more and I can guide you.")


def render() -> None:
    hero(
        icon="🏥",
        title="Recovery Coach",
        subtitle="Paste discharge instructions — I'll build a day-by-day plan you can follow.",
    )

    col_a, col_b = st.columns([1, 3])
    if col_a.button("📄 Load sample discharge", use_container_width=True):
        st.session_state.discharge_text = SAMPLE_DISCHARGE

    text = st.text_area(
        "Paste discharge instructions here",
        value=st.session_state.get("discharge_text", ""),
        height=240,
        placeholder="Discharge instructions from your hospital...",
    )

    if st.button("🏥 Build my recovery plan", type="primary"):
        if not text.strip():
            st.error("Please paste your discharge instructions or load the sample.")
            return
        with st.spinner("Building your day-by-day plan..."):
            st.session_state.recovery_plan = _run_plan(text)

    plan = st.session_state.get("recovery_plan")
    if not plan:
        return

    st.markdown("---")
    st.markdown(f"### 🏥 Recovering from: {plan.get('condition', '')}")
    st.info(plan.get("overview", ""))

    for idx, phase in enumerate(plan.get("phases", [])):
        with st.expander(phase.get("label", f"Phase {idx+1}"), expanded=(idx == 0)):
            meds = phase.get("medications", [])
            if meds:
                st.markdown("**💊 Medications**")
                for med in meds:
                    st.markdown(f"- **{med.get('name', '')}** {med.get('dose', '')} — {med.get('schedule', '')}")
            st.markdown(f"**🚶 Activity:** {phase.get('activity', '')}")
            st.markdown(f"**🍽️ Diet:** {phase.get('diet', '')}")
            red_flags = phase.get("red_flags", [])
            if red_flags:
                st.markdown("**⚠️ Watch for:**")
                for flag in red_flags:
                    st.markdown(f"- {flag}")

    st.markdown(f"**📅 Follow-up:** {plan.get('follow_up', '')}")
    st.markdown("#### 🚨 Call 911 if you have:")
    for sym in plan.get("emergency_symptoms", []):
        st.markdown(f"- {sym}")

    pdf_bytes = generate_recovery_plan_pdf(plan)
    st.download_button(
        "⬇️ Download recovery plan (PDF)",
        data=pdf_bytes,
        file_name="MedBridge_Recovery_Plan.pdf",
        mime="application/pdf",
    )

    st.markdown("---")
    st.markdown("### 📞 Daily check-in")
    st.write("How are you feeling today?")
    cols = st.columns(4)
    for idx, label in enumerate(["Better", "Same", "Worse", "New symptoms"]):
        if cols[idx].button(label, key=f"checkin_{label}", use_container_width=True):
            st.session_state.last_checkin = label
    if st.session_state.get("last_checkin"):
        response = _checkin_response(st.session_state.last_checkin)
        box_type = st.error if st.session_state.last_checkin in ("Worse", "New symptoms") else st.success
        box_type(response)
