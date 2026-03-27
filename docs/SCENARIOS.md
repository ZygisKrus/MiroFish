# Fizkonspektas Launch Simulation — Scenario Reference

This document describes the two-phase scenario matrix used to evaluate marketing strategies
for the Fizkonspektas product launch at VU Physics Faculty (Vilnius University).

**Total design:** Up to 18 scenarios across two phases, each running 28 simulated days
(112 rounds at 4 rounds/day).

---

## Phase 1: Marketing x Pricing x Emphasis (9 scenarios)

All Phase 1 scenarios use Design D1 (current site design). The goal is to find the best
combination of marketing channel, pricing model, and product emphasis.

### Phase 1 Scenario Matrix

| ID | Name | Marketing | Pricing | Emphasis |
|----|------|-----------|---------|----------|
| S1 | Baseline: Stickers + Current Price + Notes | M1 | P1 | E1 |
| S2 | Instagram Panic: Ads + Current Price + Exam-Prep | M2 | P1 | E3 |
| S3 | Peer Trust: Ambassadors + Current Price + AI Tutor | M3 | P1 | E2 |
| S4 | Full Push Cheap: Combined + Lower Price + Exam-Prep | M4 | P2 | E3 |
| S5 | Free Hook: Stickers + Freemium + Notes | M1 | P3 | E1 |
| S6 | Viral Free: Instagram + Freemium + AI Tutor | M2 | P3 | E2 |
| S7 | Peer Affordable: Ambassadors + Lower Price + Notes | M3 | P2 | E1 |
| S8 | Premium AI Push: Combined + Current Price + AI Tutor | M4 | P1 | E2 |
| S9 | Cheap Panic: Stickers + Lower Price + Exam-Prep | M1 | P2 | E3 |

---

## Variable Definitions

### Marketing Strategies

| Code | Description |
|------|-------------|
| M1 | **Guerrilla stickers** — QR codes on dorm doors (Kamciatka, Niujorkas), lecture halls, bathrooms. Slogans: "Failing Quantum Mechanics? Scan this." |
| M2 | **Instagram targeted ads** — VU Physics hashtags, exam stress content, showing AI assistant solving electrodynamics problems. |
| M3 | **Peer ambassador program** — 1 free account per study group; ambassadors spread the word organically through dorm clusters and study sessions. |
| M4 | **Combined** — All channels simultaneously (stickers + Instagram ads + peer ambassadors). Maximum reach. |

### Pricing Models

| Code | Description |
|------|-------------|
| P1 | **Current pricing** — 5.99 EUR one-time per course OR 9.99 EUR/month subscription with 7-day free trial OR lifetime all-access. |
| P2 | **Lower barrier** — 4.99 EUR/month subscription only (no per-course option). 7-day free trial. Simplified decision. |
| P3 | **Freemium** — Basic notes visible for free. AI assistant, problem sets, and advanced derivations require Premium (9.99 EUR/month). |

### Product Emphasis (Positioning)

| Code | Description |
|------|-------------|
| E1 | **Notes-first** — "120,000 lines of university-level content. Every derivation, step by step." Highlight content depth and quality. |
| E2 | **AI-tutor-first** — "Your personal physics tutor, available 24/7. Ask anything, get real answers." Highlight GPT-4 AI assistant. |
| E3 | **Exam-prep-first** — "Pass your exam in 24 hours. Everything you need, nothing you don't." Highlight urgency and exam survival. |

---

## Phase 2: Top Scenarios x Design Variants (up to 9 scenarios)

After Phase 1 completes and `analyze_results.py` ranks the scenarios, the top 3 winners
are re-run against all 3 design variants. This yields up to 9 additional scenarios
(3 winners x 3 designs).

Phase 2 scenario IDs follow the pattern `P2-{base_id}-{design}` (e.g., `P2-S4-D2`).

### Design Variants

| Code | Description |
|------|-------------|
| D1 | **Anti-Halation Brutalism** (current) — Black/white (#0D0D0D/#F4F4F4), JetBrains Mono, zero border-radius, hard shadows. Industrial/hacker aesthetic. |
| D2 | **Clean Academic** — White background, serif headers (Georgia), blue accents (#2563EB), rounded corners. Notion/Coursera feel. Traditional educational look. |
| D3 | **Glassmorphism Premium** — Frosted glass cards, gradient backgrounds, smooth animations, rounded corners. Apple-style luxury feel. |

---

## Metrics Tracked

Each simulation tracks the following key metrics per scenario:

| Metric | Description |
|--------|-------------|
| `awareness_pct` | Percentage of agents who became aware of the product |
| `trial_signups` | Number of agents who signed up for a free trial |
| `conversion_rate` | Fraction of trial users who converted to paid |
| `total_revenue_eur` | Total simulated revenue in EUR |
| `churn_rate` | Fraction of paid users who cancelled |
| `account_sharing_incidents` | Number of agents sharing a single account |
| `net_promoter_score` | NPS — agent willingness to recommend the product |
| `design_bounce_rate` | Fraction of agents who visited but immediately left (design-related) |

### Agent Behaviour Notes

- Agents reason about price in terms of "Jammi kebabs" (9.99 EUR = 2 kebabs), grounding economic decisions in local purchasing-power intuitions.
- Agents consider group buys, free trial timing relative to upcoming exams, and social proof from dorm clusters and study groups.
- Platforms simulated: Instagram, Telegram, Facebook groups, physical word-of-mouth, and direct website visits. Not Twitter or Reddit.

---

## Academic Calendar Context

All scenarios start at the `mid` point of the semester (mid-semester, building toward midterms).

Available `--academic-start` values:

| Value | Description |
|-------|-------------|
| `early` | Early semester — low stress, low urgency |
| `mid` | Mid-semester — moderate stress, building toward midterms (default) |
| `pre_exam` | Pre-exam period — high stress, high study-tool interest, strong trial pressure |
| `exam` | Exam week — peak stress, maximum urgency |

The academic calendar modulates per-day values for `study_tool_interest`, `exam_stress`,
`price_sensitivity`, `churn_risk`, and `trial_conversion_pressure`.

---

## How to Run

### Phase 1 — Test mode (2 simulated days per scenario)
```bash
cd domain/vu_physics/scripts
python run_scenarios.py --mode TEST --phase 1
```

### Phase 1 — Full run (28 simulated days per scenario)
```bash
python run_scenarios.py --mode PROD --phase 1
```

### Analyse Phase 1 results (required before Phase 2)
```bash
python analyze_results.py
```

### Phase 2 — Run top 3 x design variants (auto-reads analysis rankings)
```bash
python run_scenarios.py --mode PROD --phase 2
```

### Phase 2 — Manual top-scenario override
```bash
python run_scenarios.py --mode PROD --phase 2 --top-scenarios S4,S8,S6
```

### Run both phases sequentially
```bash
python run_scenarios.py --mode PROD --phase both
```

### Specify academic calendar start point
```bash
python run_scenarios.py --mode PROD --phase 1 --academic-start pre_exam
```

Results are saved to `domain/vu_physics/results/`:
- `{scenario_id}_meta.json` — per-scenario metadata and simulation IDs
- `phase_1_results.json` — mapping of scenario ID to simulation ID
- `phase_2_results.json` — same for Phase 2
- `analysis_report.json` — score-ranked Phase 1 results (produced by `analyze_results.py`)
