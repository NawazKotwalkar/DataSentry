<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=32&pause=1000&color=2EA3F2&center=true&vCenter=true&width=600&lines=DataSentry;Score+Your+Data's+Health;Severity-Weighted+Issue+Scoring;Audit.+Score.+Track.+Repeat." alt="Typing SVG" />

<p><strong>A data quality auditing platform — score, audit, and rank the severity of data issues, from a quick CSV check to a fully served API and dashboard.</strong></p>

<p>
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.110-teal?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-1.32-red?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-blue?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
</p>

<p>
  <img src="https://img.shields.io/badge/status-live-brightgreen?style=flat-square" />
</p>

<h3>
  🚀 <a href="https://datasentry.streamlit.app/">Live Dashboard</a> &nbsp;•&nbsp;
  📘 <a href="https://datasentry-07z4.onrender.com/docs">API Docs</a>
</h3>

</div>

---

> ⚠️ The API runs on Render's free tier and spins down after periods of inactivity. The first request after idle time can take 30–50 seconds to wake up — that's expected, not a bug.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [What It Does](#-what-it-does)
- [Live Demo Walkthrough](#-live-demo-walkthrough)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started)
- [Feature Guide](#-feature-guide)
  - [1. CLI](#1-cli--fastest-path-no-server-needed)
  - [2. Upload CSV](#2-upload-csv-dashboard--api)
  - [3. Connect DB Table](#3-connect-db-table-live-database-auditing)
  - [4. Sources & History](#4-sources--history)
  - [5. Trends](#5-trends)
  - [6. Custom Validation Rules](#6-custom-validation-rules)
- [API Reference](#-api-reference)
- [Tech Stack](#-tech-stack)
- [Testing](#-testing)
- [Roadmap](#-roadmap)
- [Author](#-author)

---

## 🔎 Overview

Bad data quietly costs organizations time and trust long before anyone notices — silently corrupting pipelines, models, and decisions. DataSentry tells you *what's wrong* and gives every issue a **severity-weighted score** you configure yourself, so the output reflects your priorities, not an invented industry average.

- **A pure, dependency-free audit engine and CLI** — point it at any CSV and get a health score in seconds, no server required
- **A full-stack service** — a FastAPI backend with Postgres persistence and a Streamlit dashboard, for a running, shareable tool rather than a one-off script

Both share the same core philosophy: profile the data, find the problems, and rank them by a severity weight you control.

---

## ✨ What It Does

<table>
<tr>
<td width="50%">

**🩺 Health Scoring**
Every dataset gets a single 0–100 score, broken down across five weighted dimensions: nulls, duplicates, format issues, outliers, and rule violations.

**🔍 Issue Detection**
Nulls, exact and key-based duplicates, malformed emails/phones/dates, statistical outliers (IQR + z-score), and multivariate anomalies (Isolation Forest). Columns that are almost entirely unique values (IDs, zip codes) are automatically excluded from outlier checks — a customer ID being numerically far from another isn't a data quality issue.

</td>
<td width="50%">

**⚖️ Severity-Weighted Scoring**
Every issue type carries a configurable weight (in `config/cost_config.yaml`), rolled into a total figure. This is a heuristic you tune to your own priorities — not a validated financial estimate.

**📈 Trend Tracking**
Every audit run is persisted, so you can watch a dataset's health score and severity-weighted total rise or fall over time.

</td>
</tr>
</table>

---

## 🎬 Live Demo Walkthrough

1. Open the **[live dashboard](https://datasentry.streamlit.app/)**
2. Upload the included `sample_data.csv` (or any CSV of your own) in the **Upload CSV** tab
3. Watch the health score, severity-weighted cost estimate, column profile, and issue breakdown render instantly
4. Check the **Trends** tab to see the score plotted across every run so far

No installation needed to try it — the dashboard talks to the live, publicly hosted API.

---

## 🏗 Architecture

```
DataSentry/
├── engine/          # pure Python + pandas + scikit-learn — no FastAPI, no DB, no UI
│   ├── profiler.py       # per-column stats: type, null %, unique count, min/max, top values
│   ├── duplicates.py     # row-level + key-based duplicate detection
│   ├── formats.py        # regex checks: emails, phones, mixed date formats
│   ├── outliers.py       # IQR / z-score + Isolation Forest
│   ├── rules.py          # user-defined YAML/JSON validation rules
│   ├── scoring.py        # weighted formula → per-column and per-dataset health score
│   ├── cost.py           # severity-weighted score per issue type (configurable, not validated $)
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
├── scripts/
│   └── generate_test_data.sql  # generates 50K-row test tables with planted data quality issues
├── cli.py           # `python cli.py audit data.csv` — no server needed
├── sample_data.csv  # sample dataset with planted issues, for trying the CLI
└── requirements.txt
```

> **The one rule that holds the core together:** `engine/` never imports FastAPI, SQLAlchemy, or Streamlit. It takes a DataFrame in, returns a plain `AuditReport` dataclass out. The API and dashboard are adapters built around that pure core — not entangled with it.

---

## 🚀 Getting Started

<details>
<summary><strong>Option A — Just the engine and CLI (fastest, no server)</strong></summary>

```bash
git clone https://github.com/NawazKotwalkar/DataSentry.git
cd DataSentry
pip install -r requirements.txt

python cli.py audit sample_data.csv
```

</details>

<details>
<summary><strong>Option B — Full stack: API + Postgres + dashboard</strong></summary>

```bash
# 1. Start Postgres (local install, or any managed instance like Neon)

# 2. Run the API
uvicorn api.main:app --reload
# Docs at http://127.0.0.1:8000/docs

# 3. Run the dashboard (separate terminal)
streamlit run dashboard/app.py
# Opens at http://localhost:8501
```

By default the API connects to `postgresql://datasentry:datasentry@localhost:5432/datasentry` — override with a `DATABASE_URL` environment variable. The dashboard talks to `http://127.0.0.1:8000` by default — override with `DATASENTRY_API_URL`.

</details>

---

## 📚 Feature Guide

### 1. CLI — fastest path, no server needed

Run a full audit straight from the terminal:

```bash
python cli.py audit sample_data.csv
```

**With custom rules and duplicate-key detection:**

```bash
python cli.py audit sample_data.csv --rules config/rules.example.yaml --key-columns customer_id
```

**Export the full report as JSON:**

```bash
python cli.py audit sample_data.csv --json report.json
```

| Flag | Purpose |
|---|---|
| `--rules <path>` | Path to a YAML/JSON file of custom validation rules |
| `--key-columns <col1,col2>` | Comma-separated columns to check for duplicate keys |
| `--json <path>` | Write the full audit report to a JSON file |

---

### 2. Upload CSV (Dashboard & API)

**Via the dashboard:** open the **Upload CSV** tab, choose a file, optionally enter key columns, click **Run audit**. Results — health score, severity-weighted cost estimate, column profile table, and an issue-type breakdown — render immediately below.

**Via the API directly:**

```bash
curl -X POST "https://datasentry-07z4.onrender.com/audit/upload" \
  -F "file=@sample_data.csv" \
  -F "key_columns=customer_id"
```

Returns a JSON summary with the audit run's `id`, `health_score`, `total_cost`, `row_count`, and `column_count`.

---

### 3. Connect DB Table (live database auditing)

Audit a table in *any* database you have credentials for — the same engine that powers CSV uploads, pointed at a live table via `pandas.read_sql_table()`.

> ⚠️ **Disabled in the public demo, by design.** Typing live database credentials into a hosted web form is a real risk — a password can pass through server memory, request logs, and crash traces even when nothing is intentionally stored. Rather than ask you to trust a warning label, this feature is **off by default** on the public dashboard. The `"Connect DB table"` tab explains this and points here.

**To try it yourself, locally, against a database you control:**

1. Run the API and dashboard locally (see [Getting Started](#-getting-started))
2. Set an environment variable before starting the dashboard:
```bash
   export ENABLE_DB_AUDIT_UI=true   # Windows: set ENABLE_DB_AUDIT_UI=true
   streamlit run dashboard/app.py
```
3. In the now-visible form, fill in:

   | Field | Example |
   |---|---|
   | SQLAlchemy connection string | `postgresql://user:password@host:5432/dbname` |
   | Table name | `orders` |
   | Key column(s) | `order_id` |

4. Click **"Run audit"** — results render the same as a CSV upload. The connection string is never persisted; only the audit *results* are saved, same as any other run.

**Need test data to try this against?** `scripts/generate_test_data.sql` creates two tables — `customers` and `orders` — with 50,000 rows each and realistic, intentionally planted data quality issues (nulls, duplicates, negative values, inconsistent formatting). Run it with:

```bash
psql "your_connection_string" -f scripts/generate_test_data.sql
```

**Via the API directly** (same opt-in reasoning applies — only point this at a database you own):

```bash
curl -X POST "http://127.0.0.1:8000/audit/db-table" \
  -H "Content-Type: application/json" \
  -d '{
    "connection_string": "postgresql://user:password@host:5432/dbname",
    "table_name": "orders",
    "options": { "key_columns": ["order_id"] }
  }'
```

---

### 4. Sources & History

Every dataset you've ever audited — CSV or DB table — shows up in the **Sources & history** tab, with its name, type, and when it was first audited. This is how DataSentry tells apart "this CSV" from "that live table" across many runs.

---

### 5. Trends

Pick any source from the dropdown to see:
- **Health score over time** — a line chart across every audit run for that source
- **Cost over time** — how the severity-weighted total has moved
- **Full run history table** — every run's row count, column count, score, and severity-weighted cost, most recent first

This is what turns a one-off audit into ongoing monitoring — re-run an audit on the same source periodically and watch whether things are improving or degrading.

---

### 6. Custom Validation Rules

Define your own business rules in YAML (see `config/rules.example.yaml`):

```yaml
rules:
  - name: customer_id_required
    column: customer_id
    type: not_null

  - name: order_amount_positive
    column: order_amount
    type: min_value
    value: 0

  - name: status_allowed_values
    column: status
    type: allowed_values
    values: ["pending", "shipped", "delivered", "cancelled"]

  - name: email_basic_pattern
    column: email
    type: regex
    pattern: "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$"
```

| Rule type | Checks |
|---|---|
| `not_null` | Column has no missing values |
| `unique` | Column has no duplicate values |
| `min_value` / `max_value` | Numeric column stays within bounds |
| `allowed_values` | Column values fall within an allowed set |
| `regex` | Column values match a pattern |

Pass the rules file via `--rules` on the CLI, or via the `options.rules` field on `POST /audit/db-table`.

---

## 🔌 API Reference

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | `GET` | Health check |
| `/audit/upload` | `POST` | Audit an uploaded CSV |
| `/audit/db-table` | `POST` | Audit a live database table via a connection string |
| `/sources` | `GET` | List every dataset audited so far |
| `/audit-runs/{id}` | `GET` | Full detail for one run — column stats and issues |
| `/trends/{source_id}` | `GET` | Health score and severity-weighted cost history for a source |

Full interactive documentation, with request/response schemas and a "Try it out" button for every endpoint, is available at **[/docs](https://datasentry-07z4.onrender.com/docs)**.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Audit engine | Python, Pandas, scikit-learn |
| API | FastAPI, Pydantic |
| Database | PostgreSQL + SQLAlchemy ORM |
| Dashboard | Streamlit |
| Config | YAML / JSON |
| Testing | pytest |
| Hosting | Render (API), Neon (Postgres), Streamlit Community Cloud (dashboard) |

---

## ✅ Testing

```bash
pytest tests/
```

`tests/test_crud.py` runs against an in-memory SQLite database, so it doesn't require Postgres to be running. Every engine module (`profiler`, `duplicates`, `formats`, `outliers`, `rules`, `scoring`, `cost`, `audit`) has dedicated unit coverage.

---

## 🗺 Roadmap

DataSentry is under active development. Coming soon:

- 🐳 **Docker** — a single `docker-compose up` bringing up Postgres, the API, and the dashboard together

## 👤 Author

**Nawaz Kotwalkar**

<p>
  <a href="https://linkedin.com/in/nawazkotwalkar"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" /></a>
  <a href="https://github.com/NawazKotwalkar"><img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" /></a>
</p>

<div align="center">
<sub>Built to answer one question: given the issues in your data, which ones matter most?</sub>
</div>
