
import sys
import os
from dotenv import load_dotenv

# Ensure we can import from backend/app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.utils.llm_client import LLMClient
from app.config import Config

def test_llm():
    print(f"Testing LLM with model: {Config.LLM_MODEL_NAME}")
    print(f"Base URL: {Config.LLM_BASE_URL}")
    try:
        client = LLMClient()
        response = client.chat([{"role": "user", "content": "Hello, respond with 'OK' if you see this."}])
        print(f"LLM Response: {response}")
        if "OK" in response.upper():
            print("LLM Test: SUCCESS")
        else:
            print(f"LLM Test: UNEXPECTED RESPONSE ({response})")
    except Exception as e:
        print(f"LLM Test: FAILED with error: {str(e)}")

def test_zep():
    print(f"Testing Zep with API Key: {Config.ZEP_API_KEY[:10]}...")
    # This is a bit harder to test without installing zep-python, 
    # but we can check if the key is set.
    if Config.ZEP_API_KEY and len(Config.ZEP_API_KEY) > 10:
        print("Zep Configuration: SUCCESS (Key found)")
    else:
        print("Zep Configuration: FAILED (Key missing or too short)")

if __name__ == "__main__":
    test_llm()
    test_zep()
