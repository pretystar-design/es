"""Utility to convert a Grafana dashboard (JSON) to a Kibana dashboard (JSON) and translate Prometheus queries to Elasticsearch SQL (ESQL).

This is a **starter implementation** – real‑world conversion can be complex and may require
custom mappings for visualisation types, field names, and query semantics.

The script provides:
- `load_grafana_dashboard(path)` – reads a Grafana JSON dashboard.
- `convert_panel(panel)` – maps a Grafana panel to a Kibana visualisation stub.
- `promql_to_esql(promql)` – very naïve translation of common PromQL functions to ESQL.
- `assemble_kibana_dashboard(panels, title)` – builds a minimal Kibana dashboard object.
- CLI entry point to run the conversion.

You can extend the mapping dictionaries and the `promql_to_esql` logic to cover more cases.
"""

import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Helper: Very simple PromQL → ESQL translation (placeholder implementation)
# ---------------------------------------------------------------------------

def promql_to_esql(promql: str) -> str:
    """Convert a limited subset of PromQL expressions to Elasticsearch SQL.

    This function only handles a few common patterns and should be expanded
    for production use.
    """
    # Example: sum(rate(http_requests_total[5m])) => SELECT SUM(rate) FROM index WHERE @timestamp > now-5m
    # This simplistic approach extracts metric name and optional time window.
    # It does NOT cover functions, label matchers, aggregation, etc.
    metric_match = re.search(r"([a-zA-Z_][a-zA-Z0-9_]*)(?:\{[^}]*\})?", promql)
    if not metric_match:
        return "SELECT * FROM <index> WHERE <conditions>"
    metric = metric_match.group(1)

    # Detect a range selector like [5m]
    range_match = re.search(r"\[(\d+)([smhd])\]", promql)
    if range_match:
        value, unit = range_match.groups()
        # Map Prometheus units to Elasticsearch time units
        unit_map = {"s": "s", "m": "m", "h": "h", "d": "d"}
        esql_range = f"now-{value}{unit_map.get(unit, 'm')}"
    else:
        esql_range = "now"

    # Very naive SELECT clause – just the metric name
    esql = f"SELECT {metric} FROM <index> WHERE @timestamp > {esql_range}"
    return esql

# ---------------------------------------------------------------------------
# Mapping of Grafana panel types to Kibana visualization types (simplified)
# ---------------------------------------------------------------------------

GRAFANA_TO_KIBANA = {
    "graph": "line",
    "table": "data-table",
    "timeseries": "line",
    "heatmap": "heatmap",
    "stat": "metric",
    # Add more mappings as needed
}


def convert_panel(panel: dict) -> dict:
    """Convert a Grafana panel dict to a Kibana visualization stub.

    The returned dict follows Kibana's saved object schema minimally – you will
    likely need to adjust fields (e.g., index pattern, field names) after conversion.
    """
    graf_type = panel.get("type")
    kib_type = GRAFANA_TO_KIBANA.get(graf_type, "visualization")

    # Extract the Prometheus query if present (Grafana stores it under "targets")
    targets = panel.get("targets", [])
    esql_queries = []
    for tgt in targets:
        promql = tgt.get("expr") or tgt.get("query")
        if promql:
            esql_queries.append(promql_to_esql(promql))

    kibana_vis = {
        "type": kib_type,
        "title": panel.get("title", "Untitled"),
        "description": panel.get("description", ""),
        "queries": esql_queries,
        # Placeholder for the rest of Kibana visualization configuration
        "options": {},
    }
    return kibana_vis

# ---------------------------------------------------------------------------
# Dashboard assembly
# ---------------------------------------------------------------------------

def assemble_kibana_dashboard(kibana_panels: list, title: str) -> dict:
    """Create a minimal Kibana dashboard JSON object from converted panels."""
    dashboard = {
        "type": "dashboard",
        "title": title,
        "panels": [],
    }
    for idx, vis in enumerate(kibana_panels, start=1):
        panel_entry = {
            "panelIndex": str(idx),
            "gridData": {"x": 0, "y": (idx - 1) * 15, "w": 24, "h": 15, "i": str(idx)},
            "embeddableConfig": {},
            "type": "visualization",
            "id": f"vis-{idx}",
            "version": "7.17.0",
            "attributes": vis,
        }
        dashboard["panels"].append(panel_entry)
    return dashboard

# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def main(grafana_path: str, output_path: str, title: str = "Converted Dashboard"):
    graf_path = Path(grafana_path)
    if not graf_path.is_file():
        print(f"Grafana dashboard file not found: {grafana_path}", file=sys.stderr)
        sys.exit(1)

    with graf_path.open("r", encoding="utf-8") as f:
        grafana_dashboard = json.load(f)

    panels = grafana_dashboard.get("panels", [])
    kibana_vis = [convert_panel(p) for p in panels]
    kibana_dash = assemble_kibana_dashboard(kibana_vis, title)

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(kibana_dash, f, indent=2, ensure_ascii=False)
    print(f"Kibana dashboard written to {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_dashboard.py <grafana_json> <kibana_output_json> [title]", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "Converted Dashboard")
