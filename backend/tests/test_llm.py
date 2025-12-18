import asyncio
import os
import sys

# Add backend directory to sys.path to import app modules
# Current file: backend/tests/test_llm.py
# Parent: backend/tests
# Grandparent: backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.llm import LLMClient
from app.services.ops_tools import openai_tools_schema, tool_web_search
from dotenv import load_dotenv
import json

async def main():
    # Load .env from backend directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    load_dotenv(env_path)
    
    print("Testing LLMClient with Tools...")
    try:
        llm = LLMClient()
        print(f"Provider: {llm.provider}")
        print(f"Endpoint: {llm.endpoint}")
        print(f"Model: {llm.model}")
        print(f"Timeout: {llm.timeout}")
        
        messages = [{"role": "user", "content": "请联网查询今天的日期和星期"}]
        
        # 1. Get tools definition
        tools = openai_tools_schema()
        # Filter only web_search for this test
        chat_tools = [t for t in tools if t["function"]["name"] == "web_search"]
        
        print(f"Tools: {json.dumps(chat_tools, ensure_ascii=False)}")
        
        print("Sending initial request...")
        resp = await llm.chat(messages, tools=chat_tools)
        
        if "choices" in resp and resp["choices"]:
            msg = resp["choices"][0].get("message", {})
            tool_calls = msg.get("tool_calls")
            
            if tool_calls:
                print(f"Tool calls triggered: {len(tool_calls)}")
                # Append assistant message with tool_calls
                messages.append(msg)
                
                for tc in tool_calls:
                    fn = tc.get("function", {})
                    name = fn.get("name")
                    args_str = fn.get("arguments", "{}")
                    print(f"Executing tool: {name} with args: {args_str}")
                    
                    if name == "web_search":
                        try:
                            args = json.loads(args_str)
                            # Execute tool
                            tool_result = await tool_web_search(args.get("query"), args.get("max_results", 5))
                            
                            # Append tool result message
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tc.get("id"),
                                "name": name,
                                "content": json.dumps(tool_result, ensure_ascii=False)
                            })
                            print("Tool execution completed.")
                        except Exception as e:
                            print(f"Tool execution failed: {e}")
                
                # 2. Send follow-up request with tool results
                print("Sending follow-up request...")
                resp = await llm.chat(messages, tools=chat_tools)
                if "choices" in resp and resp["choices"]:
                    final_msg = resp["choices"][0].get("message", {})
                    print("\nFinal Reply:")
                    print(final_msg.get('content'))
                    if "reasoning_content" in final_msg:
                        print(f"\nReasoning:\n{final_msg.get('reasoning_content')}")
            else:
                print("No tool calls triggered.")
                print(f"Reply: {msg.get('content')}")
        else:
            print(resp)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(main())
