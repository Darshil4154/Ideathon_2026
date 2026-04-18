# MedBridge AI — Your AI Healthcare Copilot

**An AI-powered healthcare navigator for rural and underserved communities in the Brazos Valley, Texas.**

MedBridge AI is a no-code, Claude-powered Streamlit app that helps patients find assistance programs, catch medical billing errors, check medications for dangerous interactions, stay on top of preventive screenings, recover safely after discharge, and apply for public insurance — all through plain-language conversations.

Built for the Texas A&M healthcare ideathon.

---

## ✨ What's in the app

| # | Module | What it does |
|---|--------|--------------|
| 1 | 🧭 **AI Health Navigator** | Conversational chat that matches the user's situation to real Brazos Valley healthcare programs (FQHCs, charity care, 340B pharmacies, Medicaid, ACA). Emergency-symptom detection is built in. |
| 2 | 🩺 **Preventive Screen Check** | Builds a personalized USPSTF-based screening timeline (Plotly), tailored to age, sex, smoking status, family history, and conditions. |
| 3 | 🏥 **Recovery Coach** | Turns hospital discharge instructions into a clear day-by-day recovery plan, with daily check-ins and PDF export. |
| 4 | 📋 **Insurance FormFill** | Plain-English Q&A that screens households for Medicaid, CHIP, ACA subsidies, and Medicare, and outputs a pre-filled PDF application summary. |
| 5 | ⏱️ **Waitlist Fast-Track** | Bypasses the 3-month waitlist via predictive AI triage — incentivized appointment swapping, live cancellation catching with push notifications, and weekly pre-care check-ins that auto-escalate priority when symptoms worsen. |

### 🔎 Module 5 deep-dive — Waitlist Fast-Track

Finding a clinic means nothing if the next appointment is 4 months away. Fast-Track dynamically reorganizes the clinic's calendar so high-acuity patients get seen first.

- 🔄 **Incentivized Swapping** — AI scans the clinic's calendar for patients with routine checkups, ranks them by flexibility score, and sends a personalized SMS offering a reward (e.g. "$15 pharmacy credit") to move their slot. One tap frees an earlier appointment for a critical patient.
- ⚡ **Live Cancellation Catcher** — The millisecond a slot opens, the AI ranks the waitlist by medical vulnerability and fires a push notification to the best-matched patient with a 5-minute acceptance window. If unacknowledged, it auto-forwards to the next person.
- 📉 **Pre-Care Monitoring** — While a patient waits for their appointment, the AI runs a weekly check-in (symptom trend + severity score). If things worsen, waitlist priority is escalated automatically and the care team is notified.

## 🛠 Tech stack

- Python 3.11+
- [Streamlit](https://streamlit.io)
- [Anthropic Claude API](https://www.anthropic.com) — model: `claude-sonnet-4-20250514`
- `fpdf2`, `Pillow`, `python-dotenv`, `plotly`, `pandas`

## 🚀 Setup

```bash
# 1. Clone / unzip the project
cd medbridge-ai

# 2. (Recommended) create a virtual env
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
#    Edit .env and replace the placeholder:
#    ANTHROPIC_API_KEY=sk-ant-...

# 5. Run the app
streamlit run app.py
```

The app opens at http://localhost:8501.

## 🎮 Demo Mode

Every module has a hand-crafted **Demo Mode** response that runs locally without any API call.

- Toggle **🎮 Demo Mode** in the sidebar.
- Demo Mode is **automatic** when no `ANTHROPIC_API_KEY` is configured — perfect for ideathon WiFi hiccups.
- All six modules, all export buttons, and all charts work in Demo Mode.

## 📁 Project structure

```
medbridge-ai/
├── app.py                     # Streamlit entrypoint + sidebar nav + Demo Mode toggle
├── modules/
│   ├── home.py                # Dashboard / landing page
│   ├── navigator.py           # Module 1: conversational program matcher
│   ├── screen_check.py        # Module 2: USPSTF screening timeline
│   ├── recovery_coach.py      # Module 3: day-by-day recovery plan
│   ├── form_fill.py           # Module 4: insurance eligibility Q&A
│   └── waitlist.py            # Module 5: Fast-Track (swap + catcher + pre-care)
├── data/
│   ├── programs.json          # Brazos Valley clinics / programs
│   ├── uspstf_guidelines.json # Screening guidelines reference
│   └── waitlist.json          # Demo waitlist + routine holders + live cancellations
├── utils/
│   ├── ai_engine.py           # Claude wrapper + system prompts
│   ├── bill_parser.py         # Demo bill analysis + dispute letter builder
│   ├── pdf_generator.py       # PDF exports (dispute letter, summaries, plans)
│   └── ui.py                  # Reusable UI primitives (hero, cards, tiles)
├── assets/
│   └── styles.css             # MedBridge color palette & components
├── .env                       # ANTHROPIC_API_KEY=...
├── requirements.txt
└── README.md
```

## 🧪 Demo flow for judges (90 seconds)

1. **Home** — walk through the dashboard, point at the emergency card.
2. **Navigator** — click the "uninsured + diabetes" example → see matched programs with maps.
3. **Screen Check** — click **Load demo profile** → review the timeline with overdue mammogram.
4. **Recovery Coach** — click **Load sample discharge** → walk through the 3-phase plan.
5. **FormFill** — answer the 8 questions → see the matched programs + downloadable PDF.
6. **Fast-Track** — pick Maria Gonzalez (critical diabetes patient) → run Smart Swap → see 3 ranked candidates with incentive offers → flip to Pre-Care Monitoring → submit a "Worse" check-in and watch the priority auto-escalate.

## ⚠️ Disclaimer

MedBridge AI is a prototype and is **not a substitute for professional medical advice**. Always consult a licensed healthcare provider for clinical decisions. Eligibility and pricing information is illustrative and should be verified with the listed organizations.

## 👥 Team

_Team info placeholder — Texas A&M Health Ideathon 2026._

## 📄 License

MIT — use it, fork it, ship it to more communities.
