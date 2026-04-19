"""Module 7: Waitlist Fast-Track - AI-powered triage, incentivized swapping,
live cancellation catcher, and pre-care monitoring."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from utils.ui import hero

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "waitlist.json"


def _load() -> dict[str, Any]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _init_state() -> None:
    st.session_state.setdefault("wl_data", _load())
    st.session_state.setdefault("wl_accepted_swaps", set())
    st.session_state.setdefault("wl_claimed_slot", None)
    st.session_state.setdefault("wl_precare_result", None)


def _acuity_badge(score: int) -> str:
    if score >= 9:
        cls, label = "mb-badge-danger", "Critical"
    elif score >= 7:
        cls, label = "mb-badge-warning", "High"
    elif score >= 5:
        cls, label = "mb-badge-info", "Moderate"
    else:
        cls, label = "mb-badge-ok", "Routine"
    return f"<span class='mb-badge {cls}'>{label} · {score}/10</span>"


def _render_overview(data: dict[str, Any]) -> None:
    clinic = data["clinic"]
    st.markdown(
        f"""
        <div class='mb-stats-row'>
            <div class='mb-stat'>
                <div class='mb-stat-value'>{clinic['next_standard_slot_days']} days</div>
                <div class='mb-stat-label'>Standard waitlist</div>
            </div>
            <div class='mb-stat'>
                <div class='mb-stat-value'>{clinic['cancellation_rate_pct']}%</div>
                <div class='mb-stat-label'>Cancellation rate</div>
            </div>
            <div class='mb-stat'>
                <div class='mb-stat-value'>{len(data['waitlist'])}</div>
                <div class='mb-stat-label'>High-acuity patients</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------- Tab 1: Smart Swap ---------------- #

def _recommend_swaps(routine: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = sorted(routine, key=lambda r: -r["flexibility_score"])
    return [
        {
            **r,
            "match_score": round(r["flexibility_score"] * 100),
        }
        for r in ranked[:3]
    ]


def _tab_swap(data: dict[str, Any]) -> None:
    waitlist = data["waitlist"]
    options = {f"{p['name']} · {p['condition'][:40]}": p for p in waitlist if p["acuity"] >= 7}
    chosen_label = st.selectbox("Who needs a faster appointment?", list(options.keys()))
    critical = options[chosen_label]

    st.markdown(
        f"""
        <div class='mb-card'>
            <h4>🆘 {critical['name']} · {critical['age']} y/o {_acuity_badge(critical['acuity'])}</h4>
            <p><b>{critical['condition']}</b></p>
            <p class='mb-muted'>Waiting {critical['days_waiting']} days · Currently scheduled {critical['scheduled_for']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🔎 Find swap candidates", type="primary", key="swap_find"):
        st.session_state.swap_recs = _recommend_swaps(data["routine_holders"])

    recs = st.session_state.get("swap_recs", [])
    if not recs:
        return

    st.markdown("#### AI-ranked swap candidates")
    for rec in recs:
        accepted = rec["id"] in st.session_state.wl_accepted_swaps
        status_badge = (
            "<span class='mb-badge mb-badge-ok'>Accepted</span>"
            if accepted
            else f"<span class='mb-badge mb-badge-info'>{rec['match_score']}% match</span>"
        )
        st.markdown(
            f"""
            <div class='mb-card'>
                <h4>{rec['name']} {status_badge}</h4>
                <p>{rec['visit_type']} · {rec['scheduled_for']} @ {rec['scheduled_time']}</p>
                <p class='mb-muted'>Offer: <b>{rec['preferred_reward']}</b></p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        cols = st.columns([1, 1, 4])
        if cols[0].button("📱 Send offer", key=f"send_{rec['id']}"):
            st.toast(f"Offer sent to {rec['name']}", icon="📬")
        if cols[1].button("✅ Accepted", key=f"accept_{rec['id']}"):
            st.session_state.wl_accepted_swaps.add(rec["id"])
            st.rerun()

    if st.session_state.wl_accepted_swaps:
        reclaimed = len(st.session_state.wl_accepted_swaps)
        st.success(f"🎉 {reclaimed} slot(s) freed - ~{reclaimed * 21} days earlier for {critical['name']}.")


# ---------------- Tab 2: Live Cancellation Catcher ---------------- #

def _tab_catcher(data: dict[str, Any]) -> None:
    ranked = sorted(data["waitlist"], key=lambda x: (-x["acuity"], -x["days_waiting"]))

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 🛰️ Live slot feed")
        for item in data["live_cancellations"]:
            st.markdown(
                f"""
                <div class='mb-card'>
                    <h4>🕒 {item['slot_time']}</h4>
                    <p class='mb-muted'>{item['canceled_by']} · {item['minutes_ago']} min ago</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with col_b:
        st.markdown("#### 🎯 Top waitlist picks")
        for i, p in enumerate(ranked[:3], 1):
            st.markdown(
                f"""
                <div class='mb-card'>
                    <h4>#{i} {p['name']} {_acuity_badge(p['acuity'])}</h4>
                    <p class='mb-muted'>Waiting {p['days_waiting']} days</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("#### Simulate a match")
    colx, coly, colz = st.columns([2, 2, 1])
    slot = colx.selectbox("Open slot", [c["slot_time"] for c in data["live_cancellations"]])
    target = coly.selectbox("Best match", [f"{p['name']} · {p['acuity']}/10" for p in ranked[:4]])
    if colz.button("⚡ Notify", type="primary", use_container_width=True):
        st.session_state.wl_claimed_slot = {"slot": slot, "patient": target, "ts": datetime.now().strftime("%H:%M:%S")}

    if st.session_state.wl_claimed_slot:
        info = st.session_state.wl_claimed_slot
        st.success(
            f"✅ Push sent at {info['ts']} · **{info['patient']}** → **{info['slot']}**. "
            f"5-minute window; auto-forwards if unacknowledged."
        )


# ---------------- Tab 3: Pre-Care Monitoring ---------------- #

def _escalation_logic(severity: int, trend: str, days: int) -> tuple[str, str, str]:
    if severity >= 7 or trend == "Worse":
        return (
            "ESCALATED",
            "Priority boosted - clinician notified.",
            "Symptoms are getting worse. I've escalated your file - the clinic will reach out within 24 hours with an earlier visit or telehealth today.",
        )
    if severity >= 4 or (trend == "Same" and days > 21):
        return (
            "WATCH",
            "Added to watch list - next check-in in 3 days.",
            "Hanging in there - thanks. I'll check in again in 3 days. Tap 'Escalate now' if anything gets worse.",
        )
    return (
        "STABLE",
        "Weekly cadence maintained.",
        "Holding steady - great. I'll see you again next week.",
    )


def _tab_precare(data: dict[str, Any]) -> None:
    waitlist = data["waitlist"]
    patient_labels = {f"{p['name']} · {p['condition'][:40]}": p for p in waitlist}
    selected_label = st.selectbox("Patient", list(patient_labels.keys()), key="precare_patient")
    patient = patient_labels[selected_label]

    st.markdown(
        f"""
        <div class='mb-card'>
            <h4>👤 {patient['name']} {_acuity_badge(patient['acuity'])}</h4>
            <p class='mb-muted'>Scheduled {patient['scheduled_for']} · Waiting {patient['days_waiting']} days</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("precare_form"):
        col1, col2 = st.columns(2)
        trend = col1.selectbox("Symptoms vs last week", ["Better", "Same", "Worse"], index=1)
        severity = col2.slider("How bad right now? (0–10)", 0, 10, 4)
        details = st.text_area("Anything new?", placeholder="e.g. swelling, fever, missed doses…", height=80)
        submitted = st.form_submit_button("📤 Submit check-in", type="primary")

    if submitted:
        status, priority_change, ai_message = _escalation_logic(severity, trend, patient["days_waiting"])
        st.session_state.wl_precare_result = {
            "patient": patient["name"],
            "status": status,
            "priority_change": priority_change,
            "ai_message": ai_message,
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    result = st.session_state.wl_precare_result
    if not result:
        return

    status_class = {
        "ESCALATED": "mb-badge-danger",
        "WATCH": "mb-badge-warning",
        "STABLE": "mb-badge-ok",
    }[result["status"]]
    st.markdown(
        f"""
        <div class='mb-card' style='border-left: 4px solid #1B4F72'>
            <h4>📬 {result['patient']} <span class='mb-badge {status_class}'>{result['status']}</span></h4>
            <p><b>{result['priority_change']}</b></p>
            <p class='mb-muted'>💬 {result['ai_message']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------- Tab 4: Full waitlist (tucked away) ---------------- #

def _tab_waitlist(data: dict[str, Any]) -> None:
    for p in sorted(data["waitlist"], key=lambda x: (-x["acuity"], -x["days_waiting"])):
        escalated_tag = " <span class='mb-badge mb-badge-danger'>Escalated</span>" if p.get("escalated") else ""
        st.markdown(
            f"""
            <div class='mb-card'>
                <h4>{p['name']} · {p['age']} y/o {_acuity_badge(p['acuity'])}{escalated_tag}</h4>
                <p>{p['condition']}</p>
                <p class='mb-muted'>Waiting {p['days_waiting']} days · {p['insurance']} · ZIP {p['zip']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------- Entrypoint ---------------- #

def render() -> None:
    hero(
        icon="⏱️",
        title="Waitlist Fast-Track",
        subtitle="AI triage that beats the 3-month wait - swap, catch cancellations, escalate when it matters.",
    )
    _init_state()
    data = st.session_state.wl_data

    _render_overview(data)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔄 Smart Swap",
        "⚡ Cancellation Catcher",
        "📉 Pre-Care Check-in",
        "🗂️ Full waitlist",
    ])
    with tab1:
        _tab_swap(data)
    with tab2:
        _tab_catcher(data)
    with tab3:
        _tab_precare(data)
    with tab4:
        _tab_waitlist(data)
