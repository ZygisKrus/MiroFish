# System Architecture: MiroFish Ecosystem

## 1. Tiered Intelligence Model
The system is optimized for both reasoning depth and operational scale using a Brain/Muscle/Memory split.

### Brain (Claude 3.5 Sonnet)
- **Role**: World-building and strategic analysis.
- **Components**: `ontology_generator.py`, `simulation_config_generator.py`.
- **Function**: Processes raw seeds into high-fidelity psychological profiles and cultural invariants.

### Muscle (DeepSeek V3)
- **Role**: High-volume social simulation.
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
