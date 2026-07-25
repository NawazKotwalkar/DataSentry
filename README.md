# DataSentry

A hybrid CS/DS data quality auditing engine. Point it at a dataset — a CSV or
a live database table — and it profiles the data, finds problems (nulls,
duplicates, malformed formats, statistical/ML-based outliers, custom rule
violations), scores overall health on a 0–100 scale, estimates the dollar
cost of those problems, and tracks quality over time.

## Status: Step 1 complete — Engine + CLI

This is a pure-Python audit engine with no server or database dependency,
plus a CLI so it's usable standalone. Subsequent build steps (FastAPI +
Postgres, Streamlit dashboard, Docker) are not part of this drop.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
python cli.py audit sample_data.csv
python cli.py audit sample_data.csv --rules config/rules.example.yaml --key-columns customer_id
python cli.py audit sample_data.csv --json report.json
```

## Run tests

```bash
pytest tests/
```

## Architecture

```
datasentry/
├── engine/          # pure Python + pandas + sklearn — no FastAPI, no DB, no I/O
│   ├── profiler.py      # per-column stats: type, null %, unique count, min/max, top values
│   ├── duplicates.py    # row-level + key-based duplicate detection
│   ├── formats.py       # regex checks: emails, phones, mixed date formats
│   ├── outliers.py      # IQR/z-score AND Isolation Forest
│   ├── rules.py         # applies user-defined YAML/JSON validation rules
│   ├── scoring.py       # weighted formula → per-column and per-dataset health score
│   ├── cost.py          # $ business-cost estimate per issue type
│   └── audit.py         # orchestrator: run_audit(df, rules, cost_config) -> AuditReport
├── config/
│   ├── rules.example.yaml
│   └── cost_config.yaml
├── tests/
├── cli.py           # `python cli.py audit data.csv` — no server needed
├── sample_data.csv  # sample dataset with planted issues, for trying the CLI
└── requirements.txt
```

**The one rule that holds it together:** `engine/` never imports FastAPI,
SQLAlchemy, or Streamlit. It takes a DataFrame in, returns a plain
`AuditReport` dataclass out. Everything else is an adapter plugged around
that pure core.

## Next build steps

1. **API + Postgres** — wrap the engine in FastAPI, persist results via
   SQLAlchemy, add the live-DB audit path.
2. **Streamlit dashboard** — upload/connect UI, score display, issue
   drill-down, anomaly chart, trend line.
3. **Docker** — `docker-compose up` brings up all three services together.
