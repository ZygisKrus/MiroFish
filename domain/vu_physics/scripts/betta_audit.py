import os
import json
import requests
from dotenv import load_dotenv

load_dotenv("/home/zygis/MiroFish/.env")
API_KEY = os.environ.get("LLM_API_KEY", "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")
BASE_URL = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("LLM_REASONING_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")

def call_llm(system_prompt: str, user_prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.5
    }
    try:
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ Error calling LLM: {e}")
        return ""

def run_betta_audit():
    print("==================================================")
    print("🐟 STARTING BETTA-FISH MULTI-AGENT AUDIT")
    print("==================================================")
    
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    seed_path = os.path.abspath(os.path.join(SCRIPT_DIR, "../seeds/mega_seed_world_book.md"))
    
    if not os.path.exists(seed_path):
        print(f"❌ Error: Could not find {seed_path}")
        return
        
    with open(seed_path, "r", encoding="utf-8") as f:
        mega_seed = f.read()

    print(f"✅ Loaded Mega-Seed ({len(mega_seed)} characters). Dispatching to Agent Forum...")

    print("\n📊 Agent 1: Market Analyst is reviewing pricing and business models...")
    analyst_system = "You are a ruthless Market Analyst specializing in EdTech SaaS."
    analyst_prompt = f"Review this simulated world context for a physics study app called Fizkonspektas. Focus on the 9.99 EUR/month pricing and the free trial strategy. Identify 2 specific business hypotheses we should test (e.g., lifetime deal vs subscription, premium AI vs basic notes). CONTEXT: {mega_seed[:3000]}..."
    analyst_report = call_llm(analyst_system, analyst_prompt)

    print("🧠 Agent 2: Student Psychology Expert is reviewing emotional drivers...")
    psych_system = "You are a Student Psychology Expert who understands exam stress and academic pressure."
    psych_prompt = f"Review this simulated world context for a physics study app called Fizkonspektas. Focus on the anxiety around kolis (midterms), skola (failed exams), and the debate between using AI as a cheat vs a tutor. Identify 2 specific UI/UX or feature hypotheses we should test to alleviate guilt and maximize adoption. CONTEXT: {mega_seed[:3000]}..."
    psych_report = call_llm(psych_system, psych_prompt)

    print("🇱🇹 Agent 3: Lithuanian Cultural Auditor is reviewing local authenticity...")
    culture_system = "You are a Lithuanian Cultural Auditor, an alumnus of Vilnius University Physics Faculty (VU FF)."
    culture_prompt = f"Review this simulated world context for a physics study app called Fizkonspektas. Ensure the slang (Kamčiatka, Saulėtekis, fidi, laborai) is used correctly. Suggest 2 highly specific, hyper-local marketing slogans (like dorm stickers) that would genuinely resonate with a stressed VU student. CONTEXT: {mega_seed[:3000]}..."
    culture_report = call_llm(culture_system, culture_prompt)

    print("\n👑 Coordinator Agent: Synthesizing final A/B/C test scenarios...")
    coordinator_system = "You are the Lead Software Architect and Product Manager."
    coordinator_prompt = f"Synthesize the reports from your three expert agents into a finalized Refined Mega-Seed. Market Analyst: {analyst_report} | Psychology: {psych_report} | Culture: {culture_report}. TASK: 1. Define exactly 3 distinct Scenarios (A, B, C) that the MiroFish simulation should test. Each scenario should have a specific Marketing Slogan, Pricing Model, and UI focus. 2. Rewrite the ending of the original Mega-Seed to explicitly introduce these 3 scenarios into the simulation conflict."
    final_synthesis = call_llm(coordinator_system, coordinator_prompt)

    output_path = os.path.abspath(os.path.join(SCRIPT_DIR, "../seeds/refined_mega_seed.md"))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"{mega_seed}\n\n---\n\n## BETTA-FISH STRATEGIC INJECTIONS\n\n{final_synthesis}")
        
    print(f"\n✅ Betta-Audit Complete! Refined Seed saved to: {output_path}")

if __name__ == "__main__":
    run_betta_audit()
