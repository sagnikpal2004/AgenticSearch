from openrouter import OpenRouter
import json
import re
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
client = OpenRouter(api_key=OPENROUTER_API_KEY)

PLANNING_MODELS = [
    "openai/gpt-oss-20b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "openrouter/auto"
]

block_template = """
--- PAGE {} ---
Title: {}
Description: {}
Headers: {}
Preview: {}
"""

prompt_template = prompt = """
You are an information extraction system.

Given a user query and some scraped web content, infer a clean schema
for a table of entities.

The schema should:
- Represent the main entities in the data
- Include 5-8 relevant attributes (columns)
- Use concise, consistent names
- Avoid redundant or overlapping fields

IMPORTANT:
- Do NOT include duplicate or overly similar attributes
- Keep schema general and reusable

Return ONLY valid JSON in this format:
"attributes": ["...", "...", "..."]

User query: {}

Context:
{}
"""

def schema_gen(scrapes, query, n=5):
    scrapes = scrapes[:n]

    context_blocks = []
    for i, s in enumerate(scrapes):
        context_blocks.append(block_template.format(
            i+1, 
            s.get("title", ""), 
            s.get("description", ""), 
            ", ".join(s.get("scrape_res", {}).get("headers", [])), 
            s.get("scrape_res", {}).get("preview", "")
        ).strip())
    context_text = "\n\n".join(context_blocks)

    response = client.chat.send(
        models = PLANNING_MODELS, 
        messages=[{"role": "user", "content": prompt_template.format(query, context_text)}]
    )
    text = response.choices[0].message.content

    text = re.sub(r"```json|```", "", text).strip()
    try:
        return json.loads(text)["attributes"]
    except:
        print(f"[PLAN_ERROR] Invalid JSON response")
    return []