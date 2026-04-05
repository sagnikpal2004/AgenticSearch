from openrouter import OpenRouter
import json
import os
import re

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
client = OpenRouter(api_key=OPENROUTER_API_KEY)

PLANNING_MODELS = [
    "openai/gpt-oss-20b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "openrouter/auto"
]

prompt = """You are a search query planner.

Given a user query, generate {n} diverse and effective search queries 
that would help retrieve comprehensive information.

Make sure:
- queries are diverse
- cover different angles
- are concise and realistic
- Do NOT include years

Return JSON:
"queries": [...]

User query: {q}
"""

def plan_search(query, n=3):
    query = prompt.format(q=query.lower().strip(), n=n)
    response = client.chat.send(models=PLANNING_MODELS, messages=[{"role": "user", "content": query}])
    text = response.choices[0].message.content

    text = re.sub(r"```json|```", "", text).strip()
    try:
        return json.loads(text)["queries"]
    except:
        print(f"[PLAN_ERROR] Invalid JSON response")
    return []

