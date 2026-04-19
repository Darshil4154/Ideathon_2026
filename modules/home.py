"""Home / Dashboard - the polished landing page users see first."""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

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


# A self-contained HTML widget that uses the browser's native SpeechSynthesis
# API. Works offline, no API key, supports English + Spanish, and includes
# Stop / rate-slow controls for users who can't read the screen.
ACCESSIBILITY_WIDGET = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }
  .a11y-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    padding: 14px 20px;
    background: linear-gradient(135deg, #16A085 0%, #48C9B0 100%);
    border-radius: 16px;
    color: white;
    box-shadow: 0 10px 24px rgba(22, 160, 133, 0.25);
  }
  .a11y-label {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 700;
    font-size: 15px;
    margin-right: auto;
  }
  .a11y-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 34px; height: 34px;
    border-radius: 50%;
    background: rgba(255,255,255,0.2);
    font-size: 18px;
  }
  .a11y-bar button {
    background: #ffffff;
    color: #0E6251;
    border: none;
    border-radius: 999px;
    padding: 10px 18px;
    font-weight: 700;
    font-size: 14px;
    cursor: pointer;
    box-shadow: 0 4px 10px rgba(0,0,0,0.12);
    transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
    font-family: inherit;
  }
  .a11y-bar button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(0,0,0,0.18);
  }
  .a11y-bar button:focus-visible {
    outline: 3px solid #F4D03F;
    outline-offset: 2px;
  }
  .a11y-bar .stop {
    background: #FADBD8;
    color: #641E16;
  }
  .a11y-status {
    font-size: 12.5px;
    color: white;
    opacity: 0.92;
    min-height: 16px;
    width: 100%;
    text-align: right;
    padding-top: 4px;
  }
  @media (max-width: 700px) {
    .a11y-label { font-size: 14px; }
    .a11y-bar button { padding: 9px 14px; font-size: 13px; }
  }
</style>
</head>
<body>
<div class="a11y-bar" role="region" aria-label="Accessibility - listen to this page">
  <div class="a11y-label">
    <span class="a11y-icon" aria-hidden="true">♿</span>
    <span>Can't read the screen? Tap a button to hear it.</span>
  </div>
  <button type="button" aria-label="Listen in English" onclick="mbSpeak('en')">🔊 Listen (English)</button>
  <button type="button" aria-label="Escuchar en Espanol" onclick="mbSpeak('es')">🔊 Escuchar (Español)</button>
  <button type="button" class="stop" aria-label="Stop speaking" onclick="mbStop()">⏹ Stop</button>
  <div class="a11y-status" id="mb-status" aria-live="polite"></div>
</div>
<script>
  const TEXT = {
    en: "Welcome to MedBridge A.I., your healthcare helper for the Brazos Valley. " +
        "This app has five simple tools. Tap any tile below to get help. " +
        "Navigator finds doctors and programs that fit your situation. " +
        "Screen Check tells you which health tests you should get. " +
        "Recovery Coach turns hospital discharge papers into a day by day plan. " +
        "Form Fill helps you find insurance you qualify for. " +
        "Fast Track helps you get a clinic appointment sooner. " +
        "If you are having a medical emergency right now, call 9 1 1.",
    es: "Bienvenido a MedBridge A.I., su ayudante de salud para el Valle de Brazos. " +
        "Esta aplicacion tiene cinco herramientas simples. Toque cualquier mosaico para obtener ayuda. " +
        "El Navegador encuentra medicos y programas que le convienen. " +
        "Chequeo Preventivo le dice que examenes de salud debe hacerse. " +
        "El Entrenador de Recuperacion convierte los papeles del hospital en un plan diario. " +
        "Form Fill le ayuda a encontrar seguro medico para el que califica. " +
        "Fast Track le ayuda a conseguir una cita en la clinica mas rapido. " +
        "Si tiene una emergencia medica ahora, llame al 9 1 1."
  };

  function setStatus(msg) {
    const el = document.getElementById('mb-status');
    if (el) el.textContent = msg;
  }

  function mbStop() {
    try { window.speechSynthesis.cancel(); } catch (e) {}
    setStatus('');
  }

  function mbSpeak(lang) {
    if (!('speechSynthesis' in window)) {
      setStatus('Sorry, your browser does not support spoken audio.');
      return;
    }
    mbStop();
    const utter = new SpeechSynthesisUtterance(TEXT[lang]);
    utter.lang = lang === 'es' ? 'es-MX' : 'en-US';
    utter.rate = 0.92;
    utter.pitch = 1.0;
    utter.volume = 1.0;
    utter.onstart = () => setStatus(lang === 'es' ? '🔊 Hablando...' : '🔊 Speaking...');
    utter.onend   = () => setStatus('');
    utter.onerror = () => setStatus(lang === 'es' ? 'No se pudo reproducir el audio.' : 'Could not play audio.');
    window.speechSynthesis.speak(utter);
  }

  // Stop speech when the page unloads so it doesn't keep talking after a rerun.
  window.addEventListener('beforeunload', mbStop);
</script>
</body>
</html>
"""


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
                <b>Medical emergency?</b> Call <b>911</b> or go to the nearest ER -
                <b>St. Joseph Health Bryan</b>, (979) 776-3777.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render() -> None:
    # Accessibility bar - read the page aloud in English or Spanish.
    components.html(ACCESSIBILITY_WIDGET, height=110)

    hero(
        icon="🏥",
        title="Welcome to MedBridge AI",
        subtitle="Your healthcare copilot for the Brazos Valley - find care, fight bills, stay safe.",
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
