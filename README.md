# DataSentry

A hybrid CS/DS data quality auditing engine. Point it at a dataset — a CSV or
a live database table — and it profiles the data, finds problems (nulls,
duplicates, malformed formats, statistical/ML-based outliers, custom rule
violations), scores overall health on a 0–100 scale, estimates the dollar
cost of those problems, and tracks quality over time.

## Status: Step 3 complete — Engine + CLI + API + Postgres + Dashboard

Step 1 (pure engine + CLI) works standalone with no server or database.
Step 2 adds a FastAPI layer that persists every audit run to Postgres via
SQLAlchemy, plus a live-DB-table audit path. Step 3 adds a Streamlit
dashboard that talks only to the API over HTTP — it never imports `engine/`
or `models/` directly. Docker compose-up-everything (Step 4) is not part of
this drop yet.

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

## Run the API (Step 2)

Start a local Postgres instance:

```bash
docker-compose up -d
```

Then run the API:

```bash
uvicorn api.main:app --reload
```

Docs at `http://127.0.0.1:8000/docs`. Key endpoints:

- `POST /audit/upload` — multipart CSV upload, optional `?key_columns=id,other`
- `POST /audit/db-table` — body: `{"connection_string": "...", "table_name": "...", "options": {...}}`
- `GET /sources` — list every dataset that's been audited
- `GET /audit-runs/{id}` — full detail for one run, including column stats and issues
- `GET /trends/{source_id}` — health score history for a source, most recent first

By default the API connects to `postgresql://datasentry:datasentry@localhost:5432/datasentry`.
Override with a `DATABASE_URL` environment variable.

## Run the dashboard (Step 3)

With the API already running (`uvicorn api.main:app --reload`), in a
separate terminal:

```bash
streamlit run dashboard/app.py
```

Opens at `http://localhost:8501`. Four tabs:

- **Upload CSV** — pick a file, optionally set key columns for duplicate
  detection, run the audit, see the health score, cost estimate, column
  profile, and issue breakdown
- **Connect DB table** — audit a live table via a SQLAlchemy connection
  string, same result view
- **Sources & history** — every dataset audited so far
- **Trends** — health score and cost over time for a chosen source

By default the dashboard talks to `http://127.0.0.1:8000`. Override with a
`DATASENTRY_API_URL` environment variable if the API runs elsewhere.

## Run tests

```bash
pytest tests/
```

`tests/test_crud.py` runs against an in-memory SQLite DB, so it doesn't
require Postgres to be running.

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
├── models/          # SQLAlchemy ORM + Postgres
│   ├── database.py      # engine/session setup, get_db() dependency
│   ├── schema.py         # Source, AuditRun, ColumnStat, Issue, RuleConfig tables
│   └── crud.py           # save_report(), get_history(), etc.
├── api/             # FastAPI
│   ├── main.py
│   ├── schemas.py         # Pydantic request/response models
│   └── routes/            # audit.py, reports.py, trends.py
├── dashboard/       # Streamlit — only talks to the API, never imports engine/ directly
│   └── app.py
├── config/
│   ├── rules.example.yaml
│   └── cost_config.yaml
├── tests/
├── cli.py           # `python cli.py audit data.csv` — no server needed
├── sample_data.csv  # sample dataset with planted issues, for trying the CLI
├── docker-compose.yml  # local Postgres for API dev/testing
└── requirements.txt
```

**The one rule that holds it together:** `engine/` never imports FastAPI,
SQLAlchemy, or Streamlit. It takes a DataFrame in, returns a plain
`AuditReport` dataclass out. Everything else is an adapter plugged around
that pure core.

## Next build steps

1. **Docker** — expand `docker-compose.yml` so `docker-compose up` brings up
   Postgres, the API, and the dashboard together in one command.
