# System Architecture: MiroFish Ecosystem

## 1. Tiered Intelligence Model
The system is optimized for both reasoning depth and operational scale using a Brain/Muscle/Memory split.

### Brain
- **Role**: World-building and strategic analysis.
- **Model**: Configurable via `LLM_REASONING_MODEL` env var (default: `minimax/minimax-m2.5:free`; recommended: `meta-llama/llama-3.3-70b-instruct:free`)
- **Components**: `ontology_generator.py`, `simulation_config_generator.py`.
- **Function**: Processes raw seeds into high-fidelity psychological profiles and cultural invariants.

### Muscle
- **Role**: High-volume social simulation.
- **Model**: Configurable via `LLM_MODEL_NAME` env var
- **Components**: `simulation_runner.py` (Agents swarm).
- **Function**: Executes thousands of social interactions (posts, replies, quotes) at low cost.

### Memory (Zep Cloud)
- **Role**: Persistent social graph.
- **Components**: `zep_graph_memory_updater.py`.
- **Function**: Records agent discoveries, allowing long-term social dynamics (e.g., rumor propagation) to persist across simulation rounds.

## 2. Core Engines
Integrated modules that analyze the simulation output:
- **Insight Engine**: Deep semantic clustering and sentiment analysis.
- **Report Engine**: Generates comprehensive business and psychological reports.
- **Scraper Engine (MindSpiderLite)**: Surgically harvests real-world context to ground the simulation.

## 3. Domain Isolation
The engine is generic, but its power comes from **Domain Injections**:
- All VU Physics specific data is stored in `domain/vu_physics/`.
- This ensures the core engine remains reusable for other domains (e.g., Finance, Gaming).

## 4. v2 Services (Added 2026)

Three services were added to support the VU Physics domain and Lithuanian-language simulations:

### Academic Calendar (`backend/app/services/academic_calendar.py`)
Maps simulation week numbers to real VU semester events (midterms, exams, registration deadlines). Injects calendar context into simulation configs so agents behave differently during exam stress periods vs. normal weeks.

### OASIS Profile Generator (`backend/app/services/oasis_profile_generator.py`)
Converts seed entities (from Zep graph or local seed file) into OASIS-compatible agent profiles with 19 persona fields: name, age, profession, personality, speaking style, social behaviour, and more. Uses LLM to generate culturally-authentic profiles.

### Simulation Config Generator (`backend/app/services/simulation_config_generator.py`)
Takes a natural-language simulation requirement (e.g. "Launch Fizkonspektas with guerrilla stickers, mid-semester, notes-first messaging") and generates a full OASIS simulation config JSON including event descriptions, initial posts, and agent behaviour parameters.

### Language Injection (`backend/app/utils/llm_client.py` → `_inject_language()`)
Prepends an output-language instruction to every system prompt before LLM API calls. Controlled by `OUTPUT_LANGUAGE` env var (e.g. `Lithuanian`). Prevents Chinese-language models from defaulting to Chinese output.
