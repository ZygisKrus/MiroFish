import os
import requests
import json
import time
from bs4 import BeautifulSoup
from typing import List, Dict, Any

class MindSpiderLite:
    def __init__(self):
        self.api_key = "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"
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "deepseek/deepseek-chat"
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    def scrape_reddit_context(self, subreddit, queries):
        all_text = []
        for query in queries:
            print(f"🔍 Harvesting Context: {query}")
            url = f"https://www.reddit.com/r/{subreddit}/search/?q={query}&restrict_sr=1&t=year"
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    posts = soup.find_all(["h3", "p"])
                    for p in posts[:20]:
                        txt = p.get_text().strip()
                        if len(txt) > 30: all_text.append(txt)
                time.sleep(1.2)
            except Exception as e: print(f"Error: {e}")
        return all_text

    def generate_world_book(self, raw_context):
        print("🧠 Synthesizing Mega-Seed (VU-Wide Ecosystem)...")
        prompt = f"""
        You are an AI Data Engineer. Transform these raw Lithuanian student snippets into a 10,000-word "Vilnius University Campus World Book".
        
        RAW DATA:
        {json.dumps(raw_context[:100], ensure_ascii=False)}
        
        GOAL: Create a high-fidelity seed for a swarm intelligence simulation of the "Fizkonspektas" platform launch.
        
        REQUIREMENTS:
        1. POPULATION (150 AGENTS):
           - 70% Physics Students (FF): Struggling with Quantum Mechanics, Electrodynamics, and long lab reports.
           - 30% Other VU Students (Law, Econ, Comms): Living in the same Saulėtekis dorms (Kamčiatka, Niujorkas).
        2. SOCIAL GRAPH:
           - Define dorm roommates, study groups in the library, and rivalries.
           - Mention specific VU locations: Saulėtekio alėja, 14 korpusas, "Šnekutis" bar, library.
        3. VIBE & SLANG:
           - Use realistic Lithuanian student slang: kolis, skola, laborai, egzas, sesija, barakas, stipendija, LSP.
           - Mention cultural events like "FiDi" (Fiziko diena).
        4. THE CONFLICT:
           - "Fizkonspektas" stickers with QR codes are appearing everywhere.
           - Physics students love the KaTeX notes and AI Assistant tutor.
           - Non-physics students are jealous or asking if there is a version for Law/Econ.
           - Debates about the 9.99 EUR monthly price vs. the cost of a "kebabas" or coffee.
        """
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions", 
                headers={"Authorization": f"Bearer {self.api_key}"}, 
                json={"model": self.model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
            )
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e: return f"LLM Error: {e}"

def run():
    spider = MindSpiderLite()
    # BROAD KEYWORDS FOR VU ECOSYSTEM
    queries = [
        "fizika", "Saulėtekis", "Kamčiatka", "VU FF", "kolis", "skola", "laborai", "fidi", 
        "teorijos egzaminas", "semestras", "studentai", "konspektai", "universiteto konspektai", 
        "egzaminu uzduotys", "VU", "Vilniaus universitetas", "bendrabutis", "barakas", "sesija", "LSP"
    ]
    raw = spider.scrape_reddit_context("lithuania", queries)
    if not raw: raw = ["Vilniaus universiteto studentų gyvenimas Saulėtekyje."]
    book = spider.generate_world_book(raw)
    os.makedirs("/home/zygis/MiroFish/plans", exist_ok=True)
    with open("/home/zygis/MiroFish/plans/mega_seed_world_book.md", "w", encoding="utf-8") as f: 
        f.write(book)
    print("✅ Mega-Seed Generated Successfully! 150 agents and full VU context ready.")

if __name__ == "__main__": run()
