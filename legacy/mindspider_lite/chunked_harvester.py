import os
import requests
import json
import time
import random
from dotenv import load_dotenv

load_dotenv("/home/zygis/MiroFish/.env")
API_KEY = os.environ.get("LLM_API_KEY")
BASE_URL = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("LLM_REASONING_MODEL", "anthropic/claude-3.5-sonnet")

def call_llm(prompt: str, expect_json: bool = False):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=120
        )
        content = response.json()["choices"][0]["message"]["content"].strip()
        
        if expect_json:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            return json.loads(content)
        return content
    except Exception as e:
        print(f"❌ LLM Call Failed: {e}")
        return None

def generate_roster_batch(batch_num: int, batch_size: int = 50) -> list:
    print(f"Generating Student Roster Batch {batch_num} ({batch_size} students)...")
    prompt = f"""
    Generate a JSON array of {batch_size} fictional university students from Vilnius University.
    70% must be from the Physics Faculty (FF), 30% from other faculties (Law, Econ, Comms).
    All live in or hang out at Saulėtekis (Kamčiatka/Niujorkas dorms).
    
    Output strictly valid JSON matching this schema:
    [
      {{
        "id": "student_XX",
        "name": "Firstname Lastname",
        "major": "Physics/Law/Econ...",
        "year": "1st/2nd/3rd...",
        "mbti": "INTJ/ESFP...",
        "bio": "1 sentence description including a specific pain point (e.g., struggling with Quantum Mechanics, loves Šnekutis bar, hates early lectures)."
      }}
    ]
    Return ONLY the JSON array. Do not include introductory text.
    """
    students = call_llm(prompt, expect_json=True)
    return students if students else []

def generate_relationships(students: list) -> str:
    print("Generating Social Graph (Relationships)...")
    sample = json.dumps(random.sample(students, min(20, len(students))), ensure_ascii=False)
    prompt = f"""
    Based on this sample of students: {sample}
    Write a 500-word narrative describing the social dynamics of the Saulėtekis dorms (Kamčiatka). 
    Who is roommates with whom? Which study groups dominate the library? Who are the academic rivals?
    Use Lithuanian student slang (barakas, fidi, kolis).
    """
    return call_llm(prompt)

def generate_dialogue(topic: str, students: list) -> str:
    print(f"Generating Dialogue Thread: {topic}...")
    participants = json.dumps(students, ensure_ascii=False)
    prompt = f"""
    Write a 400-word realistic Reddit or Facebook Group comment thread about: {topic}.
    The following specific students are participating in the thread:
    {participants}
    
    Make it sound like a real, slightly toxic, stressed Lithuanian student forum. 
    Mix Lithuanian and English. Use slang (skola, egzas, laborai).
    Format as:
    **[Name]**: [Message]
    """
    return call_llm(prompt)

def build_mega_seed():
    print("🚀 Starting Chunked Generation of Mega-Seed...")
    
    all_students = []
    for i in range(1, 4):
        batch = generate_roster_batch(i, 50)
        if batch:
            for idx, s in enumerate(batch):
                s["id"] = f"student_{len(all_students) + idx + 1}"
            all_students.extend(batch)
        time.sleep(2)
        
    if len(all_students) < 50:
        print("❌ Failed to generate enough students. Aborting.")
        return

    print(f"✅ Generated {len(all_students)} unique students.")
    
    relationships = generate_relationships(all_students)
    
    dialogue_topics = [
        "Fizkonspektas QR stickers appeared on my dorm door. Is it a scam?",
        "Professor caught someone using an AI tutor for the Electrodynamics lab report.",
        "9.99 EUR a month for Fizkonspektas? I can barely afford Jammi kebabs.",
        "Passed my Quantum Mechanics kolis thanks to the new AI app. AMA.",
        "Why do physics students get all the cool tech tools? Law student complaining.",
        "The server crashed right before the deadline. Typical.",
        "Is relying on step-by-step KaTeX derivations going to ruin our actual problem-solving skills?",
        "FiDi is coming up, but I have 3 skolas. Should I use the AI to cram?"
    ]
    
    dialogues = []
    for topic in dialogue_topics:
        participants = random.sample(all_students, 4)
        thread = generate_dialogue(topic, participants)
        if thread:
            dialogues.append(f"### Thread: {topic}\n\n{thread}\n")
        time.sleep(2)

    print("🧩 Assembling the final World Book...")
    
    world_book = "# Vilnius University Campus World Book\n\n"
    world_book += "## 1. The Student Roster (150 Agents)\n\n"
    for s in all_students:
        world_book += f"- **{s.get('name', 'Unknown')}** ({s.get('major', 'Unknown')}, {s.get('year', 'Unknown')}, {s.get('mbti', 'Unknown')}): {s.get('bio', '')}\n"
        
    world_book += f"\n## 2. Social Graph & Dynamics\n\n{relationships}\n\n"
    world_book += "## 3. Simulated Chat Logs & Conflicts\n\n"
    world_book += "\n".join(dialogues)
    
    output_path = "/home/zygis/MiroFish/plans/mega_seed_world_book.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(world_book)
        
    print(f"🎉 Mega-Seed successfully generated and saved to: {output_path}")
    print(f"Total Character Count: {len(world_book)}")

if __name__ == "__main__":
    build_mega_seed()
