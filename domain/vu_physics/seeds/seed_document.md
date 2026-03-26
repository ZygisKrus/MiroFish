# FIZKONSPEKTAS — Product Reality Seed
## Ground Truth Data for MiroFish Simulation

---

## 1. Product Specification

**Name:** Fizkonspektas
**URL:** fizkonspektai.lt
**Status:** Live, ~100+ paying users
**Tech Stack:** React 19, Firebase (Auth/Firestore/Functions/Hosting), Stripe payments, OpenAI GPT-4

### Content Inventory (28 courses, ~120,000 lines of academic content)

**Physics (9 courses):**
- Mechanikos konspektas (Mechanics) — 1st year, ~4000+ lines
- Elektra ir magnetizmas (Electricity & Magnetism)
- Elektrodinamikos konspektas (Electrodynamics) — 3rd year, Ampere-Maxwell laws, displacement current
- Kvantinės mechanikos konspektas (Quantum Mechanics) — 3rd year, wave functions, operators, commutators
- Atomo ir branduolio fizika (Atomic & Nuclear Physics) — 3rd year
- Optika (Optics) — 2nd year, polarization, Fresnel equations, fiber optics
- Molekulių fizika ir termodinamika (Thermodynamics)
- Statistinė fizika (Statistical Physics)
- Kietojo kūno fizika (Solid State Physics)

**Mathematics (3 courses):**
- Aukštoji matematika I & II (Advanced Mathematics) — vector spaces, matrices, complex numbers
- Matematinės fizikos lygtys (Mathematical Physics Equations) — 3rd year

**Engineering & Technology (5 courses):**
- Elektronikos pagrindai (Electronics Fundamentals)
- Telekomunikacijų pagrindai (Telecommunications Basics)
- Fizika (General Physics)
- Chemijos technologija (Chemical Technology)

**Economics & Business (7 courses):**
- Makroekonomika, Mikroekonomika
- Įmonių finansai (Corporate Finance)
- Rinkodara (Marketing), Vadyba (Management)
- Inovacijų ekonomika ir vadyba (Innovation Economics)
- Verslo teisės pagrindai (Business Law)

**Skills (1 course):**
- Studijų įgūdžiai ir darbo sauga (Study Skills & Safety)

### Content Depth
Each course contains:
- Multiple "temos" (topics/chapters) with detailed step-by-step derivations
- LaTeX-rendered formulas (KaTeX)
- Schema.org structured FAQ data for SEO
- Multiple-choice questions with detailed explanations in Lithuanian
- Real university-level physics and mathematics content

---

## 2. Pricing Model (Actual)

### Tier 1: Single Course — €5.99 one-time (was €8.99)
- One-time purchase, permanent lifetime access
- Per-course unlocking
- No recurring fees

### Tier 2: Subscription — ALL COURSES — €0 for 7 days → €9.99/month
- Free trial: 7 days, ONE-TIME ONLY per user (tracked via Firestore)
- After trial: €9.99/month recurring (auto-renews)
- Covers ALL courses + automatic new content updates
- Cancel anytime

### Tier 3: Lifetime All-Access — One-time premium purchase
- All courses permanently, no expiration
- "VISAM GYVENIMUI" / "VISI KONSPEKTAI" positioning

### Payment Infrastructure
- Stripe integration via Firebase Cloud Functions
- Firestore as source-of-truth for purchases
- Email-based user tracking (lowercase normalization)
- Webhook signature verification
- Free trial prevention logic (tracks used trials per user)

---

## 3. Conversion Funnel (Actual UX Flow)

1. Student lands on course page (no login required to browse)
2. Sees course title + year badge + navigation tabs (Theory | Questions | Problems | Checklists)
3. First paragraph of each topic is VISIBLE (quality proof)
4. Remaining content is blurred with paywall overlay:
   **"LIKUSI MEDŽIAGA UŽŠIFRUOTA. REIKALINGAS PRO"**
5. Sunk-cost micro-quiz: 3 easy questions → progress bar reaches 80% → 100% requires purchase
6. Social proof toasts: "14 VARTOTOJŲ ŠIUO METU SKAITO 'MECHANIKĄ'"
7. Pricing modal with 3 tiers appears
8. Stripe checkout → Firestore updates → content unlocked

### Key Psychological Tactics (from design.md)
- **Blurred tease**: Student can SEE the formulas are there, just can't read them
- **Sunk cost fallacy**: After answering 3 quiz questions, feels invested
- **Social proof**: Real-time user count creates urgency
- **"24-HOUR EXAM PREP PASS"**: Stress-focused positioning for last-minute buyers

---

## 4. AI Physics Assistant (Actual Implementation)

- **Model:** GPT-4 via OpenAI API
- **Endpoint:** Cloud Function (chatwithassistant-uxuxfjkjxa-uc.a.run.app)
- **UI:** Floating launcher button (56×56px) → slide-out chat window (400px wide)
- **Isolation:** Shadow DOM (CSS fully isolated from parent page)
- **Session:** 7-minute TTL, localStorage key: fizbot_session_v3
- **Context:** Knows which course/topic the student is currently viewing
- **Features:** Real-time markdown rendering, code blocks, inline formulas
- **Access:** Available on all course pages via floating button

---

## 5. Design Language: "Anti-Halation Brutalism"

- **Colors:** #0D0D0D (near-black), #F4F4F4 (near-white)
- **Typography:** JetBrains Mono (system/formulas), Inter (body text)
- **Style:** Zero border-radius, solid hard shadows, no glassmorphism
- **Accents:** Soft green (#2E8B57), soft red (#CD5C5C), warm amber (#D4A843)
- **Icons:** Phosphor Icons library + FontAwesome 6.0
- **Responsive:** Mobile-first with bottom navigation bar
- **Branding:** Industrial/hacker aesthetic — "FIZKONSPEKTAS | Ribotos prieigos sistema"

---

## 6. Target Audience & Environment

### Primary: VU Physics Faculty (Sauletekis Campus)
- ~300 active physics students across 4 years
- Located in Sauletekis campus, Vilnius
- Dormitories: Kamciatka (Kampos) and Niujorkas — social epicenter

### Student Segments
1. **Desperate First-Years** — Overwhelmed by Prof. Vicas's Calculus, willing to pay to survive
2. **Struggling Third-Years** — QM and Electrodynamics are brutal, need precise derivations
3. **Skeptics** — Believe education should be free, E9.99 is "two Jammi kebabs"
4. **Tech Optimists** — Love the AI assistant, see it as a personal tutor
5. **Account Sharers** — Will organize 4-5 person group buys to split the cost

### Economic Reality
- Student monthly budget: E400-800 (stipend + parents)
- Food: E150-250, Dorm: E0-150 (subsidized), Fun: E50-100
- Discretionary for digital tools: E5-20/month
- **E9.99/month = ~2 Jammi kebabs** — this is the mental benchmark
- **E5.99 one-time per course** — the "safe" entry point

---

## 7. Launch Strategy Variables (For Simulation Testing)

### Marketing Channels
- **M1 — Guerrilla Stickers:** QR codes on dorm doors, lecture halls, bathrooms. Slogans: "Failing Quantum Mechanics? Scan this."
- **M2 — Instagram Ads:** Targeted at VU Physics hashtags, showing AI assistant solving electrodynamics
- **M3 — Peer Ambassadors:** 1 free account per study group, they spread the word
- **M4 — Combined:** All channels simultaneously

### Pricing Variants
- **P1 — Current:** E5.99/course or E9.99/mo subscription
- **P2 — Lower barrier:** E4.99/mo, no per-course option
- **P3 — Freemium:** Basic notes free, AI assistant + problems = premium

### Product Emphasis Variants
- **E1 — Notes-first:** "120,000 lines of university-level content"
- **E2 — AI tutor-first:** "Your personal physics tutor, available 24/7"
- **E3 — Exam-prep-first:** "Pass your exam in 24 hours"

### Design Variants
- **D1 — Current Brutalism:** Black/white, monospace, hard shadows
- **D2 — Clean Academic:** White, serif, blue accents, Notion/Coursera feel
- **D3 — Glassmorphism Premium:** Frosted glass, gradients, Apple-style luxury

---

## 8. The Core Conflict (Simulation Catalyst)

As Fizkonspektas launches, a multi-sided debate erupts:
- **Tech optimists** call it "the ultimate exam cheat code" and praise the AI
- **Skeptics** and some professors argue it makes students lazy and prevents real learning
- **Account sharers** organize group buys, threatening the business model
- **Mid-term exams approach**, driving desperation and panic purchases
- **Price sensitivity** creates a constant tension: "Is this worth 2 kebabs?"
- **Academic ethics** questions arise: Is using AI-assisted notes "cheating"?

The simulation must capture how these forces interact and which marketing/pricing/design combination overcomes the resistance.
