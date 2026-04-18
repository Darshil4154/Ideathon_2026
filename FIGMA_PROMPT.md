# Figma Design Prompt — MedBridge AI

Paste the prompt below into **Figma AI / Figma Make** (or hand it to a designer). It is structured to produce a complete, click-through prototype with all 6 product modules, onboarding, and shared components.

---

## 📋 COPY-PASTE PROMPT

Design a modern, healthcare-grade mobile + desktop app called **MedBridge AI — Your AI Healthcare Copilot**. This is a no-code, AI-powered healthcare navigator for rural and underserved communities in the Brazos Valley, Texas. The design must feel warm, trustworthy, and empowering — not clinical or corporate.

Deliver a **clickable prototype** with both **mobile (375×812)** and **desktop (1440×900)** frames for every screen listed. Use auto-layout, consistent spacing, and a reusable component library.

---

### 🎨 BRAND & DESIGN SYSTEM

**Color palette (generate color styles):**
- Primary Deep Blue: `#1B4F72` — headings, primary CTAs, brand
- Accent Blue: `#2E86C1` — links, secondary CTAs, highlights
- Light Background: `#EBF5FB` — page background
- Pure White: `#FFFFFF` — cards, surfaces
- Success Green: `#1E8449` — on-track, savings, confirmations
- Warning Amber: `#D4AC0D` — upcoming, moderate alerts
- Danger Red: `#B03A2E` — overdue, errors, emergency
- Soft Coral: `#FADBD8` — emergency banner background
- Ink: `#1C2833` — body text
- Muted: `#5D6D7E` — secondary text
- Divider: `#D4E6F1`

**Typography (Inter or DM Sans):**
- Display: 36/44, bold (hero + page titles)
- H1: 28/36, bold
- H2: 22/30, semibold
- H3: 18/26, semibold
- Body-Lg: 16/24, regular
- Body: 14/22, regular
- Caption: 12/18, regular
- Micro: 11/16, medium uppercase (badges)

**Shape & elevation:**
- Corner radius: 12 px (cards), 10 px (inputs/buttons), 20 px (pills/badges)
- Card shadow: `0 1px 3px rgba(27,79,114,.08), 0 10px 30px rgba(27,79,114,.06)`
- 8-pt spacing grid

**Iconography:** Lucide or Phosphor, 1.5 stroke, primary deep blue.

**Photography/illustration:** Warm, inclusive illustrations (Undraw or Humaaans style) for empty states — diverse skin tones, rural + urban settings. No stock hospital photography.

---

### 🧱 CORE COMPONENTS (build once, reuse everywhere)

1. **TopBar** — logo mark (🏥 + "MedBridge AI"), page title, demo-mode toggle, profile avatar.
2. **SideNav (desktop)** — 6 module entries (Navigator, Bill Scanner, Med Guard, Screen Check, Recovery Coach, FormFill) with icons + labels; active state uses left accent bar + pale blue background.
3. **BottomTabBar (mobile)** — 4 primary tabs (Home, Chat, Tools, Profile); "Tools" opens a sheet listing all 6 modules.
4. **Button** — primary, secondary, tertiary (text), destructive. States: default, hover, pressed, disabled, loading.
5. **Input field** — with floating label, helper text, error state, icon slot.
6. **Card** — with optional header row (icon + title + meta), body, footer CTA.
7. **StatusBadge** — Danger / Warning / Success / Info / Neutral variants.
8. **AlertBanner** — Info, Success, Warning, Danger (with optional action).
9. **EmergencyBanner** — red 2px border, coral fill, 🚨 icon, "Call 911 now" primary button, nearest ER text.
10. **ChatBubble** — user (right, deep blue) + assistant (left, white card with subtle left accent).
11. **ProgramCard** — clinic name, type pill, address, phone, hours, eligibility paragraph, services chip row, "Get Directions" + "Visit Website" buttons, expandable "Why this fits you" section.
12. **MetricTile** — big number, label, delta, icon.
13. **Timeline/Gantt row** — screening name, date range bar (colored by status), due label.
14. **PhaseCard** — for recovery (Day range header, medications list, activity, diet, red flags).
15. **StepProgress** — dotted progress for multi-step flows (FormFill, onboarding).
16. **Toast** — success/error floating notification.
17. **Modal sheet** — for confirmations and mobile menus.
18. **FileUploader** — drag-drop zone with icon + supported formats.
19. **LoadingState** — animated pulse placeholders + contextual spinner text ("Finding programs that match your situation...").
20. **EmptyState** — illustration + headline + supporting copy + primary CTA.

Keep a `StatusBadge` variant set for severity (Dangerous 🔴, Moderate 🟡, Mild 🟢) and screening status (Overdue / Upcoming / On track).

---

### 📄 SCREENS TO DESIGN (mobile + desktop)

#### 0. Splash / Onboarding (3 slides)
- **Slide 1** — Hero illustration (diverse patients + warm sun). Headline: "Healthcare you can actually understand." Sub: "Find care, fight bills, stay safe — in plain English."
- **Slide 2** — "Built for the Brazos Valley." Map illustration pinning Bryan/College Station. List: 12+ local programs. "Works offline in Demo Mode."
- **Slide 3** — "Your AI Copilot." Three tiles: Find care, Fight bills, Stay well. CTA "Get started" + "I already have an account".

#### 1. Home / Dashboard
- Greeting: "Good morning, Darshil 👋"
- Quick actions grid (6 tiles, one per module, each with icon + label + 1-line description)
- "Continue where you left off" card (last active module)
- "Today's priority" card (e.g., overdue screening) with CTA
- Health tip of the day (rotating)
- Emergency mini-banner at bottom: "Having an emergency? Tap to call 911."
- Desktop: 2-column — left 2/3 dashboard, right 1/3 "Getting started checklist".

#### 2. 🧭 AI Health Navigator (STAR SCREEN — give most polish)
- **2a. Entry/Empty** — illustration + welcome copy + 4 example prompt chips ("I'm uninsured with diabetes…", "I got a surprise hospital bill…", "I'm pregnant with no insurance…", "My dad is rural with high BP…") + large text input with "Send" button.
- **2b. In-conversation** — chat thread with user + assistant bubbles, typing indicator ("Finding programs that match your situation…"), inline program cards embedded in the reply.
- **2c. Results expanded** — bottom section "Programs matched to your situation" with 3–5 ProgramCards, each expandable, with "Get Directions" button opening a map pin.
- **2d. Emergency triggered** — big red EmergencyBanner at top, "Call 911" primary button, St. Joseph Health Bryan card with phone + address below.

#### 3. 💰 Medical Bill Scanner
- **3a. Upload screen** — two tabs: "Paste text" (big textarea + "Load sample bill" button) and "Upload file" (drag-drop zone). Bill preview thumbnail on the right.
- **3b. Analyzing state** — animated skeleton of the results page + spinner "Scanning 11 line items…".
- **3c. Results** — 3 MetricTiles (Billed $1,190, Fair $550, Savings $640), side-by-side bar chart ("Billed vs Fair"), table "Line-by-line review" with red-highlighted error rows, section "🔴 Errors found" (4 error cards: Duplicate CBC, Upcoding, Unbundling, Facility Fee), dispute-letter preview in a paper-style card, "Download dispute letter (PDF)" primary CTA.
- **3d. Dispute letter preview modal** — full letter with "Copy" / "Download PDF" / "Email it to me" actions.

#### 4. 💊 Medication Guard
- **4a. Input** — chip-style medication adder (type and press enter adds a pill), "Load demo meds" button (prefills 5), big "Check interactions" CTA.
- **4b. Results** — medication summary table (name, class, common use), alert hero "2 dangerous interactions found" (red), then interaction cards (Warfarin+Aspirin 🔴, Warfarin+Ibuprofen 🔴, Lisinopril+Ibuprofen 🟡) each with mechanism + recommendation + "Why it's dangerous" expandable, "Download doctor summary" CTA, "Share with my pharmacist" secondary.

#### 5. 🩺 Preventive Screen Check
- **5a. Profile form** — age slider, sex toggle, smoking selector, family-history checkbox grid, existing-conditions chip input, "Load demo profile" button, primary "Build my plan".
- **5b. Timeline** — horizontal Plotly-style gantt with today marker, each row = screening, colors by status. Legend at top. Mobile: vertical card list instead.
- **5c. Screenings list** — recommendation cards with StatusBadge + "Why it matters for you" + "Where to go in the Brazos Valley" + "Book a visit" button.
- **5d. Top priority callout** — gradient card spotlighting the #1 action this person should take.

#### 6. 🏥 Recovery Coach
- **6a. Input** — paste or upload discharge instructions, "Load sample discharge" button.
- **6b. Overview** — condition header ("Recovering from pneumonia"), plain-language overview paragraph, quick stat tiles (Days left, Meds active, Follow-up date).
- **6c. Phase timeline** — 3 PhaseCards (Day 1-3 / Day 4-7 / Day 8-14) vertically stacked with visual progress connector; expand to see medications, activity, diet, red flags.
- **6d. Daily check-in** — "How are you feeling today?" with 4 tappable emoji options (Better / Same / Worse / New symptoms), tailored response card appears below.
- **6e. Emergency symptoms list** — red card "Call 911 if…" with bullet list.

#### 7. 📋 Insurance FormFill
- **7a. Intro** — explainer + "8 quick questions, takes 2 minutes" + progress bar.
- **7b. Question screens (×8)** — one question per screen, big friendly question, input optimized for type (text / number / chip select), Back + Next buttons, progress dots.
- **7c. Results** — "✅ You likely qualify for:" with 2–3 program cards (Medicaid/CHIP, ACA Marketplace with subsidies, Medicare if applicable), each with "Why you qualify" + "How to apply" + primary CTA "Start application". Then "Next steps" checklist. Then "Pre-filled application summary" paper-style card with "Download PDF" + "Email me a copy".

#### 8. Shared / Utility
- **8a. Settings** — profile, language (English/Spanish), demo-mode toggle, API key field, notification preferences.
- **8b. API-key missing state** — friendly illustration + copy "Add your Anthropic API key to unlock live AI, or continue in Demo Mode" + two buttons.
- **8c. Error state** — generic "Something went wrong" card with retry.
- **8d. Offline state** — "You're offline — Demo Mode is active."
- **8e. About** — mission, team placeholder, ideathon context, links.

---

### 🔀 PROTOTYPE FLOW (wire these clicks)

1. Splash → Onboarding 1 → 2 → 3 → Home.
2. Home → each of the 6 module tiles → respective module entry screen.
3. **Navigator flow:** Entry → click example chip → In-conversation (with pre-populated reply) → Results with program cards → click card → Program detail.
4. **Bill Scanner flow:** Entry → click "Load sample bill" → Analyzing → Results → click "Download dispute letter" → Dispute letter modal.
5. **Med Guard flow:** Entry → "Load demo meds" → Check interactions → Results with 3 alerts.
6. **Screen Check flow:** Entry → "Load demo profile" → Timeline + list → click top priority → linked Navigator ("Find a mammogram clinic").
7. **Recovery Coach flow:** Entry → "Load sample discharge" → Overview → Phase 1 expanded → Daily check-in "Worse" → safety guidance card.
8. **FormFill flow:** Intro → Q1 → Q2 → … → Q8 → Results → Download PDF modal.
9. From any module, the bottom "Emergency" affordance → Emergency screen with 911 button + nearest ER.

---

### 🧭 INTERACTION & MOTION

- Page transitions: 200 ms ease-out slide-up on mobile, fade on desktop.
- Chat bubbles: stagger in 60 ms each.
- Emergency banner: pulse shadow once when it appears, then static.
- Button press: 2px drop, 120 ms.
- Loading spinner: brand-blue ring, 800 ms rotation.
- All animations must respect `prefers-reduced-motion` — call this out in the design notes layer.

---

### ♿ ACCESSIBILITY REQUIREMENTS

- Minimum AA contrast — verify with a plugin.
- Tap targets ≥ 44×44 px.
- All form inputs have visible labels (no placeholder-only).
- Error and status colors never carry meaning alone — pair with icon + text.
- Include a "Plain Language" toggle mock in Settings.

---

### 📱 DELIVERABLES (organize the file in these pages)

1. **00 Cover** — brand, version, design principles.
2. **01 Design System** — colors, type, spacing, components.
3. **02 Mobile – Core flows** — Splash, Home, Navigator, Bill Scanner, Med Guard, Screen Check, Recovery Coach, FormFill.
4. **03 Desktop – Same flows**.
5. **04 States** — empty, loading, error, emergency, offline.
6. **05 Prototype** — connected click-through for the 90-second demo.
7. **06 Hand-off** — redlines, spec annotations, asset exports.

---

### 🎯 DEMO SCRIPT THE PROTOTYPE MUST SUPPORT (90 seconds)

Splash → Onboarding → Home → Navigator (uninsured + diabetes example) → program match → back → Bill Scanner (load sample → analyze → see $640 savings → download dispute letter) → back → Med Guard (load demo → Warfarin+Aspirin DANGEROUS alert) → back → Screen Check (load demo profile → timeline with overdue mammogram) → back → Recovery Coach (load sample discharge → Day 1-3 phase) → back → FormFill (speed through to results with Medicaid + ACA match).

---

### 🎨 VIBE REFERENCES

- Warmth of **Cityblock Health** and **Oscar Health** onboarding
- Clarity of **Linear** and **Notion** empty states
- Trust of **One Medical** and **Mayo Clinic Patient** interfaces
- Conversational feel of **Claude.ai** and **ChatGPT mobile**
- Illustration warmth of **Doximity GPT** and **K Health**

Avoid the cold, corporate, all-white hospital-portal aesthetic. Avoid generic stethoscope stock photos. Lean into warmth, clarity, and actionable guidance.

---

Build it all. Make every screen feel like a friend who happens to be a brilliant healthcare navigator.
