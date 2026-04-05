import requests
import json
import os

url = "https://api.search.brave.com/res/v1/web/search"
headers = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip",
    "X-Subscription-Token": os.getenv("BRAVE_API_KEY")
}

cache_file = "tmp/search_cache.json"
os.makedirs(os.path.dirname(cache_file), exist_ok=True)
if os.path.exists(cache_file):
    with open(cache_file, "r") as f:
        CACHE = json.load(f)
else:
    CACHE = {}


def search(query):
    query = query.strip().lower()
    if query in CACHE:
        return CACHE[query]
    
    try:
        response = requests.get(url, headers=headers, params={"q": query}, timeout=10)
        response.raise_for_status()
        
        results = response.json().get("web", {}).get("results", [])

        CACHE[query] = results
        with open(cache_file, "w") as f:
            json.dump(CACHE, f, indent=2)

        return results

    except requests.exceptions.Timeout:
        print(f"[SEARCH_ERROR] Timeout for query: {query}")
    except requests.exceptions.RequestException as e:
        print(f"[SEARCH_ERROR] Request failed: {e}")
    except ValueError:
        print(f"[SEARCH_ERROR] Invalid JSON response")
    except Exception as e:
        print(f"[SEARCH_ERROR] Unexpected error: {e}")
    return []
