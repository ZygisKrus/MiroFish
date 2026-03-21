import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
model = os.getenv("LLM_MODEL_NAME", "stepfun/step-3.5-flash:free")
reasoning_model = os.getenv("LLM_REASONING_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")

print(f"Testing connection to {base_url}")
print(f"API Key present: {bool(api_key)}")

client = OpenAI(api_key=api_key, base_url=base_url)

def test_model(model_name):
    print(f"\nTesting model: {model_name}")
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Reply with 'Connection successful' and nothing else."}],
            max_tokens=10
        )
        print(f"Response: {response.choices[0].message.content}")
        print("✅ Success")
    except Exception as e:
        print(f"❌ Error: {e}")

test_model(model)
test_model(reasoning_model)