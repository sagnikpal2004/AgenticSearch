from openrouter import OpenRouter
import json
import re
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
client = OpenRouter(api_key=OPENROUTER_API_KEY)

EXTRACTION_MODELS = [
    "qwen/qwen3.6-plus:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "openrouter/auto"
]

prompt_template = """
You are an information extraction system.
User query: {}

This is the current state of the results table:
{}

For the following attributes:
{}

Extract entities from the following webpage content to add missing cells or add new rows.
{}

IMPORTANT:
- Extract as many entities as possible
- Only include attributes that are present
- If an attribute is missing, omit it
- Do NOT hallucinate information
- Keep values concise

Return ONLY valid JSON as a list of entities:
{{
    "updates": {{
        "entity1": {{
            "attribute1": {{ "value": "..." }},
            "attribute2": {{ "value": "..." }}
        }}
    }},
    "additions": {{
        "entity2": {{
            "attribute2": {{ "value": "..." }},
            "attribute3": {{ "value": "..." }}
        }}
    }}
}}
"""

def merge_tables(table, res, url):

    # --- HANDLE UPDATES ---
    updates = res.get("updates", {})
    for entity_name, attrs in updates.items():
        key = entity_name.lower().strip()

        if key not in table:
            table[key] = {}

        # ensure name field exists
        if "name" not in table[key]:
            table[key]["name"] = {
                "value": entity_name,
                "source": url
            }

        for attr, val_obj in attrs.items():
            value = val_obj.get("value", "").strip()
            if not value:
                continue

            if attr not in table[key]:
                table[key][attr] = {
                    "value": value,
                    "source": url
                }
            else:
                existing = table[key][attr]["value"]

                # prefer better value
                if len(value) > len(existing):
                    table[key][attr] = {
                        "value": value,
                        "source": url
                    }

    # --- HANDLE ADDITIONS ---
    additions = res.get("additions", {})
    for entity_name, attrs in additions.items():
        key = entity_name.lower().strip()

        if key not in table:
            table[key] = {}

        # ensure name field exists
        if "name" not in table[key]:
            table[key]["name"] = {
                "value": entity_name,
                "source": url
            }

        for attr, val_obj in attrs.items():
            value = val_obj.get("value", "").strip()
            if not value:
                continue

            if attr not in table[key]:
                table[key][attr] = {
                    "value": value,
                    "source": url
                }
            else:
                existing = table[key][attr]["value"]

                if len(value) > len(existing):
                    table[key][attr] = {
                        "value": value,
                        "source": url
                    }

    return table

def extract_entities(query, table, page, schema):
    text = page["scrape_res"]["content"]

    response = client.chat.send(
        models = EXTRACTION_MODELS,
        messages = [{"role": "user", "content": prompt_template.format(query, table, ", ".join(schema), text)}]
    )
    raw = response.choices[0].message.content
    cleaned = re.sub(r"```json|```", "", raw).strip()

    try:
        res = json.loads(cleaned)
    except Exception as e:
        print("[EXTRACT_ERROR] Extraction failed:", e)
        return table
    
    return merge_tables(table, res, page["url"])