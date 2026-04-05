import requests
from bs4 import BeautifulSoup

def scrape(url):
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        headers = []
        for tag in soup.find_all(["h1", "h2", "h3"]):
            text = tag.get_text(strip=True)
            if text:
                headers.append(text)

        paragraphs = []
        for tag in soup.find_all("p"):
            text = tag.get_text(strip=True)
            if len(text) >= 40:
                paragraphs.append(text)
        preview = " ".join(paragraphs)[:1000]

        content = soup.get_text(separator=" ", strip=True)
        if len(preview) < 100:
            preview = content[:1000]
        

        return {
            "headers": headers,
            "preview": preview,
            "content": content
        }
    except:
        print(f"[SCRAPE_ERROR] Failed to scrape {url}")
    return None