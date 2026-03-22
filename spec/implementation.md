# Grafana to Kibana Dashboard Conversion

## Overview

This repository contains a small utility that converts a Grafana dashboard definition (JSON) into a Kibana dashboard definition (JSON).  The conversion also translates Prometheus‑style queries (PromQL) used in Grafana panels into Elasticsearch SQL (ESQL) queries that can be understood by Kibana.

## Directory Layout

```
es/
├─ README.md                     # Project description
├─ spec/
│   ├─ es_dashboard.md          # User story (already created)
│   └─ implementation.md        # <‑‑ THIS DOCUMENT
├─ scripts/
│   └─ convert_dashboard.py      # Conversion script (Python 3)
├─ tests/
│   └─ test_convert_dashboard.py# Pytest based unit test
└─ .git/                         # Git metadata (auto‑generated)
```

## Detailed Implementation (Python)

**File:** `scripts/convert_dashboard.py`

```python
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
    # Extract metric name
    metric_match = re.search(r"([a-zA-Z_][a-zA-Z0-9_]*)(?:\{[^}]*\})?", promql)
    if not metric_match:
        return "SELECT * FROM <index> WHERE <conditions>"
    metric = metric_match.group(1)

    # Detect a range selector like [5m]
    range_match = re.search(r"\[(\d+)([smhd])\]", promql)
    if range_match:
        value, unit = range_match.groups()
        unit_map = {"s": "s", "m": "m", "h": "h", "d": "d"}
        esql_range = f"now-{value}{unit_map.get(unit, 'm')}"
    else:
        esql_range = "now"

    # Naïve SELECT clause – just the metric name
    return f"SELECT {metric} FROM <index> WHERE @timestamp > {esql_range}"

# ---------------------------------------------------------------------------
# Mapping of Grafana panel types to Kibana visualization types (simplified)
# ---------------------------------------------------------------------------

GRAFANA_TO_KIBANA = {
    "graph": "line",
    "timeseries": "line",
    "table": "data-table",
    "heatmap": "heatmap",
    "stat": "metric",
    # Extend as needed
}

def convert_panel(panel: dict) -> dict:
    """Convert a Grafana panel dict to a Kibana visualization stub.

    The returned dict follows Kibana's saved object schema minimally – you will
    likely need to adjust fields (e.g., index pattern, field names) after conversion.
    """
    graf_type = panel.get("type")
    kib_type = GRAFANA_TO_KIBANA.get(graf_type, "visualization")

    # Extract PromQL queries from Grafana panel "targets"
    esql_queries = []
    for tgt in panel.get("targets", []):
        promql = tgt.get("expr") or tgt.get("query")
        if promql:
            esql_queries.append(promql_to_esql(promql))

    return {
        "type": kib_type,
        "title": panel.get("title", "Untitled"),
        "description": panel.get("description", ""),
        "queries": esql_queries,
        "options": {},
    }

# ---------------------------------------------------------------------------
# Dashboard assembly – creates a minimal Kibana dashboard object
# ---------------------------------------------------------------------------

def assemble_kibana_dashboard(kibana_panels: list, title: str) -> dict:
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
# CLI entry point
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
```

## Usage Example

```bash
# Assume you have a Grafana JSON export saved as grafana.json
python scripts/convert_dashboard.py grafana.json kibana.json "My Kibana Dashboard"
```

The command will create `kibana.json` containing a Kibana‑compatible dashboard definition.

## Testing

Run the provided pytest suite:

```bash
cd es
pytest tests/test_convert_dashboard.py
```

All tests should pass, confirming that:
* A Grafana panel of type **graph** is mapped to a Kibana **line** visualisation.
* A simple PromQL expression (`sum(rate(cpu_seconds_total[5m]))`) is translated to an ESQL query like `SELECT sum FROM <index> WHERE @timestamp > now-5m`.

## Future Work

* **Full PromQL parser** – handle label matchers, functions, aggregations.
* **Index pattern handling** – allow user to specify the Kibana index pattern.
* **Panel layout** – preserve Grafana panel positions and sizes.
* **Support more panel types** – gauge, bar, heatmap, etc.
* **Error handling** – more descriptive messages when unsupported features are encountered.

---

*Repository*: https://github.com/pretystar-design/es
*Author*: TangJunXing (via OpenClaw)
*Created*: 2026‑03‑22
