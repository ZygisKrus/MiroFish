# MiroFish: High-Fidelity Social Simulation Engine

> A powerful, scalable multi-agent simulation engine designed to predict social media behavior, optimized with a Tiered Intelligence Architecture.

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://opensource.org/licenses/AGPL-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Why This Exists

Predicting how a specific audience will react to a product launch or marketing campaign is notoriously difficult. MiroFish solves this by creating a "Social Mirror"—a digital sandbox populated by AI agents with deep, psychologically accurate personas based on a specific target demographic. 

This enhanced version introduces a **Tiered Intelligence Architecture**, solving the traditional tradeoff between simulation quality and API cost.

## 🌟 Key Upgrades (The Tiered Architecture)

Running 100+ agents for 50 rounds requires millions of tokens. Using a single frontier model (like GPT-4o or Claude 3.5) for every action is cost-prohibitive. We split the workload:

1. **The Brain (Architect Tier)**: Uses `anthropic/claude-3.5-sonnet` via the `LLM_REASONING_MODEL` environment variable. This model runs *only once* at the start of the simulation to parse the seed document, build the GraphRAG ontology, and generate hyper-detailed, psychologically coherent agent personas.
2. **The Muscle (Actor Tier)**: Uses `deepseek/deepseek-chat` via the `LLM_MODEL_NAME` environment variable. This extremely fast, cost-efficient model handles the massive volume of round-by-round posting, commenting, and liking, simulating the agents' behavior flawlessly at a fraction of the cost.

### Resilient Execution
The simulation engine now includes a **JSON Self-Healing Loop**. If the high-speed "Actor" model outputs slightly malformed JSON during a thought trace, the engine automatically adjusts temperature and retries, ensuring 100% action completion without dropping agents' turns.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- `uv` package manager

### 1. Configuration
Create a `.env` file in the root directory:

```env
# The Muscle (High throughput, low cost - e.g., DeepSeek V3)
LLM_API_KEY=your_openrouter_key
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL_NAME=deepseek/deepseek-chat

# The Brain (High reasoning, strict JSON adherence - e.g., Claude 3.5 Sonnet)
LLM_REASONING_MODEL=anthropic/claude-3.5-sonnet

# Zep GraphRAG Memory
ZEP_API_KEY=your_zep_key
```

### 2. Installation

```bash
npm run setup:all
```

### 3. Running the Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000` and the backend at `http://localhost:5001`.

## 🧪 A/B Testing Scenarios

MiroFish is designed for A/B testing marketing strategies. You can script parallel simulations using the backend API.

Example usage (see `scripts/run_scenarios.py`):
1. **Seed Document**: Provide a rich context file (e.g., `seed_document.md`).
2. **Scenario A**: Launch with `simulation_requirement` set to "Organic Growth".
3. **Scenario B**: Launch with `simulation_requirement` set to "Aggressive Ad Campaign".
4. **Analysis**: Use the analytics script (`scripts/analyze_results.py`) to parse the `actions.jsonl` files and compare Viral Engagement Scores.

## 🧠 Memory & Evolution
By enabling `enable_graph_memory_update: True` during the `/start` payload, every agent interaction (tweet, comment, like) is continuously written back to the Zep Cloud. Agents "remember" their previous interactions, creating long-term social dynamics, grudges, and echo chambers.
