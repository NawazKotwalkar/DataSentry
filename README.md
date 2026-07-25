### 🛡️ DataSentry — Data Quality Intelligence Platform

> A general-purpose data quality monitoring tool that scores data health,
> detects anomalies, and quantifies the business cost of bad data — instantly.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.50-red?style=flat-square&logo=streamlit)
![Great Expectations](https://img.shields.io/badge/Great_Expectations-1.17-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## The Problem

Organizations lose millions annually not because they lack data — but because
no one is watching its quality. Bad data silently corrupts pipelines, models,
and business decisions before anyone notices.

Most tools tell you **what** is wrong. DataSentry tells you **what it costs**.

---

## What DataSentry Does

Point it at any CSV dataset and it instantly:

- Scores data health from **0 to 100** across 4 quality dimensions
- Detects issues — nulls, duplicates, outliers, schema drift, negative values
- Quantifies the **business cost** of every issue in rupees
- Prioritizes fixes ranked by financial impact
- Auto-generates a **data dictionary** for any dataset
- Tracks **quality trends** across multiple uploads
- Compares **two datasets** side by side

---

## Quality Score Dimensions

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| Completeness | 45% | Missing and null values |
| Uniqueness | 25% | Duplicate records |
| Validity | 20% | Values within expected ranges |
| Consistency | 10% | Logical contradictions in data |

**Score Interpretation:**

| Score | Status | Action |
|-------|--------|--------|
| 95 – 100 | 🟢 Healthy | Monitor quarterly |
| 80 – 94 | 🟡 Warning | Resolve within 48 hours |
| Below 80 | 🔴 Critical | Immediate remediation required |

---

## Business Impact Layer

Every issue detected gets a rupee cost attached — not just a count:

```
342 nulls in Total Spend column     →  ₹1,84,000 in unprocessable transactions
6,000 duplicate records detected    →  ₹3,00,000 in double-processed refunds  
1,366 high churn-risk customers     →  ₹27,32,000 revenue at risk
─────────────────────────────────────────────────────
Total estimated cost of bad data    →  ₹59,00,030
```

This business cost layer is what separates DataSentry from standard
data quality tools that report counts and percentages only.

---

## Architecture

```
Any CSV File
      ↓
Layer 1 — Ingestion & Schema Validation
          src/ingest.py
          Loads data, validates schema, detects dtype drift, logs issues
      ↓
Layer 2 — Quality Scoring Engine (0–100)
          src/quality_score.py
          Scores completeness, uniqueness, validity, consistency
      ↓
Layer 3 — Business Rules Engine
          src/rules_engine.py
          Auto-detects issues using IQR, null checks, duplicate detection
          Attaches rupee cost to every finding
      ↓
Layer 4 — Dashboard & Reports
          app.py
          Streamlit UI — score display, issue breakdown, data dictionary,
          comparison, trend tracking, executive summary
```

---

## Dashboard Features

| Feature | Description |
|---------|-------------|
| Quality Score | Single 0–100 health score with HEALTHY / WARNING / CRITICAL status |
| Dimension Breakdown | Visual breakdown of all 4 quality dimensions |
| Business Impact | Every issue ranked by rupee cost |
| Action Queue | Prioritized fix list — highest cost issues first |
| Column Deep Dive | Per-column stats, distribution, null analysis |
| Data Dictionary | Auto-generated schema documentation for any dataset |
| Dataset Comparison | Side-by-side quality comparison of two CSVs |
| Score Trend | Quality score tracking across multiple uploads |
| Executive Summary | Plain-English paragraph summarizing findings |

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/NawazKotwalkar/DataSentry.git
cd DataSentry

# Create virtual environment
python -m venv venv

# Activate — Windows
venv\Scripts\activate

# Activate — Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12 | Core language |
| Pandas | 2.3 | Data manipulation |
| Great Expectations | 1.17 | Rules validation engine |
| Streamlit | 1.50 | Dashboard and UI |
| Matplotlib | 3.10 | Charts and visualizations |
| ydata-profiling | 4.18 | EDA reporting |

---

## Project Structure

```
DataSentry/
├── src/
│   ├── ingest.py           # Data ingestion & schema validation
│   ├── quality_score.py    # 4-dimension quality scoring engine
│   └── rules_engine.py     # Business rules & cost quantification
├── app.py                  # Streamlit dashboard
├── eda.py                  # Exploratory data analysis
├── requirements.txt
└── README.md
```

---

## How It Compares

| Capability | DataSentry | Standard Tools |
|------------|------------|----------------|
| Works on any CSV | ✅ | ❌ Often dataset-specific |
| Business cost in ₹ | ✅ | ❌ Counts and percentages only |
| Auto data dictionary | ✅ | ❌ Manual documentation |
| Fix priority queue | ✅ | ❌ No prioritization |
| Dataset comparison | ✅ | ❌ Single dataset |
| Executive summary | ✅ | ❌ Technical output only |
| Open source & lightweight | ✅ | ❌ Enterprise tools cost $50K+/year |

---

## Development Note

This project used AI-assisted development (Claude by Anthropic) for UI
scaffolding, CSS styling, and code iteration — a standard practice in
modern software development.

The core logic including the quality scoring algorithm, business rules
engine, ingestion pipeline, cost quantification framework, and
architectural decisions were designed and validated by the author.

Leveraging AI tooling to ship production-quality work faster is itself
a skill this project demonstrates.

---

## Live Demo

🚀 **[Launch DataSentry](https://datasentry.streamlit.app/)**

Upload any CSV to see the full analysis in action.

---

## Author

**Nawaz Kotwalkar**

- 🔗 [LinkedIn](https://linkedin.com/in/nawazkotwalkar)
- 🐙 [GitHub](https://github.com/NawazKotwalkar)

---
