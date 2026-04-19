"""MedBridge AI - Your AI Healthcare Copilot.

Main Streamlit entrypoint. Provides sidebar navigation across a Home dashboard
and six feature modules, plus a shared Demo Mode toggle so the app works
even without an API key.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from modules import (
    form_fill,
    home,
    navigator,
    recovery_coach,
    screen_check,
    waitlist,
)
from utils.ai_engine import has_api_key

st.set_page_config(
    page_title="MedBridge AI - Your AI Healthcare Copilot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _inject_css() -> None:
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def _footer() -> None:
    st.markdown(
        """
        <div class='mb-footer'>
            ⚠️ Not medical advice - consult a licensed provider. Eligibility info is illustrative.
        </div>
        """,
        unsafe_allow_html=True,
    )


MODULES: dict[str, dict] = {
    "🏠 Home": {"render": home.render},
    "🧭 Navigator": {"render": navigator.render},
    "🩺 Screen Check": {"render": screen_check.render},
    "🏥 Recovery Coach": {"render": recovery_coach.render},
    "📋 FormFill": {"render": form_fill.render},
    "⏱️ Fast-Track": {"render": waitlist.render},
}


def _sidebar() -> str:
    with st.sidebar:
        st.markdown(
            """
            <div class='mb-brand'>
                <div class='mb-brand-logo'>🏥</div>
                <div>
                    <div class='mb-brand-title'>MedBridge AI</div>
                    <div class='mb-brand-sub'>Your AI Healthcare Copilot</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if "active_module" not in st.session_state:
            st.session_state.active_module = "🏠 Home"

        st.markdown("<div class='mb-nav-label'>Dashboard</div>", unsafe_allow_html=True)
        if st.session_state.active_module == "🏠 Home":
            st.markdown("<div class='mb-nav-active'>", unsafe_allow_html=True)
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            st.session_state.active_module = "🏠 Home"
        if st.session_state.active_module == "🏠 Home":
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='mb-nav-label' style='margin-top:12px'>Tools</div>", unsafe_allow_html=True)
        tool_keys = [k for k in MODULES if k != "🏠 Home"]
        for label in tool_keys:
            active = st.session_state.active_module == label
            if active:
                st.markdown("<div class='mb-nav-active'>", unsafe_allow_html=True)
            if st.button(label, key=f"nav_{label}", use_container_width=True):
                st.session_state.active_module = label
            if active:
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr class='mb-divider'/>", unsafe_allow_html=True)
        st.markdown("<div class='mb-nav-label'>Settings</div>", unsafe_allow_html=True)

        if "demo_mode" not in st.session_state:
            st.session_state.demo_mode = not has_api_key()
        st.session_state.demo_mode = st.toggle(
            "🎮 Demo Mode",
            value=st.session_state.demo_mode,
            help="Use pre-built responses instead of live Claude API calls. Works offline.",
        )

        if st.session_state.demo_mode:
            st.caption("🎮 Demo Mode · offline responses")
        elif not has_api_key():
            st.caption("⚠️ No API key · add to `.env`")
        else:
            st.caption("✅ Live API connected")

        st.markdown("<hr class='mb-divider'/>", unsafe_allow_html=True)

        with st.expander("ℹ️ About MedBridge AI"):
            st.markdown(
                """
**MedBridge AI** is an AI-powered healthcare copilot built for rural and
underserved communities in the Brazos Valley, Texas.

Built for the Texas A&M Healthcare Ideathon.
                """
            )

        st.markdown(
            "<div style='text-align:center; font-size:11px; color:#85929E; margin-top:10px'>"
            "v0.1 · Made with 💙 in Bryan, TX"
            "</div>",
            unsafe_allow_html=True,
        )

        return st.session_state.active_module


def main() -> None:
    _inject_css()
    active = _sidebar()
    render_fn = MODULES[active]["render"]
    render_fn()
    _footer()


if __name__ == "__main__":
    main()
