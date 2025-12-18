import asyncio
import os
import sys

# Add backend directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ops_tools import tool_web_search

async def main():
    print("Testing Web Search...")
    query = "今天星期几"
    print(f"Query: {query}")
    try:
        res = await tool_web_search(query)
        if "error" in res:
            print(f"Error: {res['error']}")
        else:
            print(f"Current Time: {res.get('current_time')}")
            print(f"Results found: {len(res.get('results', []))}")
            for i, r in enumerate(res.get("results", [])[:2]):
                print(f"[{i+1}] {r.get('title')} - {r.get('href')}")
                if r.get('full_content'):
                    print(f"    Full content len: {len(r.get('full_content'))}")
                    print(f"    Sample: {r.get('full_content')[:100]}...")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())
