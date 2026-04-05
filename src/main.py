from utils.extract import extract_entities
from utils.plan_search import plan_search
from utils.schema_gen import schema_gen
from utils.search import search
from utils.scrape import scrape

N = 3   # number of searches to make
M = 5   # number of webpages to scrape
O = 5   # number of webpages to use for schema_gen

def pipeline(x, N=3, M=5, O=5):

    planned_queries = plan_search(x)[:N]

    search_res = []
    for query in planned_queries:
        search_res.append(search(query))


    scrapes = []
    visited_urls = set()

    j = 0
    max_attempts = 50 
    attempts = 0

    while len(scrapes) < M and attempts < max_attempts:
        any_progress = False

        for webset in search_res:
            if j >= len(webset):
                continue

            website = webset[j]
            url = website.get("url")

            if not url or url in visited_urls:
                continue
            visited_urls.add(url)

            scrape_res = scrape(url)

            if scrape_res:
                website["scrape_res"] = scrape_res
                scrapes.append(website)
                any_progress = True

                if len(scrapes) >= M:
                    break

        j += 1
        attempts += 1

        if not any_progress:
            break
    print("scraping completed")

    schema = schema_gen(scrapes, x, O)

    table = {}

    for i, s in enumerate(scrapes):
        table = extract_entities(x, table, s, schema)
        print(f"\nAfter processing scrape {i + 1}:")
        print(table)
        yield table

    print(table)
    yield table