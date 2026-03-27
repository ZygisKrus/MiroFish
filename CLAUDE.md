# MiroFish — Developer Guide

MiroFish is a multi-agent social media simulation platform for academic market research.
It simulates realistic student behaviour on social platforms to evaluate marketing strategies
before real-world launch. Primary domain: VU Physics Faculty (Vilnius University).
Current product under study: Fizkonspektas (fizkonspektai.lt).

## Repository Structure

```
MiroFish/
├── backend/              # Flask API + simulation engines
│   ├── app/
│   │   ├── api/          # Flask route handlers
│   │   ├── engines/      # Insight, Report, Forum, Media, Query engines
│   │   ├── services/     # Core services (simulation, profiles, Zep, etc.)
│   │   └── utils/        # LLM client, Zep factory, helpers
│   └── run.py            # Flask entrypoint
├── frontend/             # Vue 3 dashboard (real-time monitoring)
├── domain/
│   └── vu_physics/       # VU Physics domain
│       ├── seeds/        # Agent roster & product seed files
│       └── scripts/      # run_scenarios.py, analyze_results.py
├── docs/                 # Architecture, ADRs, scenario docs
└── legacy/               # Archived pre-consolidation code (do not use)
```

## Quick Start

### Prerequisites
- Node.js 18+, Python 3.11+, uv package manager
- OpenRouter API key (for LLM access)
- Docker + Docker Compose (optional, for Zep memory)

### Install
```bash
npm run setup:all    # installs frontend deps + backend deps via uv
```

### Run locally
```bash
npm run dev          # starts Flask on :5001 and Vue on :3000
```

### Run with Docker (includes Zep memory graph)
```bash
docker compose up
```

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Required | Description |
|----------|----------|-------------|
| `LLM_API_KEY` | Yes | OpenRouter API key |
| `LLM_BASE_URL` | Yes | OpenRouter base URL |
| `LLM_MODEL_NAME` | Yes | Model for agent personas/actions |
| `LLM_REASONING_MODEL` | Yes | Model for report generation |
| `OUTPUT_LANGUAGE` | Yes | Language for all LLM output (e.g. `Lithuanian`) |
| `ZEP_API_URL` | No | Zep CE URL (default: http://localhost:8000) |
| `ZEP_API_KEY` | No | Zep Cloud API key (leave empty for CE) |

**Recommended model for Lithuanian:** `openai/gpt-oss-120b:free`

## Running Simulations

### Test run (2 simulated days, fast)
```bash
cd domain/vu_physics/scripts
python run_scenarios.py --mode TEST --phase 1
```

### Full Phase 1 (9 scenarios x 4 simulated weeks each)
```bash
python run_scenarios.py --mode PROD --phase 1
```

### Analyse results
```bash
python analyze_results.py
```

Results are saved to `domain/vu_physics/results/` and simulation actions to
`backend/uploads/simulations/{id}/twitter/actions.jsonl`.

## Key Services

| Service | File | Role |
|---------|------|------|
| Simulation runner | `backend/app/services/simulation_runner.py` | Launches and monitors OASIS simulation subprocess |
| Profile generator | `backend/app/services/oasis_profile_generator.py` | Generates agent personas from seed entities via LLM |
| Simulation config | `backend/app/services/simulation_config_generator.py` | Generates OASIS config JSON from simulation requirements |
| Academic calendar | `backend/app/services/academic_calendar.py` | Maps simulation weeks to semester events (exams, deadlines) |
| Language injection | `backend/app/utils/llm_client.py` → `_inject_language()` | Prepends output language instruction to every system prompt |
| Zep entity reader | `backend/app/services/zep_entity_reader.py` | Reads agent entities from Zep graph or local seed fallback |

## Common Gotchas

- **Agents respond in Chinese/English?** → Set `OUTPUT_LANGUAGE=Lithuanian` in `.env`
- **Zep graph 404 errors?** → Expected when using Zep CE (Community Edition). The system automatically falls back to reading agents from `domain/vu_physics/seeds/refined_mega_seed.md`. This is normal.
- **No actions in results?** → Check that `backend/` is running (`npm run dev`) before calling `run_scenarios.py`
- **Rate limit errors (429)?** → The LLM client automatically parses retry delays and backs off. If persistent, switch to a model with higher free RPM limits.
- **Graph visualization empty?** → If using local_seed_fallback, the graph endpoint reads directly from seed file. Check `/api/graph/data/local_seed_fallback` returns nodes.

## Seed Files

| File | Purpose |
|------|---------|
| `domain/vu_physics/seeds/refined_mega_seed.md` | **Active** — consolidated 150-agent roster + product specs. Use this for simulations. |
| `domain/vu_physics/seeds/mega_seed_world_book.md` | Source roster (used as Zep CE fallback) |
| `domain/vu_physics/seeds/seed_document.md` | Legacy product spec (content merged into refined_mega_seed) |

## Scenarios

See `docs/SCENARIOS.md` for the full 9-scenario Phase 1 matrix and Phase 2 design variants.
