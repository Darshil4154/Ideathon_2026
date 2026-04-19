# MedBridge AI - Your AI Healthcare Copilot

**An AI-powered healthcare navigator for rural and underserved communities in the Brazos Valley, Texas.**

MedBridge AI is a no-code, Claude-powered Streamlit app that helps patients find assistance programs, stay on top of preventive screenings, recover safely after discharge, apply for public insurance, and skip the 3-month clinic waitlist - all through plain-language conversations in a friendly, mobile-ready UI.

Built for the Texas A&M Healthcare Ideathon 2026.

---

## ✨ What's in the app

| # | Module | What it does |
|---|--------|--------------|
| 1 | 🧭 **AI Health Navigator** | Conversational chat that matches the user's situation to real Brazos Valley healthcare programs (FQHCs, charity care, 340B pharmacies, Medicaid, ACA). Plain-language example prompts, a floating chatbot bubble, and emergency-symptom detection are built in. |
| 2 | 🩺 **Preventive Screen Check** | Builds a personalized USPSTF-based screening timeline (Plotly gantt), tailored to age, sex, smoking status, drinking status, family history, and existing conditions. Pill-button selectors keep every choice visible. |
| 3 | 🏥 **Recovery Coach** | Turns hospital discharge instructions into a clear day-by-day recovery plan with daily check-ins. Accepts a pasted summary, the built-in sample, or an uploaded **PDF / Word (.docx) / TXT** file. |
| 4 | 📋 **Insurance FormFill** | 8-question plain-English intake that screens households for Medicaid, CHIP, ACA subsidies, and Medicare, and produces a printable application summary. |
| 5 | ⏱️ **Waitlist Fast-Track** | Bypasses the 3-month waitlist via predictive AI triage - incentivized appointment swapping, live cancellation catching with push notifications, and weekly pre-care check-ins that auto-escalate priority when symptoms worsen. |

### 🔎 Module 5 deep-dive - Waitlist Fast-Track

Finding a clinic means nothing if the next appointment is 4 months away. Fast-Track dynamically reorganizes the clinic's calendar so high-acuity patients get seen first.

- 🔄 **Incentivized Swapping** - AI scans the clinic's calendar for patients with routine checkups, ranks them by flexibility score, and sends a personalized SMS offering a reward (e.g. "$15 pharmacy credit") to move their slot. One tap frees an earlier appointment for a critical patient.
- ⚡ **Live Cancellation Catcher** - The millisecond a slot opens, the AI ranks the waitlist by medical vulnerability and fires a push notification to the best-matched patient with a 5-minute acceptance window. If unacknowledged, it auto-forwards to the next person.
- 📉 **Pre-Care Monitoring** - While a patient waits for their appointment, the AI runs a weekly check-in (symptom trend + severity score). If things worsen, waitlist priority is escalated automatically and the care team is notified.

## 🛠 Tech stack

- Python 3.11+
- [Streamlit](https://streamlit.io) (UI)
- [OpenRouter](https://openrouter.ai) (preferred LLM gateway) via the OpenAI Python SDK
- [Anthropic Claude API](https://www.anthropic.com) (direct fallback)
- `plotly`, `pandas` (charts + data)
- `pypdf`, `python-docx` (discharge-file parsing)
- `python-dotenv` (config)

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
#    Copy the template and fill in one of the keys:
cp .env.example .env
#    Then edit .env and set ONE of:
#      OPENROUTER_API_KEY=sk-or-v1-...      (preferred)
#      ANTHROPIC_API_KEY=sk-ant-...         (fallback)

# 5. Run the app
streamlit run app.py
```

The app opens at http://localhost:8501.

### Which key should I use?

- **OpenRouter** is the primary path - one key, routed to Anthropic's `claude-sonnet-4.5` by default. Change `OPENROUTER_MODEL` in `.env` to swap models without touching code.
- **Anthropic** direct works too - set `ANTHROPIC_API_KEY` and the app uses the native SDK.
- With neither key, the app auto-enters **Demo Mode** (see below).

## 🎮 Demo Mode

Every module ships with a hand-crafted **Demo Mode** response that runs locally without any API call.

- Toggle **🎮 Demo Mode** in the sidebar at any time.
- Demo Mode is **automatic** when no API key is configured - perfect for ideathon WiFi hiccups.
- All five tools, every chart, every check-in, and every program match works in Demo Mode.

## 📁 Project structure

```
medbridge-ai/
├── app.py                     # Streamlit entrypoint + sidebar nav + Demo Mode toggle
├── modules/
│   ├── home.py                # Dashboard / landing page
│   ├── navigator.py           # Module 1: conversational program matcher + chatbot bubble
│   ├── screen_check.py        # Module 2: USPSTF screening timeline with pill selectors
│   ├── recovery_coach.py      # Module 3: day-by-day recovery plan + PDF/DOCX upload
│   ├── form_fill.py           # Module 4: insurance eligibility Q&A
│   └── waitlist.py            # Module 5: Fast-Track (swap + catcher + pre-care)
├── data/
│   ├── programs.json          # Brazos Valley clinics / assistance programs
│   ├── uspstf_guidelines.json # Preventive screening reference
│   └── waitlist.json          # Demo waitlist + routine holders + live cancellations
├── utils/
│   ├── ai_engine.py           # OpenRouter + Anthropic wrapper, system prompts, data loaders
│   └── ui.py                  # Reusable UI primitives (hero, cards, tiles)
├── assets/
│   └── styles.css             # MedBridge design system (colors, type scale, components)
├── .streamlit/
│   └── config.toml            # Forces light theme
├── .env.example               # Template - copy to .env and add your key
├── .gitignore
├── requirements.txt
├── FIGMA_PROMPT.md            # Paste-ready Figma AI prompt for the full design system
└── README.md
```

## 🧪 Demo flow for judges (90 seconds)

1. **Home** - walk through the dashboard, point at the emergency card.
2. **Navigator** - tap the "I can't afford my medicine" example chip → watch live matched programs appear with directions.
3. **Screen Check** - click **Load demo profile** → review the bolded timeline with the overdue mammogram and prediabetes flag.
4. **Recovery Coach** - upload a discharge PDF (or click **Load sample discharge**) → walk through the 3-phase plan and a "Worse" daily check-in.
5. **FormFill** - answer the 8 questions → see matched programs + pre-filled application summary.
6. **Fast-Track** - pick Maria Gonzalez (critical diabetes patient) → run Smart Swap → see 3 ranked candidates with incentive offers → flip to Pre-Care Monitoring → submit a "Worse" check-in and watch the priority auto-escalate.

## 🎨 Design system

The visual language is defined in [`assets/styles.css`](assets/styles.css):

- **Palette**: deep blue `#1B4F72`, accent `#2E86C1`, warm bg `#F4F9FD`, success `#1E8449`, warning `#B7950B`, danger `#B03A2E`
- **Typography**: Plus Jakarta Sans (display/headings), Inter (body) - loaded from Google Fonts
- **Type scale**: 30 / 22 / 18 / 16 / 14 / 12.5 / 11 (display → micro) via CSS variables
- **Shape**: 14-20 px radii, soft layered shadows, 8 px spacing grid
- **Components**: hero banner, stat row, tile, metric tile, card, pill radio group, badge, emergency banner, floating chatbot bubble, premium chat input

A paste-ready prompt for recreating the whole system in Figma AI / Figma Make lives in [`FIGMA_PROMPT.md`](FIGMA_PROMPT.md).

## 🔐 Security notes

- **`.env` is gitignored.** Never commit it. Use `.env.example` as the template.
- If an API key was ever shared in chat, screenshots, or commits, rotate it at the provider dashboard.
- Demo Mode runs entirely offline and sends nothing to external APIs.

## ⚠️ Disclaimer

MedBridge AI is a prototype and is **not a substitute for professional medical advice**. Always consult a licensed healthcare provider for clinical decisions. Eligibility and pricing information is illustrative and should be verified directly with the listed organizations.

## 👥 Team

_Team info placeholder - Texas A&M Healthcare Ideathon 2026._

## 📄 License

MIT - use it, fork it, ship it to more communities.
