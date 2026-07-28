# 🛡️ DataSentry

**A data quality intelligence platform — score, audit, and quantify the cost of bad data, from a quick CSV check to a fully served API and dashboard.**

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-teal?style=flat-square&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red?style=flat-square&logo=streamlit)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=flat-square&logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## Overview

Bad data quietly costs organizations money long before anyone notices — silently corrupting pipelines, models, and decisions. Most tools tell you *what* is wrong. DataSentry tells you *what it costs*, and gives you two ways to get there:

- **A pure, dependency-free audit engine and CLI** — point it at any CSV and get a health score in seconds
- **A full-stack service** — a FastAPI backend with Postgres persistence and a Streamlit dashboard, for teams that want a running, shareable tool rather than a one-off script

Both share the same core philosophy: profile the data, find the problems, score the damage, and put a number on what it's costing you.

---

## What It Does

Point DataSentry at a dataset and it will:

- Score overall data health on a **0–100 scale**
- Detect **nulls, duplicates, malformed formats, and outliers** (statistical and ML-based)
- Apply your own **custom validation rules**
- Estimate the **dollar cost** of every issue found
- Track **quality trends** over time, run over run
- Serve results through a **REST API** and a **visual dashboard** — not just a terminal printout

---

## Architecture

```
DataSentry/
├── engine/          # pure Python + pandas + scikit-learn — no FastAPI, no DB, no UI
│   ├── profiler.py       # per-column stats: type, null %, unique count, min/max, top values
│   ├── duplicates.py     # row-level + key-based duplicate detection
│   ├── formats.py        # regex checks: emails, phones, mixed date formats
│   ├── outliers.py       # IQR / z-score + Isolation Forest
│   ├── rules.py          # user-defined YAML/JSON validation rules
│   ├── scoring.py        # weighted formula → per-column and per-dataset health score
│   ├── cost.py           # dollar cost estimate per issue type
│   └── audit.py          # orchestrator: run_audit(df, rules, cost_config) -> AuditReport
│
├── models/          # SQLAlchemy ORM + Postgres
│   ├── database.py       # engine/session setup, get_db() dependency
│   ├── schema.py         # Source, AuditRun, ColumnStat, Issue, RuleConfig tables
│   └── crud.py           # save_report(), get_history(), etc.
│
├── api/             # FastAPI service
│   ├── main.py
│   ├── schemas.py         # Pydantic request/response models
│   └── routes/            # audit.py, reports.py, trends.py
│
├── dashboard/       # Streamlit — talks only to the API over HTTP, never imports engine/ directly
│   └── app.py
│
├── config/
│   ├── rules.example.yaml
│   └── cost_config.yaml
│
├── tests/           # unit coverage across engine, CRUD, and audit orchestration
├── cli.py           # `python cli.py audit data.csv` — no server needed
├── sample_data.csv  # sample dataset with planted issues, for trying the CLI
├── docker-compose.yml, Dockerfile.api, Dockerfile.dashboard
└── requirements.txt
```

**The rule that holds the core together:** `engine/` never imports FastAPI, SQLAlchemy, or Streamlit. It takes a DataFrame in, returns a plain `AuditReport` dataclass out. The API, the dashboard, and Docker are all adapters built around that pure core — not entangled with it.

---

## Getting Started

### Option A — Just the engine and CLI (fastest path, no server needed)

```bash
pip install -r requirements.txt
python cli.py audit sample_data.csv
python cli.py audit sample_data.csv --rules config/rules.example.yaml --key-columns customer_id
python cli.py audit sample_data.csv --json report.json
```

### Option B — Full stack: API + Postgres + dashboard

**1. Start Postgres** (locally installed, or via `docker-compose up postgres`)

**2. Run the API**
```bash
uvicorn api.main:app --reload
```
Docs at `http://127.0.0.1:8000/docs`. Key endpoints:

| Endpoint | Purpose |
|---|---|
| `POST /audit/upload` | Audit an uploaded CSV |
| `POST /audit/db-table` | Audit a live database table via a connection string |
| `GET /sources` | List every dataset audited so far |
| `GET /audit-runs/{id}` | Full detail for one run — column stats and issues |
| `GET /trends/{source_id}` | Health score and cost history for a source |

By default the API connects to `postgresql://datasentry:datasentry@localhost:5432/datasentry`. Override with a `DATABASE_URL` environment variable to point at any Postgres instance, including a managed one like Neon.

**3. Run the dashboard**
```bash
streamlit run dashboard/app.py
```
Opens at `http://localhost:8501` with four tabs: **Upload CSV**, **Connect DB table**, **Sources & history**, and **Trends**. Override `DATASENTRY_API_URL` if the API isn't running on the default local address.

### Run tests
```bash
pytest tests/
```
`tests/test_crud.py` runs against an in-memory SQLite database, so it doesn't require Postgres to be running.

---

## Roadmap

DataSentry is under active development. Coming soon:

- 🐳 **Docker** — a single `docker-compose up` bringing up Postgres, the API, and the dashboard together, no manual setup required
- 🎨 **UI refresh** — a more polished, portfolio-ready dashboard experience: better visual hierarchy, richer issue drill-downs, and clearer trend visualizations

---

## Tech Stack

| Layer | Technology |
|---|---|
| Audit engine | Python, Pandas, scikit-learn |
| API | FastAPI, Pydantic |
| Database | PostgreSQL + SQLAlchemy ORM |
| Dashboard | Streamlit |
| Config | YAML / JSON |
| Testing | pytest |
| Infra (in progress) | Docker + docker-compose |

---

## Author

**Nawaz Kotwalkar**

- 🔗 [LinkedIn](https://linkedin.com/in/nawazkotwalkar)
- 🐙 [GitHub](https://github.com/NawazKotwalkar)