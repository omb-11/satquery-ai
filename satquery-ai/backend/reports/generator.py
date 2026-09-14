"""
SatQuery AI — Report Generator
Generates HTML and JSON analysis reports.
"""
from __future__ import annotations
import json
import base64
from datetime import datetime
from pathlib import Path
from loguru import logger

from backend.core.config import settings

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SatQuery AI — Analysis Report</title>
<style>
  body { font-family: 'Segoe UI', Arial, sans-serif; background: #0a1628; color: #e2e8f0; margin: 0; padding: 20px; }
  .header { border-bottom: 2px solid #00a8ff; padding-bottom: 16px; margin-bottom: 24px; }
  .logo { font-family: monospace; font-size: 24px; color: #00ff87; letter-spacing: 4px; }
  .subtitle { color: #64748b; font-size: 12px; margin-top: 4px; }
  .section { background: #0f2040; border: 1px solid #1a3a6b; padding: 16px; margin-bottom: 16px; border-radius: 2px; }
  .section h2 { color: #00a8ff; font-size: 14px; text-transform: uppercase; letter-spacing: 2px; margin: 0 0 12px 0; border-bottom: 1px solid #1a3a6b; padding-bottom: 8px; }
  .finding { font-size: 18px; color: #e2e8f0; line-height: 1.6; }
  .confidence-high { color: #00ff87; }
  .confidence-medium { color: #ffb347; }
  .confidence-low { color: #ff4444; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th { background: #0a1628; color: #64748b; padding: 8px; text-align: left; border-bottom: 1px solid #1a3a6b; }
  td { padding: 8px; border-bottom: 1px solid #1a2a3a; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 2px; font-size: 11px; font-family: monospace; }
  .badge-green { background: rgba(0,255,135,0.15); color: #00ff87; border: 1px solid #00ff87; }
  .badge-amber { background: rgba(255,179,71,0.15); color: #ffb347; border: 1px solid #ffb347; }
  .badge-red { background: rgba(255,68,68,0.15); color: #ff4444; border: 1px solid #ff4444; }
  .trace-step { display: flex; align-items: center; gap: 12px; padding: 6px 0; border-bottom: 1px solid #1a2a3a; font-size: 12px; font-family: monospace; }
  .step-num { color: #64748b; width: 24px; }
  .step-status { width: 16px; }
  .step-tool { color: #ffb347; width: 180px; }
  .step-output { color: #94a3b8; flex: 1; }
  .step-time { color: #00a8ff; width: 60px; text-align: right; }
  .provenance { font-size: 11px; color: #475569; font-family: monospace; }
  .footer { border-top: 1px solid #1a3a6b; padding-top: 16px; margin-top: 24px; font-size: 11px; color: #475569; }
</style>
</head>
<body>
<div class="header">
  <div class="logo">SATQUERY AI</div>
  <div class="subtitle">Remote Sensing Intelligence Workstation — Analysis Report</div>
  <div class="subtitle">Generated: {generated_at} | Run ID: {run_id}</div>
</div>

<div class="section">
  <h2>1. Query</h2>
  <p class="finding">{query}</p>
</div>

<div class="section">
  <h2>2. Input Information</h2>
  <table>
    <tr><th>Mode</th><td>{input_mode}</td></tr>
    <tr><th>Task Type</th><td>{task_type}</td></tr>
    <tr><th>Files</th><td>{file_count} image(s)</td></tr>
  </table>
</div>

<div class="section">
  <h2>3. Finding</h2>
  <div class="finding">{answer}</div>
</div>

<div class="section">
  <h2>4. Confidence</h2>
  <p class="confidence-{confidence_level}">
    {confidence_level_upper} — {confidence_score:.2f}
  </p>
</div>

<div class="section">
  <h2>5. Evidence</h2>
  <table>
    <tr><th>#</th><th>Source</th><th>Claim</th><th>Category</th><th>Score</th></tr>
    {evidence_rows}
  </table>
</div>

<div class="section">
  <h2>6. Models & Tools Used</h2>
  <p>{models_used}</p>
</div>

<div class="section">
  <h2>7. Limitations</h2>
  <ul>
    {limitations_html}
  </ul>
</div>

<div class="section">
  <h2>8. Execution Trace</h2>
  {trace_html}
</div>

<div class="section">
  <h2>9. Provenance</h2>
  <div class="provenance">
    <div>Software: SatQuery AI v{app_version}</div>
    <div>Timestamp: {generated_at}</div>
    <div>Device: {device}</div>
    <div>Parameters: {parameters}</div>
  </div>
</div>

<div class="footer">
  SatQuery AI — Agentic Earth Observation Intelligence | ISRO SIH 2026<br>
  This report is generated from actual computed evidence. Claims marked as 'Inferred' or 'Estimated' carry uncertainty.
</div>
</body>
</html>"""


class ReportGenerator:
    """Generates HTML and JSON reports from run results."""

    def generate_html(self, run_data: dict) -> str:
        """Generate HTML report from run data dict."""
        try:
            evidence = run_data.get("evidence", [])
            trace = run_data.get("trace", [])
            confidence = run_data.get("confidence", {})
            limitations = run_data.get("limitations", [])

            # Evidence rows
            evidence_rows = ""
            for i, ev in enumerate(evidence[:20], 1):
                score = ev.get("score", 0)
                evidence_rows += f"""<tr>
                    <td>{i}</td>
                    <td><span class="badge badge-amber">{ev.get('source', 'unknown')}</span></td>
                    <td>{ev.get('claim', '')}</td>
                    <td>{ev.get('category', '')}</td>
                    <td>{score:.2f}</td>
                </tr>"""

            # Trace HTML
            trace_html = ""
            for step in trace:
                status = step.get("status", "")
                icon = "✓" if status == "done" else ("✗" if status == "error" else "○")
                trace_html += f"""<div class="trace-step">
                    <span class="step-num">{step.get('step_num', 0):02d}</span>
                    <span class="step-status">{icon}</span>
                    <span class="step-tool">{step.get('tool', '')}</span>
                    <span class="step-output">{step.get('output', '')[:100]}</span>
                    <span class="step-time">{step.get('elapsed_ms', 0):.0f}ms</span>
                </div>"""

            # Limitations
            limitations_html = "".join(f"<li>{lim}</li>" for lim in limitations) or "<li>None reported</li>"

            conf_level = confidence.get("level", "medium")
            conf_score = confidence.get("score", 0.0)

            html = HTML_TEMPLATE.format(
                generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                run_id=run_data.get("run_id", "unknown"),
                query=run_data.get("query", ""),
                input_mode=run_data.get("input_mode", ""),
                task_type=run_data.get("task_type", ""),
                file_count=len(run_data.get("input_paths", [])),
                answer=run_data.get("answer", "").replace("\n", "<br>"),
                confidence_level=conf_level,
                confidence_level_upper=conf_level.upper(),
                confidence_score=conf_score,
                evidence_rows=evidence_rows or "<tr><td colspan='5'>No evidence recorded</td></tr>",
                models_used=", ".join(run_data.get("models_used", [])) or "Not recorded",
                limitations_html=limitations_html,
                trace_html=trace_html or "<p>No trace recorded</p>",
                app_version=settings.app_version,
                device=settings.get_device(),
                parameters=json.dumps(run_data.get("parameters", {}), indent=2)[:500],
            )
            return html
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return f"<html><body><h1>Report Error</h1><p>{e}</p></body></html>"

    def generate_json(self, run_data: dict) -> dict:
        """Generate machine-readable JSON report."""
        return {
            "report_type": "SatQuery AI Analysis Report",
            "schema_version": "1.0",
            "generated_at": datetime.utcnow().isoformat(),
            "software": {
                "name": "SatQuery AI",
                "version": settings.app_version,
                "device": settings.get_device(),
            },
            "run": run_data,
        }

    def save_html(self, run_id: str, run_data: dict) -> Path:
        """Save HTML report to disk and return path."""
        html = self.generate_html(run_data)
        out_path = settings.reports_dir / f"{run_id}.html"
        out_path.write_text(html, encoding="utf-8")
        return out_path


report_generator = ReportGenerator()
