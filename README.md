# AgenticSearch

AgenticSearch is a multi-step web research pipeline that turns a natural-language question into a structured, source-backed table of entities. It combines query planning, web search, scraping, schema inference, and entity extraction into one streaming workflow.

The project also includes a small Gradio UI for trying the pipeline interactively.

## What it does

Given a user query, the app:

1. Uses an LLM to generate a few diverse search queries.
2. Sends those queries to Brave Search.
3. Scrapes the most relevant pages.
4. Infers a schema from the scraped content.
5. Extracts entities and attributes into a table.
6. Streams the evolving results to the UI.

## Project Structure

```text
src/
  main.py          # Core pipeline that orchestrates planning, search, scraping, schema generation, and extraction
  frontend.py      # Gradio interface for the pipeline
  utils/
    search.py      # Brave Search wrapper with local JSON cache
    scrape.py      # HTML scraping and text extraction
    plan_search.py  # LLM-based query planner
    schema_gen.py   # LLM-based schema inference
    extract.py      # LLM-based entity extraction and table merging
```

## Requirements

- Python 3.10+
- A valid `BRAVE_API_KEY`
- A valid `OPENROUTER_API_KEY`

## Installation

Create and activate a virtual environment, then install the dependencies:

```bash
pip install -r requirements.txt
```

If you prefer, you can install the packages manually:

```bash
pip install openrouter requests gradio bs4
```

## Environment Variables

Set these before running the app:

- `BRAVE_API_KEY`: Used for Brave Search API requests
- `OPENROUTER_API_KEY`: Used for all LLM calls through OpenRouter

Example on Windows PowerShell:

```powershell
$env:BRAVE_API_KEY="your-brave-key"
$env:OPENROUTER_API_KEY="your-openrouter-key"
```

## Running the App

### Gradio UI

Launch the interactive interface:

```bash
python src/frontend.py
```

This starts a local Gradio app where you can enter a query and watch the structured results update as pages are processed.

### Pipeline Only

If you want to use the pipeline directly in code, import `pipeline` from `src/main.py` and iterate over its streamed table output.

Example:

```python
from main import pipeline

for table in pipeline("best macarons in NYC"):
    print(table)
```

## How the Pipeline Works

### 1. Query Planning

`src/utils/plan_search.py` sends the user query to an LLM and asks for multiple search queries that cover different angles of the topic.

### 2. Search

`src/utils/search.py` sends each planned query to Brave Search and caches the results locally in `tmp/search_cache.json`.

### 3. Scraping

`src/utils/scrape.py` fetches each selected page, removes scripts and styles, and extracts page headers, a preview, and full text.

### 4. Schema Generation

`src/utils/schema_gen.py` looks at the scraped pages and asks the LLM to infer a useful set of attributes for the results table.

### 5. Entity Extraction

`src/utils/extract.py` extracts entities and attributes from each page and merges them into a single table with source URLs.

## Output Format

The pipeline produces a nested table-like structure where each entity contains attributes such as:

- `name`
- other inferred schema columns

Each cell stores:

- `value`: the extracted text
- `source`: the source URL for that value

The Gradio UI renders this as an HTML table, with values linked back to their sources.

## Cache

Search results are cached in:

```text
tmp/search_cache.json
```

The cache file is created automatically if it does not exist.

## Notes

- The pipeline is designed to be streaming, so intermediate results are yielded as the table is built.
- Some prompts request JSON from the model and then parse the returned text after removing markdown code fences.
- The implementation is experimental and may need tuning depending on the query type and the quality of the source pages.

## Troubleshooting

### Missing API Keys

If searches or LLM calls fail, verify that both environment variables are set.

### Empty Results

If the table stays empty, common causes are:

- Brave Search returns no relevant pages
- The scraper cannot fetch a page
- The LLM returns invalid JSON
- The query is too broad or too narrow

### Gradio Does Not Open

Make sure `gradio` is installed and that the script is being run from the project environment.

## License

No license file is currently included.
