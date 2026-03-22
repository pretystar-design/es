import json
import subprocess
import os
from pathlib import Path


def test_conversion(tmp_path: Path):
    # Create a minimal Grafana dashboard JSON with one panel and a PromQL query
    grafana_dashboard = {
        "title": "Sample Grafana Dashboard",
        "panels": [
            {
                "id": 1,
                "title": "CPU Usage",
                "type": "graph",
                "targets": [
                    {"expr": "sum(rate(cpu_seconds_total[5m]))"}
                ]
            }
        ]
    }

    grafana_file = tmp_path / "grafana.json"
    grafana_file.write_text(json.dumps(grafana_dashboard), encoding="utf-8")

    output_file = tmp_path / "kibana.json"

    # Run the conversion script
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "convert_dashboard.py"
    subprocess.run([
        "python3",
        str(script_path),
        str(grafana_file),
        str(output_file),
        "Test Dashboard"
    ], check=True)

    # Verify the output Kibana dashboard JSON structure
    result = json.loads(output_file.read_text(encoding="utf-8"))
    assert result["type"] == "dashboard"
    assert result["title"] == "Test Dashboard"
    assert len(result["panels"]) == 1
    panel = result["panels"][0]["attributes"]
    # The conversion should have produced an ESQL query for the PromQL expression
    assert panel["queries"] == ["SELECT sum FROM <index> WHERE @timestamp > now-5m"]
    # Verify the Kibana visualisation type mapping (graph -> line)
    assert panel["type"] == "line"
