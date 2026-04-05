import gradio as gr
from main import pipeline

def table_to_html(table):
    if not table:
        return "<p>Loading...</p>"

    # Preserve the first-seen attribute order instead of sorting columns.
    all_attrs = []
    for entity in table.values():
        for attr in entity.keys():
            if attr not in all_attrs:
                all_attrs.append(attr)

    # Build HTML
    html = "<table border='1' style='border-collapse: collapse; width: 100%;'>"

    # Header row
    html += "<tr>"
    for attr in all_attrs:
        html += f"<th style='padding: 8px;'>{attr}</th>"
    html += "</tr>"

    # Rows
    for entity in table.values():
        html += "<tr>"

        for attr in all_attrs:
            if attr in entity:
                val = entity[attr]["value"]
                src = entity[attr]["source"]

                html += f"""
                <td style='padding: 8px;'>
                    <a href="{src}" target="_blank">{val}</a>
                </td>
                """
            else:
                html += "<td></td>"

        html += "</tr>"

    html += "</table>"
    return html

def run_pipeline(query):
    yield "<p><b>🔄 Starting pipeline...</b></p>"

    step = 1
    for table in pipeline(query):
        html = f"<p><b>🔄 Processing step {step}...</b></p>"
        html += table_to_html(table)
        step += 1
        yield html

    yield "<p><b>✅ Done!</b></p>" + table_to_html(table)

with gr.Blocks() as demo:
    gr.Markdown("# Agentic Search System")
    gr.Markdown("Streaming structured results with sources")

    query = gr.Textbox(label="Enter query", placeholder="Ask a question about a topic...")
    results = gr.HTML(label="Results")

    query.submit(fn=run_pipeline, inputs=query, outputs=results)

demo.launch()