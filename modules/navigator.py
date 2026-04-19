"""Module 1: AI Health Navigator - conversational program-matching chat.

Plain-language examples anyone can understand, a floating chatbot bubble at
the bottom-right, and live OpenRouter / Anthropic responses.
"""

from __future__ import annotations

import re
from urllib.parse import quote_plus

import streamlit as st

from utils.ai_engine import (
    build_navigator_system_prompt,
    call_claude_chat,
    load_programs,
)
from utils.ui import hero

# ---------- Plain-language example questions ---------- #

EXAMPLE_QUESTIONS = [
    "I can't afford to see a doctor",
    "I don't have any insurance",
    "My medicine is too expensive",
    "I got a really big hospital bill",
    "I'm pregnant and need help",
    "My kid is sick and we're uninsured",
    "I live far from a clinic",
    "I'm diabetic and running out of pills",
]

EMERGENCY_KEYWORDS = [
    "chest pain", "can't breathe", "cant breathe", "difficulty breathing",
    "short of breath", "severe bleeding", "stroke", "heart attack",
    "unconscious", "suicide", "overdose",
]

def _render_chatbot_fab() -> None:
    """Floating round chatbot bubble pinned to the bottom-right of the page."""
    st.markdown(
        """
        <div class="mb-chatbot-fab" title="How can I help?">
            <div class="mb-chatbot-icon">💬</div>
            <div class="mb-chatbot-label">How can I help?</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------- State helpers ---------- #

def _init_state() -> None:
    st.session_state.setdefault("nav_history", [])
    st.session_state.setdefault("nav_matched", [])


def _is_emergency(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in EMERGENCY_KEYWORDS)


def _extract_matched_ids(text: str) -> tuple[str, list[str]]:
    match = re.search(r"MATCHED_IDS:\s*([a-zA-Z0-9,\-\s_]+)\s*$", text)
    if not match:
        return text, []
    ids = [s.strip() for s in match.group(1).split(",") if s.strip()]
    return text[: match.start()].rstrip(), ids


def _match_programs(ids: list[str]) -> list[dict]:
    by_id = {p["id"]: p for p in load_programs()}
    seen: set[str] = set()
    out: list[dict] = []
    for i in ids:
        if i in by_id and i not in seen:
            seen.add(i)
            out.append(by_id[i])
    return out


def _demo_response(text: str) -> tuple[str, list[str]]:
    """Simple fallback used when Demo Mode is on or API fails."""
    t = text.lower()
    reply = "I hear you. Here are some places in the Brazos Valley that can help:\n\n"
    matched: list[str] = []
    if any(k in t for k in ["diabet", "pill", "medicine", "prescription", "medication"]):
        reply += (
            "### 🏥 Brazos Valley Community Health Center\n"
            "- They see patients who don't have insurance, and bills are based on what you can pay.\n"
            "- **Call (979) 774-4515** - tell them you need help with your medicine.\n\n"
        )
        matched += ["bvchc", "340b-pharmacy"]
    if any(k in t for k in ["insurance", "uninsured", "afford"]):
        reply += (
            "### 📋 Texas 2-1-1 (free help line)\n"
            "- Dial **2-1-1** - a real person helps you apply for Medicaid, CHIP, or food help.\n\n"
        )
        matched.append("tx-hhsc")
    if any(k in t for k in ["bill", "debt", "owe"]):
        reply += (
            "### ⚖️ Lone Star Legal Aid\n"
            "- Free legal help for medical bills if you can't afford to pay.\n"
            "- **Call (979) 775-5050**\n\n"
        )
        matched.append("lonestar-legal")
    if not matched:
        reply += (
            "### 🏥 Brazos Valley Community Health Center\n"
            "- A good first call for almost any health concern.\n"
            "- **(979) 774-4515**\n\n"
        )
        matched = ["bvchc", "tx-hhsc"]
    reply += "**One call today is a real step forward. You're not alone.** 💙"
    return reply, matched


# ---------- UI pieces ---------- #

def _emergency_banner() -> None:
    st.markdown(
        """
        <div class='mb-emergency'>
            <div class='mb-emergency-icon'>🚨</div>
            <div>
                <b>This sounds like a medical emergency.</b><br/>
                <b>Call 911 now</b> - or go to St. Joseph Health Bryan, 2801 Franciscan Dr · (979) 776-3777
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_examples() -> None:
    st.markdown("<div class='nav-examples-label'>Tap a question to start - or type your own below 👇</div>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, ex in enumerate(EXAMPLE_QUESTIONS):
        if cols[i % 2].button(ex, key=f"nav_ex_{i}", use_container_width=True):
            st.session_state._nav_seed = ex
            st.rerun()




def _render_program_card(program: dict) -> None:
    maps_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(program['address'])}"
    with st.expander(f"📍 {program['name']}"):
        st.markdown(f"**Phone:** {program['phone']}")
        st.markdown(f"**Address:** {program['address']}")
        st.markdown(f"**Hours:** {program.get('hours', 'Call for hours')}")
        st.markdown(f"**Who it helps:** {program['eligibility']}")
        col_a, col_b = st.columns(2)
        col_a.link_button("🌐 Website", program.get("website", "#"), use_container_width=True)
        col_b.link_button("🗺️ Directions", maps_url, use_container_width=True)


# ---------- Main render ---------- #

def render() -> None:
    hero(
        icon="🧭",
        title="AI Health Navigator",
        subtitle="Describe your situation in your own words - I'll find help for you.",
    )

    _init_state()

    # --- Handle input first so state updates before we render ---
    seed = st.session_state.pop("_nav_seed", None)
    typed = st.chat_input("Ask me anything - like \"I can't afford my medicine\" or \"I need a doctor near me\"…")
    user_input = typed or seed

    if user_input:
        if _is_emergency(user_input):
            _emergency_banner()
        st.session_state.nav_history.append({"role": "user", "content": user_input})
        with st.spinner("Finding the best help for you…"):
            try:
                if st.session_state.get("demo_mode", False):
                    reply, ids = _demo_response(user_input)
                else:
                    raw = call_claude_chat(
                        build_navigator_system_prompt(),
                        [{"role": t["role"], "content": t["content"]} for t in st.session_state.nav_history],
                        max_tokens=1500,
                    )
                    reply, ids = _extract_matched_ids(raw)
            except RuntimeError as err:
                st.error(str(err))
                reply, ids = _demo_response(user_input)
        st.session_state.nav_history.append({"role": "assistant", "content": reply})
        st.session_state.nav_matched = ids

    # --- Full-width chat area ---
    if not st.session_state.nav_history:
        _render_examples()
    else:
        for turn in st.session_state.nav_history:
            with st.chat_message(turn["role"]):
                st.markdown(turn["content"])

        if st.session_state.nav_matched:
            st.markdown("### 🎯 Programs for you")
            for program in _match_programs(st.session_state.nav_matched):
                _render_program_card(program)

        if st.button("🔄 Start a new question"):
            st.session_state.nav_history = []
            st.session_state.nav_matched = []
            st.rerun()

    _render_chatbot_fab()
