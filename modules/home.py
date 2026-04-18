"""Home / Dashboard — the polished landing page users see first."""

from __future__ import annotations

import streamlit as st

from utils.ui import hero

MODULE_TILES = [
    {
        "key": "🧭 Navigator",
        "icon": "🧭",
        "title": "Navigator",
        "desc": "Find programs that match your situation.",
    },
    {
        "key": "🩺 Screen Check",
        "icon": "🩺",
        "title": "Screen Check",
        "desc": "Personalized preventive screening plan.",
    },
    {
        "key": "🏥 Recovery Coach",
        "icon": "🏥",
        "title": "Recovery Coach",
        "desc": "Day-by-day plan from discharge notes.",
    },
    {
        "key": "📋 FormFill",
        "icon": "📋",
        "title": "FormFill",
        "desc": "Find insurance you qualify for.",
    },
    {
        "key": "⏱️ Fast-Track",
        "icon": "⏱️",
        "title": "Fast-Track",
        "desc": "Skip the 3-month waitlist.",
    },
]


def _stats_row() -> None:
    st.markdown(
        """
        <div class='mb-stats-row'>
            <div class='mb-stat'>
                <div class='mb-stat-value'>5</div>
                <div class='mb-stat-label'>AI-powered tools</div>
            </div>
            <div class='mb-stat'>
                <div class='mb-stat-value'>12+</div>
                <div class='mb-stat-label'>Local programs mapped</div>
            </div>
            <div class='mb-stat'>
                <div class='mb-stat-value'>94 → 0</div>
                <div class='mb-stat-label'>Days of waitlist cut</div>
            </div>
            <div class='mb-stat'>
                <div class='mb-stat-value'>100%</div>
                <div class='mb-stat-label'>Works offline</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_emergency() -> None:
    st.markdown(
        """
        <div class='mb-emergency'>
            <div class='mb-emergency-icon'>🚨</div>
            <div>
                <b>Medical emergency?</b> Call <b>911</b> or go to the nearest ER —
                <b>St. Joseph Health Bryan</b>, (979) 776-3777.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render() -> None:
    hero(
        icon="🏥",
        title="Welcome to MedBridge AI",
        subtitle="Your healthcare copilot for the Brazos Valley — find care, fight bills, stay safe.",
    )

    _stats_row()

    st.markdown("### What do you want to do today?")

    for row_start in range(0, len(MODULE_TILES), 3):
        row = MODULE_TILES[row_start : row_start + 3]
        cols = st.columns(3, gap="small")
        for i, tile in enumerate(row):
            with cols[i]:
                st.markdown(
                    f"""
                    <div class='mb-tile'>
                        <div class='mb-tile-icon'>{tile['icon']}</div>
                        <div class='mb-tile-title'>{tile['title']}</div>
                        <div class='mb-tile-desc'>{tile['desc']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Open", key=f"home_open_{tile['key']}", use_container_width=True):
                    st.session_state.active_module = tile["key"]
                    st.rerun()

    st.markdown("<br/>", unsafe_allow_html=True)
    _render_emergency()
