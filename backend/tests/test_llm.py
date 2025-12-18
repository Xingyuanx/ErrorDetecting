import asyncio
import os
import sys

# Add backend directory to sys.path to import app modules
# Current file: backend/tests/test_llm.py
# Parent: backend/tests
# Grandparent: backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.llm import LLMClient
from dotenv import load_dotenv

async def main():
    # Load .env from backend directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    load_dotenv(env_path)
    
    print("Testing LLMClient...")
    try:
        llm = LLMClient()
        print(f"Provider: {llm.provider}")
        print(f"Endpoint: {llm.endpoint}")
        print(f"Model: {llm.model}")
        
        messages = [{"role": "user", "content": "你好"}]
        print("Sending request...")
        resp = await llm.chat(messages)
        print("Response received:")
        # Check for reasoning content since we use DeepSeek R1
        if "choices" in resp and resp["choices"]:
            msg = resp["choices"][0].get("message", {})
            print(f"Reply: {msg.get('content')}")
            if "reasoning_content" in msg:
                print(f"Reasoning: {msg.get('reasoning_content')[:100]}...") # Print first 100 chars
        else:
            print(resp)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
