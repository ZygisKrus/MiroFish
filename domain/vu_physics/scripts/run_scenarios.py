import requests
import json
import time
import os
import argparse

BASE_URL = "http://127.0.0.1:5001/api"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SEED_FILE = os.path.abspath(os.path.join(SCRIPT_DIR, "../seeds/refined_mega_seed.md"))


def run_scenario(scenario_name, marketing_strategy, requirement_keyword, rounds=3):
    print(f"\n{'='*50}")
    print(f"🚀 STARTING SCENARIO: {scenario_name}")
    print(f"{'='*50}")

    if not os.path.exists(SEED_FILE):
        print(f"ERROR: {SEED_FILE} not found.")
        return

    # 1. Generate Ontology (Step 1)
    # We still do this to create the PROJECT, even if we reuse the graph
    print("\n[Step 1] Generating Ontology from Seed Document...")

    simulation_requirement = (
        f"Simulate the launch of the Fizkonspektas platform at the Vilnius University (VU) "
        f"Physics Faculty. This is {scenario_name}. "
        f"MARKETING STRATEGY: {marketing_strategy}. "
        f"The simulation must focus on how students react to this specific strategy ({requirement_keyword})."
    )

    additional_context = (
        "CRITICAL: The simulation takes place in Lithuania. All generated personas must act and speak "
        "like Lithuanian university students, specifically from the VU Physics Faculty. "
        "Ensure entity types like 'PhysicsStudent', 'Professor', 'DormitoryCommunity', and 'TechCompany' are created. "
        "Personas should mention local concepts like 'Saulėtekis', 'Kamčiatka', exams ('koliokviumai'), "
        "and specific difficult subjects like 'Kvantinė mechanika' or 'Aukštoji matematika'."
    )

    with open(SEED_FILE, "rb") as f:
        files = {'files': (os.path.basename(SEED_FILE), f, 'text/markdown')}
        data = {
            'simulation_requirement': simulation_requirement,
            'project_name': f'Fizkonspektas - {scenario_name}',
            'additional_context': additional_context
        }
        response = requests.post(f"{BASE_URL}/graph/ontology/generate", files=files, data=data)

    if response.status_code != 200:
        print(f"FAILED Step 1: {response.text}")
        return None

    res_data = response.json()
    project_id = res_data['data']['project_id']
    print(f"SUCCESS: Project Created ID={project_id}")

    # [Step 2 & 3 SKIPPED - Zep Free Plan Limit Reached]
    print("\n[Step 2/3] Skipping Graph Build (Zep Free Plan Episode Limit Reached)")
    graph_id = "dummy_graph_id_for_local_bypass"

    # 4. Create Simulation
    print("\n[Step 4] Creating Simulation...")
    data = {
        "project_id": project_id,
        "graph_id": graph_id,
        "enable_twitter": True,
        "enable_reddit": True
    }
    response = requests.post(f"{BASE_URL}/simulation/create", json=data)
    if response.status_code != 200:
        print(f"FAILED Step 4: {response.text}")
        return None
    simulation_id = response.json()['data']['simulation_id']
    print(f"SUCCESS: Simulation Created ID={simulation_id}")

    # 5. Prepare Simulation
    print(f"\n[Step 5] Preparing Simulation (Persona Generation - Will limit based on mode)...")
    data = {"simulation_id": simulation_id}
    response = requests.post(f"{BASE_URL}/simulation/prepare", json=data)
    if response.status_code != 200:
        print(f"FAILED Step 5: {response.text}")
        return None

    print("Waiting for preparation...")
    for _ in range(150):
        response = requests.post(f"{BASE_URL}/simulation/prepare/status", json=data)
        if response.status_code != 200:
            print(f"FAILED to check prep status: {response.text}")
            return None
        status_data = response.json().get('data', {})
        status = status_data.get('status', 'unknown')
        print(f"Current Status: {status} ({status_data.get('progress', 0)}%)")
        if status == 'ready':
            print("SUCCESS: Simulation Ready")
            break
        elif status == 'failed':
            print(f"FAILED Preparation: {status_data.get('error')}")
            return None
        time.sleep(10)
    else:
        print("TIMED OUT waiting for preparation")
        return None

    # 6. Start Simulation
    print(f"\n[Step 6] Starting Simulation ({rounds} rounds)...")
    data = {
        "simulation_id": simulation_id,
        "max_rounds": rounds,
        "enable_graph_memory_update": False, # Disabled for long runs to avoid Zep overhead
        "graph_id": graph_id
    }
    response = requests.post(f"{BASE_URL}/simulation/start", json=data)
    if response.status_code != 200:
        print(f"FAILED Step 6: {response.text}")
        return None
    print(f"SUCCESS: Simulation Started")

    # 7. Poll status
    print("\n[Step 7] Polling Simulation Status...")
    for _ in range(480):
        response = requests.get(f"{BASE_URL}/simulation/{simulation_id}/run-status")
        status_data = response.json().get('data', {})
        total_rnd = status_data.get('total_rounds', rounds)
        print(f"Status: {status_data.get('runner_status')}, Round: {status_data.get('current_round', 0)}/{total_rnd}")
        if status_data.get('runner_status') in ['completed', 'failed']:
            break
        time.sleep(15)

    print(f"\n--- SCENARIO {scenario_name} COMPLETED ---")
    return simulation_id

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="TEST", choices=["TEST", "PROD"], help="TEST mode runs 2 rounds. PROD mode runs 200 rounds.")
    args = parser.parse_args()

    rounds = 2 if args.mode == "TEST" else 200

    print(f"Starting A/B/C Testing for Fizkonspektas Launch ({args.mode} MODE - {rounds} Rounds)")

    # Run Scenario A
    sim_a = run_scenario(
        "Scenario A (The Crammer's Exploit)",
        "€7.99/mo, 7-day free trial. Minimalist 'Rapid Cheatsheet' UI. Target: Desperate students cramming for exams who use personal Gmails and forget to cancel.",
        "Scenario A",
        rounds=rounds
    )
    if sim_a:
        print(f"Simulation A ID: {sim_a}")
    else:
        print("❌ Scenario A failed.")

    # Run Scenario B
    sim_b = run_scenario(
        "Scenario B (The Exclusive Drop)",
        "€7.99/mo, no trial. Waitlist only. 'Used by Top 1% of VU Students'. Target: FOMO-driven students who want to feel elite.",
        "Scenario B",
        rounds=rounds
    )
    if sim_b:
        print(f"Simulation B ID: {sim_b}")
    else:
        print("❌ Scenario B failed.")

    # Run Scenario C
    sim_c = run_scenario(
        "Scenario C (The Peer Pressure Nudge)",
        "Freemium model. Basic features free, but you see exactly who in your group has Premium. Target: Socially anxious students who don't want to fall behind their friends.",
        "Scenario C",
        rounds=rounds
    )
    if sim_c:
        print(f"Simulation C ID: {sim_c}")
    else:
        print("❌ Scenario C failed.")

    print("\n--- ALL SCENARIOS COMPLETED ---")
    print("Run analyze_results.py to compare the simulations.")

if __name__ == "__main__":
    main()
