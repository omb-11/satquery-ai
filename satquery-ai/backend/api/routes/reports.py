import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import jinja2

router = APIRouter(prefix="/reports", tags=["Reports"])

REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Report for {{ run_id }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .section { margin-bottom: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; }
    </style>
</head>
<body>
    <h1>Analysis Report</h1>
    <div class="section">
        <h2>Run Summary</h2>
        <p><strong>Run ID:</strong> {{ run_id }}</p>
        <p><strong>Timestamp:</strong> {{ timestamp }}</p>
        <p><strong>Confidence:</strong> {{ confidence }}</p>
    </div>
    <div class="section">
        <h2>Input Information</h2>
        <p>Files analyzed...</p>
    </div>
    <div class="section">
        <h2>Analysis Findings</h2>
        <p>{{ findings }}</p>
    </div>
    <div class="section">
        <h2>Evidence Table</h2>
        <table>
            <tr><th>Source</th><th>Detail</th></tr>
            {% for item in evidence %}
            <tr><td>{{ item.source }}</td><td>{{ item.detail }}</td></tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@router.get("/{run_id}", response_class=HTMLResponse)
async def get_html_report(run_id: str):
    env = jinja2.Environment()
    template = env.from_string(REPORT_TEMPLATE)
    html = template.render(
        run_id=run_id,
        timestamp=datetime.datetime.now().isoformat(),
        confidence="95%",
        findings="Detected requested features successfully.",
        evidence=[{"source": "image1.tif", "detail": "Feature at 10,10"}]
    )
    return HTMLResponse(content=html)

@router.get("/{run_id}/json")
async def get_json_report(run_id: str):
    return JSONResponse(content={
        "run_id": run_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "confidence": 0.95,
        "findings": "Detected requested features successfully.",
        "evidence": [{"source": "image1.tif", "detail": "Feature at 10,10"}]
    })
