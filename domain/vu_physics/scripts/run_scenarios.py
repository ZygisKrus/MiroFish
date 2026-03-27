"""
Fizkonspektas Launch Simulation - Two-Phase Scenario Runner

Phase 1: Test 9 combinations of Marketing x Pricing x Emphasis (with current design D1)
Phase 2: Test top 3 winners from Phase 1 x 3 Design variants (9 more scenarios)

Total: Up to 18 scenarios, each running 28 simulated days (112 rounds at 4 rounds/day).
"""

import sys
import requests
import json
import time
import os
import argparse
from datetime import datetime

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../backend"))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

try:
    from app.services.academic_calendar import AcademicCalendar, AcademicCalendarConfig
    _CALENDAR_AVAILABLE = True
except ImportError:
    _CALENDAR_AVAILABLE = False

# Polling constants
POLL_INTERVAL_FAST = 5       # seconds between graph build polls
POLL_INTERVAL_PREPARE = 10   # seconds between prepare polls
POLL_INTERVAL_SIM = 15       # seconds between simulation polls
GRAPH_BUILD_TIMEOUT = 60     # max polls for graph build (~5 min)
PREPARE_TIMEOUT = 150        # max polls for preparation (~25 min)
SIM_TIMEOUT = 960            # max polls for full simulation (~4 hours)

BASE_URL = "http://127.0.0.1:5001/api"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SEED_FILE = os.path.abspath(os.path.join(SCRIPT_DIR, "../seeds/refined_mega_seed.md"))
RESULTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../results"))

# ============================================================
# SCENARIO DEFINITIONS
# ============================================================

# Marketing channel strategies
MARKETING = {
    "M1": "Guerrilla stickers: QR codes on dorm doors (Kamciatka, Niujorkas), lecture halls, bathrooms. Slogans: 'Failing Quantum Mechanics? Scan this.'",
    "M2": "Instagram targeted ads: VU Physics hashtags, exam stress content, showing AI assistant solving electrodynamics problems.",
    "M3": "Peer ambassador program: 1 free account per study group, ambassadors spread the word organically through dorm clusters and study sessions.",
    "M4": "Combined: All channels simultaneously (stickers + Instagram ads + peer ambassadors). Maximum reach.",
}

# Pricing strategies
PRICING = {
    "P1": "Current pricing: 5.99 EUR one-time per course OR 9.99 EUR/month subscription with 7-day free trial OR lifetime all-access.",
    "P2": "Lower barrier: 4.99 EUR/month subscription only (no per-course option). 7-day free trial. Simplified decision.",
    "P3": "Freemium model: Basic notes visible for free. AI assistant, problem sets, and advanced derivations require Premium (9.99 EUR/month).",
}

# Product emphasis / positioning
EMPHASIS = {
    "E1": "Notes-first: '120,000 lines of university-level content. Every derivation, step by step.' Highlight content depth and quality.",
    "E2": "AI-tutor-first: 'Your personal physics tutor, available 24/7. Ask anything, get real answers.' Highlight GPT-4 AI assistant.",
    "E3": "Exam-prep-first: 'Pass your exam in 24 hours. Everything you need, nothing you don't.' Highlight urgency and exam survival.",
}

# Design variants (Phase 2 only)
DESIGNS = {
    "D1": "Current 'Anti-Halation Brutalism': Black/white (#0D0D0D/#F4F4F4), JetBrains Mono, zero border-radius, hard shadows. Industrial/hacker aesthetic.",
    "D2": "'Clean Academic': White background, serif headers (Georgia), blue accents (#2563EB), rounded corners. Notion/Coursera feel. Traditional educational look.",
    "D3": "'Glassmorphism Premium': Frosted glass cards, gradient backgrounds, smooth animations, rounded corners. Apple-style luxury feel.",
}

# Phase 1: 9 scenarios (Marketing x Pricing x Emphasis, all with design D1)
PHASE_1_SCENARIOS = [
    {"id": "S1", "marketing": "M1", "pricing": "P1", "emphasis": "E1", "design": "D1",
     "name": "Baseline: Stickers + Current Price + Notes"},
    {"id": "S2", "marketing": "M2", "pricing": "P1", "emphasis": "E3", "design": "D1",
     "name": "Instagram Panic: Ads + Current Price + Exam-Prep"},
    {"id": "S3", "marketing": "M3", "pricing": "P1", "emphasis": "E2", "design": "D1",
     "name": "Peer Trust: Ambassadors + Current Price + AI Tutor"},
    {"id": "S4", "marketing": "M4", "pricing": "P2", "emphasis": "E3", "design": "D1",
     "name": "Full Push Cheap: Combined + Lower Price + Exam-Prep"},
    {"id": "S5", "marketing": "M1", "pricing": "P3", "emphasis": "E1", "design": "D1",
     "name": "Free Hook: Stickers + Freemium + Notes"},
    {"id": "S6", "marketing": "M2", "pricing": "P3", "emphasis": "E2", "design": "D1",
     "name": "Viral Free: Instagram + Freemium + AI Tutor"},
    {"id": "S7", "marketing": "M3", "pricing": "P2", "emphasis": "E1", "design": "D1",
     "name": "Peer Affordable: Ambassadors + Lower Price + Notes"},
    {"id": "S8", "marketing": "M4", "pricing": "P1", "emphasis": "E2", "design": "D1",
     "name": "Premium AI Push: Combined + Current Price + AI Tutor"},
    {"id": "S9", "marketing": "M1", "pricing": "P2", "emphasis": "E3", "design": "D1",
     "name": "Cheap Panic: Stickers + Lower Price + Exam-Prep"},
]

# Academic calendar setting for all scenarios
ACADEMIC_CONTEXT = "mid"  # Start mid-semester, building toward midterms


def build_academic_context_description(academic_start: str) -> str:
    """Build a data-rich academic context description using AcademicCalendar"""
    if not _CALENDAR_AVAILABLE:
        return f"Academic calendar: Start at '{academic_start}' point in semester."

    config = AcademicCalendarConfig(semester_start_point=academic_start)
    calendar = AcademicCalendar(config)

    lines = [f"ACADEMIC CALENDAR (start: '{academic_start}', 28-day window):"]

    # Sample key days
    prev_period = None
    for day in range(1, 29):
        day_cfg = calendar.get_day_config(day)
        period_name = day_cfg.academic_period.value
        if period_name != prev_period:
            m = day_cfg.modifiers
            lines.append(
                f"  Day {day:2d}+: {period_name.upper()} "
                f"[study_interest={m.study_tool_interest:.1f}, "
                f"stress={m.exam_stress:.1f}, "
                f"price_sensitivity={m.price_sensitivity:.1f}, "
                f"churn_risk={m.churn_risk:.1f}, "
                f"trial_pressure={m.trial_conversion_pressure:.1f}]"
            )
            prev_period = period_name

    return "\n".join(lines)


def build_scenario_requirement(scenario, academic_start=None):
    """Build the simulation requirement string for a scenario"""
    m = MARKETING[scenario["marketing"]]
    p = PRICING[scenario["pricing"]]
    e = EMPHASIS[scenario["emphasis"]]
    d = DESIGNS[scenario["design"]]

    return (
        f"Simulate the launch of Fizkonspektas at VU Physics Faculty (Sauletekis campus). "
        f"This is scenario {scenario['id']}: '{scenario['name']}'. "
        f"\n\nMARKETING STRATEGY ({scenario['marketing']}): {m} "
        f"\n\nPRICING MODEL ({scenario['pricing']}): {p} "
        f"\n\nPRODUCT EMPHASIS ({scenario['emphasis']}): {e} "
        f"\n\nDESIGN VARIANT ({scenario['design']}): {d} "
        f"\n\nACADEMIC CONTEXT: {build_academic_context_description(academic_start or ACADEMIC_CONTEXT)}"
        f"\n\nKEY METRICS TO TRACK: awareness_pct, trial_signups, conversion_rate, total_revenue_eur, "
        f"churn_rate, account_sharing_incidents, net_promoter_score, design_bounce_rate. "
        f"\n\nAGENT BEHAVIOR: Students must reason about price in terms of 'Jammi kebabs' "
        f"(9.99 EUR = 2 kebabs). They should consider group buys, free trial timing relative to exams, "
        f"and social proof from dorm clusters and study groups."
    )


def run_scenario(scenario, rounds, academic_start="mid"):
    """Run a single scenario through the full simulation pipeline"""
    scenario_id = scenario["id"]
    scenario_name = scenario["name"]

    print(f"\n{'='*60}")
    print(f">>> SCENARIO {scenario_id}: {scenario_name}")
    print(f">>> Marketing: {scenario['marketing']} | Pricing: {scenario['pricing']} | Emphasis: {scenario['emphasis']} | Design: {scenario['design']}")
    print(f"{'='*60}")

    if not os.path.exists(SEED_FILE):
        print(f"ERROR: {SEED_FILE} not found.")
        return None

    # Build requirement
    simulation_requirement = build_scenario_requirement(scenario, academic_start)

    additional_context = (
        "CRITICAL: This simulation takes place in Lithuania, at Vilnius University Physics Faculty. "
        "All agents must behave like Lithuanian university students. "
        "Use Lithuanian timezone (Europe/Vilnius). "
        "Platforms: Instagram, Telegram, Facebook groups, physical word-of-mouth, direct website visits. "
        "NOT Twitter or Reddit. "
        "Entity types must include: PhysicsStudent, Professor, DormFloor, StudyGroup, LectureCohort, MarketingChannel. "
        "Relationships must include: roommate_of, studies_with, influenced_by, saw_ad_on, shares_account_with. "
        f"Academic calendar: Start at '{academic_start}' point in semester."
    )

    # Step 1: Generate Ontology
    print("\n[Step 1] Generating Ontology...")
    with open(SEED_FILE, "rb") as f:
        files = {'files': (os.path.basename(SEED_FILE), f, 'text/markdown')}
        data = {
            'simulation_requirement': simulation_requirement,
            'project_name': f'Fizkonspektas - {scenario_id} - {scenario_name}',
            'additional_context': additional_context
        }
        response = requests.post(f"{BASE_URL}/graph/ontology/generate", files=files, data=data)

    if response.status_code != 200:
        print(f"FAILED Step 1: {response.text}")
        return None

    res_data = response.json()
    project_id = res_data['data']['project_id']
    print(f"OK: Project ID={project_id}")

    # Step 2: Build Knowledge Graph
    print("\n[Step 2] Building Knowledge Graph...")
    graph_id = "local_seed_fallback"
    response = requests.post(f"{BASE_URL}/graph/build", json={"project_id": project_id})
    if response.status_code == 200:
        task_id = response.json()['data']['task_id']
        for _ in range(GRAPH_BUILD_TIMEOUT):
            r = requests.get(f"{BASE_URL}/graph/task/{task_id}")
            task = r.json()
            status = task.get('status', 'unknown')
            if status == 'completed':
                built_id = task.get('result', {}).get('graph_id')
                if built_id:
                    graph_id = built_id
                print(f"OK: Graph built - {graph_id}")
                break
            elif status == 'failed':
                print(f"WARN: Graph build failed, using local seed fallback")
                break
            time.sleep(POLL_INTERVAL_FAST)

    # Step 3: Create Simulation (with new platform flags)
    print("\n[Step 3] Creating Simulation...")
    data = {
        "project_id": project_id,
        "graph_id": graph_id,
        "enable_instagram": True,
        "enable_telegram": True,
        "enable_facebook": True,
        "enable_physical": True,
        "enable_website": True,
    }
    response = requests.post(f"{BASE_URL}/simulation/create", json=data)
    if response.status_code != 200:
        print(f"FAILED Step 3: {response.text}")
        return None
    simulation_id = response.json()['data']['simulation_id']
    print(f"OK: Simulation ID={simulation_id}")

    # Step 4: Prepare Simulation
    print("\n[Step 4] Preparing Simulation (profile generation)...")
    data = {"simulation_id": simulation_id}
    response = requests.post(f"{BASE_URL}/simulation/prepare", json=data)
    if response.status_code != 200:
        print(f"FAILED Step 4: {response.text}")
        return None

    for _ in range(PREPARE_TIMEOUT):
        response = requests.post(f"{BASE_URL}/simulation/prepare/status", json=data)
        if response.status_code != 200:
            return None
        status_data = response.json().get('data', {})
        status = status_data.get('status', 'unknown')
        print(f"  Prep: {status} ({status_data.get('progress', 0)}%)")
        if status == 'ready':
            break
        elif status == 'failed':
            print(f"FAILED: {status_data.get('error')}")
            return None
        time.sleep(POLL_INTERVAL_PREPARE)
    else:
        print("TIMED OUT")
        return None

    # Step 5: Start Simulation
    print(f"\n[Step 5] Starting Simulation ({rounds} rounds, ~{rounds // 4} days)...")
    data = {
        "simulation_id": simulation_id,
        "max_rounds": rounds,
        "enable_graph_memory_update": False,
        "graph_id": graph_id
    }
    response = requests.post(f"{BASE_URL}/simulation/start", json=data)
    if response.status_code != 200:
        print(f"FAILED Step 5: {response.text}")
        return None

    # Step 6: Poll until complete
    print("\n[Step 6] Running simulation...")
    for _ in range(SIM_TIMEOUT):  # Up to 4 hours for long simulations
        response = requests.get(f"{BASE_URL}/simulation/{simulation_id}/run-status")
        status_data = response.json().get('data', {})
        total_rnd = status_data.get('total_rounds', rounds)
        current = status_data.get('current_round', 0)
        day = (current // 4) + 1 if current > 0 else 0
        print(f"  Round {current}/{total_rnd} (Day {day}) - {status_data.get('runner_status')}")
        if status_data.get('runner_status') in ['completed', 'failed']:
            break
        time.sleep(POLL_INTERVAL_SIM)

    # Save scenario metadata
    os.makedirs(RESULTS_DIR, exist_ok=True)
    meta = {
        "scenario": scenario,
        "simulation_id": simulation_id,
        "project_id": project_id,
        "graph_id": graph_id,
        "rounds": rounds,
        "academic_start": academic_start,
        "completed_at": datetime.now().isoformat(),
    }
    meta_path = os.path.join(RESULTS_DIR, f"{scenario_id}_meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Metadata saved to {meta_path}")

    print(f"\n--- SCENARIO {scenario_id} COMPLETED ---")
    return simulation_id


def run_phase_1(rounds, academic_start="mid"):
    """Run all 9 Phase 1 scenarios"""
    print("\n" + "=" * 70)
    print("PHASE 1: Marketing x Pricing x Emphasis (9 scenarios, Design D1)")
    print("=" * 70)

    results = {}
    for scenario in PHASE_1_SCENARIOS:
        sim_id = run_scenario(scenario, rounds, academic_start)
        if sim_id:
            results[scenario["id"]] = sim_id
            print(f"OK: {scenario['id']} -> {sim_id}")
        else:
            print(f"FAILED: {scenario['id']}")

    # Save phase 1 results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    results_path = os.path.join(RESULTS_DIR, "phase_1_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nPhase 1 results: {results_path}")
    return results


def run_phase_2(top_scenario_ids, rounds, academic_start="mid"):
    """Run Phase 2: Top scenarios x 3 Design variants"""
    print("\n" + "=" * 70)
    print("PHASE 2: Top Scenarios x Design Variants (up to 9 scenarios)")
    print("=" * 70)

    # Build Phase 2 scenarios from top Phase 1 winners
    phase_2_scenarios = []
    for rank, sid in enumerate(top_scenario_ids[:3]):
        # Find the original Phase 1 scenario
        base = next((s for s in PHASE_1_SCENARIOS if s["id"] == sid), None)
        if not base:
            print(f"WARN: Scenario {sid} not found in Phase 1")
            continue

        for design_key in ["D1", "D2", "D3"]:
            new_scenario = {
                "id": f"P2-{base['id']}-{design_key}",
                "marketing": base["marketing"],
                "pricing": base["pricing"],
                "emphasis": base["emphasis"],
                "design": design_key,
                "name": f"{base['name']} + {design_key}",
            }
            phase_2_scenarios.append(new_scenario)

    results = {}
    for scenario in phase_2_scenarios:
        sim_id = run_scenario(scenario, rounds, academic_start)
        if sim_id:
            results[scenario["id"]] = sim_id

    # Save phase 2 results
    results_path = os.path.join(RESULTS_DIR, "phase_2_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nPhase 2 results: {results_path}")
    return results


def main():
    parser = argparse.ArgumentParser(description="Fizkonspektas Launch Simulation Runner")
    parser.add_argument("--mode", type=str, default="TEST", choices=["TEST", "PROD"],
                        help="TEST: 8 rounds (2 days). PROD: 112 rounds (28 days).")
    parser.add_argument("--phase", type=str, default="1", choices=["1", "2", "both"],
                        help="Which phase to run. '2' requires phase_1_results.json.")
    parser.add_argument("--academic-start", type=str, default="mid",
                        choices=["early", "mid", "pre_exam", "exam"],
                        help="Academic calendar start point.")
    parser.add_argument("--top-scenarios", type=str, default=None,
                        help="Comma-separated scenario IDs for Phase 2 (e.g., 'S4,S6,S8'). "
                             "If not provided, reads from phase_1_results.json.")
    args = parser.parse_args()

    rounds = 8 if args.mode == "TEST" else 112  # 2 days vs 28 days

    print(f"\nFizkonspektas Launch Simulation ({args.mode} MODE)")
    print(f"Rounds per scenario: {rounds} (~{rounds // 4} days)")
    print(f"Academic start: {args.academic_start}")

    if args.phase in ["1", "both"]:
        phase_1_results = run_phase_1(rounds, args.academic_start)

    if args.phase in ["2", "both"]:
        # Determine top scenarios for Phase 2
        if args.top_scenarios:
            top_ids = [s.strip() for s in args.top_scenarios.split(",")]
        else:
            # Try to read score-ranked top 3 from analysis report first
            analysis_path = os.path.join(RESULTS_DIR, "analysis_report.json")
            results_path = os.path.join(RESULTS_DIR, "phase_1_results.json")

            if os.path.exists(analysis_path):
                with open(analysis_path) as f:
                    analysis_data = json.load(f)
                ranked = analysis_data.get("phase_1_ranking", [])
                top_ids = [r["scenario"]["id"] for r in ranked[:3] if r.get("scenario", {}).get("id")]
                if top_ids:
                    print(f"Using top 3 from Phase 1 analysis (score-ranked): {top_ids}")
                else:
                    print("WARNING: analysis_report.json found but has no rankings. Run analyze_results.py after Phase 1.")
                    return
            elif os.path.exists(results_path):
                print("WARNING: No analysis_report.json found. Phase 1 results exist but haven't been analyzed.")
                print("Run: python analyze_results.py  -- then re-run Phase 2")
                print("Or provide --top-scenarios manually (e.g. --top-scenarios S4,S8,S6)")
                return
            else:
                print("ERROR: No Phase 1 results found. Run Phase 1 first or provide --top-scenarios.")
                return

        run_phase_2(top_ids, rounds, args.academic_start)

    print("\n" + "=" * 70)
    print("ALL SCENARIOS COMPLETED")
    print(f"Results saved to: {RESULTS_DIR}/")
    print("Run analyze_results.py to compare scenarios.")
    print("=" * 70)


if __name__ == "__main__":
    main()
