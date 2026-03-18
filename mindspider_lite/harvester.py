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
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def scrape_reddit_context(self, subreddit, queries):
        all_text = []
        for query in queries:
            print(f"Harvesting: {query}")
            url = f"https://www.reddit.com/r/{subreddit}/search/?q={query}&restrict_sr=1&t=year"
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    posts = soup.find_all(["h3", "p"])
                    for p in posts[:15]:
                        all_text.append(p.get_text().strip())
                time.sleep(1)
            except Exception as e: print(f"Error: {e}")
        return all_text

    def generate_world_book(self, raw_context):
        prompt = f"Transform this context into a 5000-word VU Physics World Book with 100 fictional students and chat logs: {json.dumps(raw_context[:30])}"
        try:
            response = requests.post(f"{self.base_url}/chat/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json={"model": self.model, "messages": [{"role": "user", "content": prompt}]})
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e: return str(e)

def run():
    spider = MindSpiderLite()
    raw = spider.scrape_reddit_context("lithuania", ["fizika", "Saulėtekis"])
    book = spider.generate_world_book(raw)
    with open("/home/zygis/MiroFish/plans/mega_seed_world_book.md", "w") as f: f.write(book)
    print("Done")

if __name__ == "__main__": run()