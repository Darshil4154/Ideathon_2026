"""Module 6: Insurance FormFill - conversational eligibility + pre-filled application."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from utils.ai_engine import (
    build_formfill_system_prompt,
    call_claude,
    extract_json,
)
from utils.ui import hero

QUESTIONS = [
    {"key": "name", "text": "What's your name? (This goes on your application summary.)", "kind": "text", "placeholder": "First Last"},
    {"key": "state", "text": "What state do you live in?", "kind": "text", "placeholder": "Texas"},
    {"key": "household", "text": "How many people are in your household?", "kind": "number", "min": 1, "max": 15},
    {"key": "income", "text": "What is your approximate annual household income (in US dollars)?", "kind": "number", "min": 0, "max": 500000},
    {"key": "insurance", "text": "Do you currently have any health insurance?", "kind": "select", "options": ["No, I'm uninsured", "Yes - employer plan", "Yes - Medicaid/CHIP", "Yes - Medicare", "Yes - Marketplace plan", "Other"]},
    {"key": "family_status", "text": "Are you pregnant or do you have children under 19?", "kind": "select", "options": ["No", "Yes - pregnant", "Yes - children under 19", "Yes - both"]},
    {"key": "disability", "text": "Do you have a disability that affects your ability to work?", "kind": "select", "options": ["No", "Yes", "Applying for SSDI/SSI"]},
    {"key": "age", "text": "What is your age?", "kind": "number", "min": 0, "max": 120},
]

FPL_2025 = {1: 15060, 2: 20440, 3: 25820, 4: 31200, 5: 36580, 6: 41960, 7: 47340, 8: 52720}


def _fpl(household_size: int) -> int:
    if household_size <= 8:
        return FPL_2025[household_size]
    return FPL_2025[8] + (household_size - 8) * 5380


def _percent_fpl(income: float, household: int) -> float:
    base = _fpl(household)
    if base == 0:
        return 0
    return round(100 * income / base, 1)


def _demo_analysis(answers: dict[str, Any]) -> dict[str, Any]:
    household = int(answers.get("household", 1) or 1)
    income = float(answers.get("income", 0) or 0)
    age = int(answers.get("age", 0) or 0)
    pct = _percent_fpl(income, household)
    has_kids_or_pregnant = "Yes" in str(answers.get("family_status", ""))
    disabled = str(answers.get("disability", "")).startswith("Yes") or "SSDI" in str(answers.get("disability", ""))

    eligibility = []
    if age >= 65 or disabled:
        eligibility.append({
            "program": "Medicare",
            "likely_qualifies": True,
            "reason": ("You are 65 or older - Medicare enrollment is automatic for many and essential for the rest."
                       if age >= 65 else "People receiving SSDI for 24+ months qualify for Medicare regardless of age."),
            "how_to_apply": "Apply at ssa.gov or call 1-800-772-1213.",
        })

    if has_kids_or_pregnant and pct <= 200:
        eligibility.append({
            "program": "Medicaid / CHIP",
            "likely_qualifies": True,
            "reason": f"You have children or are pregnant, with household income at about {pct}% of the Federal Poverty Level - you likely qualify in Texas.",
            "how_to_apply": "Apply at yourtexasbenefits.com or dial 2-1-1 for a navigator.",
        })
    elif pct <= 138 and disabled:
        eligibility.append({
            "program": "Medicaid (disability pathway)",
            "likely_qualifies": True,
            "reason": f"Income around {pct}% of FPL plus a disability typically qualifies for Texas Medicaid.",
            "how_to_apply": "Apply at yourtexasbenefits.com or dial 2-1-1.",
        })

    if pct <= 400 and age < 65:
        eligibility.append({
            "program": "Healthcare.gov Marketplace (ACA) with subsidies",
            "likely_qualifies": True,
            "reason": f"At ~{pct}% FPL, you qualify for premium tax credits - in many cases reducing monthly premiums to very low or $0 levels.",
            "how_to_apply": "Enroll at healthcare.gov or call 1-800-318-2596.",
        })

    if not eligibility:
        eligibility.append({
            "program": "Healthcare.gov Marketplace (ACA)",
            "likely_qualifies": True,
            "reason": "You can still buy a Marketplace plan at full price - and revisit subsidies if your income changes.",
            "how_to_apply": "healthcare.gov",
        })

    next_steps = [
        "Gather documents: photo ID, Social Security numbers, pay stubs or tax return, proof of Texas residence.",
        "Start with 2-1-1 (Texas HHSC navigator) - one call covers Medicaid, CHIP, and SNAP screening.",
        "If you don't qualify for Medicaid, move to healthcare.gov the same week to lock in a Marketplace plan.",
    ]

    summary_text = (
        f"Name: {answers.get('name', '')}\n"
        f"State: {answers.get('state', '')}\n"
        f"Household size: {household}\n"
        f"Annual household income: ${income:,.0f}\n"
        f"% of Federal Poverty Level: {pct}%\n"
        f"Current insurance: {answers.get('insurance', '')}\n"
        f"Family status: {answers.get('family_status', '')}\n"
        f"Disability: {answers.get('disability', '')}\n"
        f"Age: {age}\n\n"
        "Likely programs:\n"
        + "\n".join(f" - {item['program']} - {item['reason']}" for item in eligibility)
        + "\n\nPrepared: " + datetime.today().strftime("%B %d, %Y")
    )

    return {
        "eligibility": eligibility,
        "next_steps": next_steps,
        "application_summary": summary_text,
    }


def _run_analysis(answers: dict[str, Any]) -> dict[str, Any]:
    if st.session_state.get("demo_mode", False):
        return _demo_analysis(answers)
    try:
        raw = call_claude(
            build_formfill_system_prompt(),
            f"Household answers: {answers}",
            max_tokens=1500,
        )
        return extract_json(raw)
    except (RuntimeError, ValueError) as err:
        st.warning(f"Live analysis unavailable ({err}). Showing demo analysis.")
        return _demo_analysis(answers)


def render() -> None:
    hero(
        icon="📋",
        title="Insurance FormFill",
        subtitle="Answer 8 quick questions - I'll find the insurance programs you qualify for.",
    )

    if "formfill_answers" not in st.session_state:
        st.session_state.formfill_answers = {}
    if "formfill_step" not in st.session_state:
        st.session_state.formfill_step = 0

    step = st.session_state.formfill_step
    total = len(QUESTIONS)
    st.progress(min(step / total, 1.0), text=f"Question {min(step+1, total)} of {total}")

    if step < total:
        q = QUESTIONS[step]
        st.markdown(f"#### {q['text']}")
        value: Any = None
        if q["kind"] == "text":
            value = st.text_input("Your answer", key=f"ff_{q['key']}", placeholder=q.get("placeholder", ""), label_visibility="collapsed")
        elif q["kind"] == "number":
            value = st.number_input(
                "Your answer",
                min_value=q.get("min", 0),
                max_value=q.get("max", 1_000_000),
                step=1,
                key=f"ff_{q['key']}",
                label_visibility="collapsed",
            )
        elif q["kind"] == "select":
            value = st.selectbox("Your answer", q["options"], key=f"ff_{q['key']}", label_visibility="collapsed")

        col_a, col_b = st.columns([1, 1])
        if col_a.button("⬅️ Back", disabled=(step == 0), use_container_width=True):
            st.session_state.formfill_step = max(0, step - 1)
            st.rerun()
        if col_b.button("Next ➡️", type="primary", use_container_width=True):
            if q["kind"] == "text" and not str(value).strip():
                st.error("Please enter an answer.")
            else:
                st.session_state.formfill_answers[q["key"]] = value
                st.session_state.formfill_step = step + 1
                st.rerun()
        return

    # Done - run analysis
    answers = st.session_state.formfill_answers
    with st.spinner("Matching programs based on your answers..."):
        result = _run_analysis(answers)

    st.markdown("### ✅ Based on your answers, you likely qualify for:")
    for item in result.get("eligibility", []):
        st.markdown(
            f"""
            <div class='mb-card'>
              <h4>{item.get('program', '')}</h4>
              <p><b>Why:</b> {item.get('reason', '')}</p>
              <p><b>How to apply:</b> {item.get('how_to_apply', '')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    steps = result.get("next_steps", [])
    if steps:
        st.markdown("### 📋 Next steps")
        for idx, s in enumerate(steps, 1):
            st.markdown(f"**{idx}.** {s}")

    summary_text = result.get("application_summary", "")
    st.markdown("### 📄 Your pre-filled application summary")
    st.text_area("Summary", summary_text, height=300, label_visibility="collapsed")

    if st.button("🔄 Start over"):
        st.session_state.formfill_answers = {}
        st.session_state.formfill_step = 0
        st.rerun()
