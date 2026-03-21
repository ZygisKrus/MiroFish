# MiroFish: Unified Swarm Intelligence Ecosystem

> A powerful, scalable multi-agent simulation engine designed to predict social media behavior, optimized with a Tiered Intelligence Architecture.

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://opensource.org/licenses/AGPL-3.0)
[![Architecture: Tiered Intelligence](https://img.shields.io/badge/Architecture-Tiered%20Intelligence-green.svg)](docs/ARCHITECTURE.md)

## 🏁 Project Status: Unified
This repository is the result of consolidating the original `MiroFish` engine, the `BettaFish` analysis suites, and the `MindSpider` ingestion tools into a single, maintainable core.

## 🏗️ Architecture (Brain/Muscle/Memory)
We solve the cost vs. quality tradeoff by splitting intelligence:

1. **The Brain (Claude 3.5 Sonnet)**: Handles world-building, ontology generation, and deep psychological profiling.
2. **The Muscle (DeepSeek V3)**: Executes the massive volume of social interactions (posts, likes, replies) at scale.
3. **The Memory (Zep Cloud)**: A persistent social graph that ensures agents "remember" social trends and rumors across rounds.

Detailed architecture can be found in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## 📂 Repository Structure
- `backend/`: The core Flask API and simulation engine.
  - `app/engines/`: Integrated analysis engines (Insight, Report, Media).
- `frontend/`: Real-time monitoring dashboard (Vue.js).
- `domain/`: Isolated domain knowledge and strategy scripts.
  - `vu_physics/`: Current focus area - Vilnius University Physics student swarm.
- `docs/`: Unified documentation and original project archives.

## 🚀 Quick Start

### 1. Setup Environment
Create a `.env` in the root:
```env
# Muscle (StepFun)
LLM_API_KEY=your_key
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL_NAME=stepfun/step-3.5-flash:free

# Brain (Nemotron 3 Super)
LLM_REASONING_MODEL=nvidia/nemotron-3-super-120b-a12b:free

# Memory
ZEP_API_KEY=your_zep_key
```

### 2. Installation
```bash
npm run setup:all
```

### 3. Run Development Server
```bash
npm run dev
```

## 🧪 Current Domain: Fizkonspektas (VU Physics)
The system is currently optimized for simulating the launch of **Fizkonspektas** at Vilnius University. 
- **Seeds**: Located in `domain/vu_physics/seeds/`.
- **Scripts**: Run simulations via `domain/vu_physics/scripts/run_scenarios.py`.
- **Analysis**: Check results with `domain/vu_physics/scripts/analyze_results.py`.

---
*MiroFish was originally developed with support from the Shanda Group and is driven by the OASIS simulation engine.*
