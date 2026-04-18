"""Module 1: AI Health Navigator — conversational program-matching chat."""

from __future__ import annotations

import re
from urllib.parse import quote_plus

import streamlit as st

from utils.ai_engine import (
    build_navigator_system_prompt,
    call_claude_chat,
    load_programs,
)
from utils.ui import hero, section_label

EMERGENCY_KEYWORDS = [
    "chest pain",
    "can't breathe",
    "cant breathe",
    "difficulty breathing",
    "short of breath",
    "severe bleeding",
    "stroke",
    "heart attack",
    "unconscious",
    "suicide",
    "overdose",
]


def _is_emergency(text: str) -> bool:
    text_l = text.lower()
    return any(kw in text_l for kw in EMERGENCY_KEYWORDS)


def _emergency_banner() -> None:
    st.markdown(
        """
        <div class='mb-emergency'>
        🚨 <b>This sounds like a medical emergency.</b><br/>
        <b>Call 911 immediately</b> or go to the nearest emergency room:<br/>
        <b>St. Joseph Health Bryan</b> — 2801 Franciscan Dr, Bryan, TX 77802 · (979) 776-3777
        </div>
        """,
        unsafe_allow_html=True,
    )


def _demo_response(user_message: str) -> tuple[str, list[str]]:
    """Deterministic demo response used when Demo Mode is on or API key missing."""
    text_l = user_message.lower()
    text = (
        "I hear you — let me find some options close to you.\n\n"
        "Based on what you shared, here are programs that could help right away:\n\n"
    )
    matched: list[str] = []
    if any(k in text_l for k in ["diabet", "insulin", "medication", "prescription", "medicine", "meds"]):
        text += (
            "### 🏥 Brazos Valley Community Health Center (FQHC)\n"
            "- **Why this fits:** They treat uninsured patients on a sliding scale and have an in-house 340B pharmacy, so your diabetes medications can be deeply discounted.\n"
            "- **Next step:** Call **(979) 774-4515** and say you are uninsured with diabetes and need to establish care. Bring a photo ID and proof of income (pay stub or tax return) if you have one.\n\n"
            "### 💊 340B Drug Pricing Program\n"
            "- **Why this fits:** Once you are a BVCHC patient, you can fill prescriptions at the 340B rate — often 50-80% cheaper.\n"
            "- **Next step:** Ask your BVCHC provider to route prescriptions to the BVCHC pharmacy.\n\n"
        )
        matched += ["bvchc", "340b-pharmacy"]
    if any(k in text_l for k in ["uninsur", "no insurance", "can't afford", "cannot afford"]):
        text += (
            "### 📋 Texas Health and Human Services (Medicaid / CHIP)\n"
            "- **Why this fits:** Depending on your household income and situation (children, pregnancy, or disability), you may qualify for Medicaid or CHIP at no or low cost.\n"
            "- **Next step:** Apply online at yourtexasbenefits.com or call **2-1-1**.\n\n"
            "### 🛒 Healthcare.gov Marketplace\n"
            "- **Why this fits:** If you don't qualify for Medicaid, enhanced ACA subsidies can reduce premiums to $0–$50/month for many households.\n"
            "- **Next step:** Visit healthcare.gov or call **(800) 318-2596**.\n\n"
        )
        matched += ["tx-hhsc", "healthcare-gov"]
    if any(k in text_l for k in ["bill", "debt", "collection", "can't pay", "owe"]):
        text += (
            "### ⚖️ Lone Star Legal Aid\n"
            "- **Why this fits:** They provide free legal help for medical debt and insurance disputes for low-income Texans.\n"
            "- **Next step:** Call **(979) 775-5050**.\n\n"
        )
        matched.append("lonestar-legal")
    if any(k in text_l for k in ["food", "hungry", "snap"]):
        text += (
            "### 🥫 Brazos Valley Food Bank\n"
            "- **Why this fits:** Free emergency food and help applying for SNAP (food stamps).\n"
            "- **Next step:** Call **(979) 779-3663**.\n\n"
        )
        matched.append("bv-foodbank")

    if not matched:
        text += (
            "### 🏥 Brazos Valley Community Health Center (FQHC)\n"
            "- **Why this fits:** A great first stop for almost any health concern — they see patients regardless of insurance and have primary care, pediatrics, dental, and behavioral health in one building.\n"
            "- **Next step:** Call **(979) 774-4515** to schedule.\n\n"
            "### 📋 Texas Health and Human Services\n"
            "- **Why this fits:** Helps enroll in Medicaid, CHIP, or SNAP based on your household.\n"
            "- **Next step:** Dial **2-1-1** for a live navigator.\n\n"
        )
        matched += ["bvchc", "tx-hhsc"]

    text += "**You don't have to figure this out alone — one call today is a real step forward.** 💙"
    return text, matched


def _match_programs(ids: list[str]) -> list[dict]:
    programs = load_programs()
    id_set = {i.strip() for i in ids if i.strip()}
    # preserve the order returned by the model
    by_id = {p["id"]: p for p in programs}
    result = [by_id[i] for i in ids if i in by_id]
    # de-dupe while preserving order
    seen = set()
    unique = []
    for p in result:
        if p["id"] in seen:
            continue
        seen.add(p["id"])
        unique.append(p)
    return unique


def _extract_matched_ids(text: str) -> tuple[str, list[str]]:
    """Pull the 'MATCHED_IDS: ...' trailer line out of a model response."""
    match = re.search(r"MATCHED_IDS:\s*([a-zA-Z0-9,\-\s_]+)\s*$", text)
    if not match:
        return text, []
    ids = [s.strip() for s in match.group(1).split(",") if s.strip()]
    cleaned = text[: match.start()].rstrip()
    return cleaned, ids


def _render_program_card(program: dict) -> None:
    maps_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(program['address'])}"
    with st.expander(f"📍 {program['name']} — {program['type']}"):
        col_a, col_b = st.columns([3, 2])
        with col_a:
            st.markdown(f"**Address:** {program['address']}")
            st.markdown(f"**Phone:** {program['phone']}")
            st.markdown(f"**Hours:** {program.get('hours', 'Call for hours')}")
            st.markdown(f"**Services:** {', '.join(program.get('services', []))}")
            st.markdown(f"**Languages:** {', '.join(program.get('languages', ['English']))}")
            st.markdown(f"**Eligibility:** {program['eligibility']}")
        with col_b:
            st.link_button("🌐 Visit Website", program.get("website", "#"), use_container_width=True)
            st.link_button("🗺️ Get Directions", maps_url, use_container_width=True)


def render() -> None:
    hero(
        icon="🧭",
        title="AI Health Navigator",
        subtitle="Describe your situation — I'll match you to real Brazos Valley programs you qualify for.",
    )

    if "nav_history" not in st.session_state:
        st.session_state.nav_history = []
    if "nav_matched" not in st.session_state:
        st.session_state.nav_matched = []

    with st.expander("💡 Not sure what to say? Try an example"):
        examples = [
            "I'm uninsured, have diabetes, and live in Bryan TX. I can't afford my medication.",
            "I got a $4,000 hospital bill and I don't know how to pay it. I make $2,000/month.",
            "I'm pregnant, 22 years old, no insurance. What do I do?",
            "My dad is a rural farmer in Burleson County with high blood pressure. He hates driving into town.",
        ]
        cols = st.columns(2)
        for i, ex in enumerate(examples):
            if cols[i % 2].button(ex, key=f"ex_{i}", use_container_width=True):
                st.session_state._nav_seed = ex

    # Render chat history
    for turn in st.session_state.nav_history:
        with st.chat_message(turn["role"]):
            st.markdown(turn["display"])

    seed = st.session_state.pop("_nav_seed", None)
    user_input = st.chat_input("Describe your situation in your own words...")
    if seed and not user_input:
        user_input = seed

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.nav_history.append({"role": "user", "content": user_input, "display": user_input})

        if _is_emergency(user_input):
            _emergency_banner()

        with st.chat_message("assistant"):
            placeholder = st.empty()
            with st.spinner("Finding programs that match your situation..."):
                try:
                    if st.session_state.get("demo_mode", False):
                        reply, matched_ids = _demo_response(user_input)
                    else:
                        raw = call_claude_chat(
                            build_navigator_system_prompt(),
                            [{"role": t["role"], "content": t["content"]} for t in st.session_state.nav_history],
                            max_tokens=1500,
                        )
                        reply, matched_ids = _extract_matched_ids(raw)
                except RuntimeError as err:
                    st.error(str(err))
                    st.info("Switching to Demo Mode response so you can continue.")
                    reply, matched_ids = _demo_response(user_input)
            placeholder.markdown(reply)

        st.session_state.nav_history.append({"role": "assistant", "content": reply, "display": reply})
        st.session_state.nav_matched = matched_ids

    # Matched programs
    if st.session_state.nav_matched:
        st.markdown("<br/>", unsafe_allow_html=True)
        section_label("Matched programs")
        st.markdown("### 🎯 Programs matched to your situation")
        for program in _match_programs(st.session_state.nav_matched):
            _render_program_card(program)

    if st.session_state.nav_history:
        if st.button("🔄 Start a new conversation", use_container_width=False):
            st.session_state.nav_history = []
            st.session_state.nav_matched = []
            st.rerun()
