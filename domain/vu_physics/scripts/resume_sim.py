import requests
import time
import sys

BASE_URL = "http://localhost:5001/api"
simulation_id = "sim_bfa1f8dfa527"

print(f"\n[Step 5] Preparing Simulation (Claude 3.5 Persona Generation)...")
data = {"simulation_id": simulation_id}
response = requests.post(f"{BASE_URL}/simulation/prepare", json=data)
if response.status_code != 200:
    print(f"FAILED Step 5: {response.text}")
    sys.exit(1)

for i in range(12): # Monitor for 1 minute
    response = requests.post(f"{BASE_URL}/simulation/prepare/status", json=data)
    status_data = response.json()["data"]
    status = status_data["status"]
    prog = status_data.get("progress", 0)
    print(f"Current Status: {status} ({prog}%) - Attempt {i+1}")
    if status == "ready": break
    elif status == "failed":
        print(f"FAILED Preparation: {status_data.get('error')}")
        sys.exit(1)
    time.sleep(5)
