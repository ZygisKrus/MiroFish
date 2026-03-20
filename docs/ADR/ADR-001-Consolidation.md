# ADR-001: Consolidation of Fragmented Simulation Engines

## Status
Accepted

## Context
The project was historically split across `MiroFish`, `BettaFish`, and `MindSpider`. This led to:
1. **Logic Duplication:** Multiple Flask servers and redundant persona generation logic.
2. **Maintenance Overhead:** Difficulty in tracking changes across disjointed sub-projects.
3. **Domain Pollution:** General-purpose engine code was mixed with VU-specific cultural grounding logic.

## Decision
We will unify the ecosystem into a single core based on the `MiroFish/backend` structure:
1. **Migration:** All functional engines from `bettafish` (Insight, Report, Forum) are moved to `backend/app/engines/`.
2. **Unified API:** The main Flask app in `backend/run.py` will serve all endpoints.
3. **Domain Isolation:** VU-specific seeds, prompts, and strategy scripts are isolated in `domain/vu_physics/`.
4. **Scraper Standardization:** `MindSpiderLite` becomes the primary ingestion tool for rapid domain grounding.

## Consequences
- **Positive:** Single source of truth, reduced API complexity, easier cross-engine analysis.
- **Negative:** Requires updating all script paths and potential frontend API calls.
