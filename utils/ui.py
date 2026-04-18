"""Reusable UI primitives so every module has a consistent, polished look."""

from __future__ import annotations

import streamlit as st


def hero(icon: str, title: str, subtitle: str) -> None:
    """Full-width gradient hero shown at the top of every page."""
    st.markdown(
        f"""
        <div class='mb-hero'>
            <div class='mb-hero-inner'>
                <div class='mb-hero-icon'>{icon}</div>
                <div>
                    <h1>{title}</h1>
                    <p>{subtitle}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    st.markdown(f"<span class='mb-section-label'>{text}</span>", unsafe_allow_html=True)


def card(title: str, body_html: str) -> None:
    st.markdown(
        f"<div class='mb-card'><h4>{title}</h4>{body_html}</div>",
        unsafe_allow_html=True,
    )


def tile_button(col, icon: str, title: str, desc: str, cta: str, key: str) -> bool:
    """Render a dashboard tile that behaves like a button. Returns True when clicked."""
    with col:
        st.markdown(
            f"""
            <div class='mb-tile'>
                <div class='mb-tile-icon'>{icon}</div>
                <div class='mb-tile-title'>{title}</div>
                <div class='mb-tile-desc'>{desc}</div>
                <div class='mb-tile-cta'>{cta} →</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return st.button("Open", key=key, use_container_width=True)


def metric_tile(label: str, value: str, *, tone: str = "primary") -> str:
    """Return the HTML for a branded metric tile (call with unsafe_allow_html)."""
    return f"""
    <div class='mb-metric'>
        <div class='mb-metric-label'>{label}</div>
        <div class='mb-metric-value'>{value}</div>
    </div>
    """
