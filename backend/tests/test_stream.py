import asyncio
import os
import sys
import json

# Add backend directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.llm import LLMClient
from dotenv import load_dotenv

async def main():
    # Load .env from backend directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    load_dotenv(env_path)
    
    print("Testing LLMClient Streaming...")
    try:
        llm = LLMClient()
        print(f"Provider: {llm.provider}")
        print(f"Endpoint: {llm.endpoint}")
        print(f"Model: {llm.model}")
        
        messages = [{"role": "user", "content": ""}]
        
        print("Sending streaming request...")
        stream_gen = await llm.chat(messages, stream=True)
        
        full_content = ""
        full_reasoning = ""
        
        print("\nStreaming Response:")
        async for chunk in stream_gen:
            choices = chunk.get("choices") or []
            if not choices:
                continue
            
            delta = choices[0].get("delta") or {}
            content = delta.get("content") or ""
            reasoning = delta.get("reasoning_content") or ""
            
            if reasoning:
                full_reasoning += reasoning
                print(f"[Reasoning] {reasoning}", end="", flush=True)
            if content:
                full_content += content
                print(content, end="", flush=True)
        
        print("\n\nStream Finished.")
        print(f"Full Content Length: {len(full_content)}")
        print(f"Full Reasoning Length: {len(full_reasoning)}")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(main())
