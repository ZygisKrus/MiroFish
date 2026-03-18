import requests
import json
import time
import os

BASE_URL = "http://localhost:5001/api"
SEED_FILE = "plans/seed_document.md"

def run_scenario(scenario_name, marketing_strategy):
    print(f"\n{'='*50}")
    print(f"🚀 STARTING SCENARIO: {scenario_name}")
    print(f"{'='*50}")
    
    if not os.path.exists(SEED_FILE):
        print(f"ERROR: {SEED_FILE} not found.")
        return

    # 1. Generate Ontology (Step 1)
    print("\n[Step 1] Generating Ontology from Seed Document...")
    
    simulation_requirement = (
        f"Simulate the launch of the Fizkonspektas platform at the Vilnius University (VU) "
        f"Physics Faculty. The goal is to see how different student personas react to the platform. "
        f"MARKETING STRATEGY FOR THIS SCENARIO: {marketing_strategy}. "
        f"Simulate how students discover the platform through this strategy and their reactions."
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

    # 2. Build Graph (Step 2)
    print("\n[Step 2] Building GraphRAG Memory...")
    data = {
        'project_id': project_id,
        'chunk_size': 400
    }
    response = requests.post(f"{BASE_URL}/graph/build", json=data)
    if response.status_code != 200:
        print(f"FAILED Step 2: {response.text}")
        return None
    
    task_id = response.json()['data']['task_id']
    print(f"SUCCESS: Build Task Started ID={task_id}")

    # 3. Wait for build
    print("\n[Step 3] Waiting for Graph Build...")
    graph_id = None
    for _ in range(40):
        response = requests.get(f"{BASE_URL}/graph/task/{task_id}")
        task_data = response.json()['data']
        status = task_data['status']
        print(f"Current Status: {status} ({task_data.get('progress', 0)}%)")
        if status == 'completed':
            graph_id = task_data['result']['graph_id']
            print(f"SUCCESS: Graph Built ID={graph_id}")
            break
        elif status == 'failed':
            print(f"FAILED Build: {task_data.get('error')}")
            return None
        time.sleep(5)
    
    if not graph_id:
        print("TIMED OUT waiting for build")
        return None

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
    print("\n[Step 5] Preparing Simulation (Persona Generation)...")
    data = {"simulation_id": simulation_id}
    response = requests.post(f"{BASE_URL}/simulation/prepare", json=data)
    if response.status_code != 200:
        print(f"FAILED Step 5: {response.text}")
        return None
    
    print("Waiting for preparation...")
    for _ in range(40):
        response = requests.post(f"{BASE_URL}/simulation/prepare/status", json=data)
        status_data = response.json()['data']
        status = status_data['status']
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
    print("\n[Step 6] Starting Simulation (3 rounds)...")
    data = {
        "simulation_id": simulation_id,
        "max_rounds": 3,
        "enable_graph_memory_update": True,
        "graph_id": graph_id
    }
    response = requests.post(f"{BASE_URL}/simulation/start", json=data)
    if response.status_code != 200:
        print(f"FAILED Step 6: {response.text}")
        return None
    print(f"SUCCESS: Simulation Started")

    # 7. Poll status
    print("\n[Step 7] Polling Simulation Status...")
    for _ in range(20):
        response = requests.get(f"{BASE_URL}/simulation/{simulation_id}/run-status")
        status_data = response.json()['data']
        print(f"Status: {status_data['runner_status']}, Round: {status_data['current_round']}/3")
        if status_data['runner_status'] in ['completed', 'failed']:
            break
        time.sleep(15)

    print(f"\n--- SCENARIO {scenario_name} COMPLETED ---")
    return simulation_id

def main():
    print("Starting A/B Testing for Fizkonspektas Launch")
    
    sim_a = run_scenario(
        "Scenario A (Organic Launch)", 
        "No paid marketing. Relying purely on organic word-of-mouth in Facebook groups and Reddit."
    )
    
    if sim_a:
        print(f"Simulation A ID: {sim_a} (Keep this for the report agent)")
        
    sim_b = run_scenario(
        "Scenario B (Guerrilla Marketing)", 
        "Aggressive sticker campaign in Saulėtekis dorms with QR codes and provocative slogans like 'Failing Quantum Mechanics? Scan this'."
    )
    
    if sim_b:
        print(f"Simulation B ID: {sim_b} (Keep this for the report agent)")
        
    print("\nAll Scenarios Completed. Use the ReportAgent to analyze the results.")

if __name__ == "__main__":
    main()
