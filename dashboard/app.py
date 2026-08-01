"""DataSentry Streamlit dashboard.

Talks only to the FastAPI layer over HTTP — never imports engine/ or
models/ directly, so the dashboard can be deployed independently of the
audit engine and database.

Run with:
    streamlit run dashboard/app.py
"""
from __future__ import annotations

import os

import pandas as pd
import requests
import streamlit as st

API_BASE_URL = os.environ.get("DATASENTRY_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="DataSentry", page_icon="💛", layout="wide")


# --------------------------------------------------------------------------
# Theme — warm, soft, unhurried. Cream surfaces, a rounded humanist body
# face, a gentle serif for headings, and motion that settles once rather
# than looping. Nothing alarms; even "needs attention" stays soft.
# --------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Nunito:wght@400;600;700;800&display=swap');

:root {
    --cream:        #FBF7F0;
    --cream-2:      #F3ECE1;
    --card:         rgba(255, 255, 255, 0.72);
    --card-solid:   #FFFFFF;
    --border-soft:  rgba(220, 207, 186, 0.65);
    --ink:          #2E2A24;
    --ink-muted:    #6B6155;
    --rose:         #C97F79;
    --rose-deep:    #A85850;
    --rose-wash:    rgba(201, 127, 121, 0.18);
    --sage:         #7F9470;
    --sage-deep:    #5B7049;
    --sage-wash:    rgba(127, 148, 112, 0.18);
    --amber:        #C99A57;
    --amber-deep:   #9C752E;
    --amber-wash:   rgba(201, 154, 87, 0.20);
    --shadow-soft:  0 6px 20px rgba(74, 66, 56, 0.08);
    --shadow-lift:  0 10px 28px rgba(74, 66, 56, 0.12);
    --glass-blur:   blur(16px);
}

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #FDF9F3 0%, #F7EEE4 45%, #F3E7DC 100%) !important;
    background-attachment: fixed;
    color: var(--ink);
    font-family: 'Nunito', sans-serif;
}

/* ---- Soft ambient color washes behind the glass, purely atmospheric ---- */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: -10%; left: -10%;
    width: 45%; height: 45%;
    background: radial-gradient(circle, rgba(201, 127, 121, 0.10) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}
[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    bottom: -10%; right: -10%;
    width: 50%; height: 50%;
    background: radial-gradient(circle, rgba(127, 148, 112, 0.10) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { visibility: hidden; }
#MainMenu, footer { visibility: hidden; }

.block-container { padding-top: 2rem; max-width: 1100px; position: relative; z-index: 1; }

/* ---- Gentle entrance — settles once, never loops ---- */
.ds-fade-in { animation: ds-fade-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) both; }
@keyframes ds-fade-up {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ---- Header ---- */
.ds-header {
    text-align: center;
    padding: 2.2rem 1.6rem 1.6rem;
    background: var(--card);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--border-soft);
    border-radius: 22px;
    box-shadow: var(--shadow-soft);
}
.ds-header-mark {
    font-size: 1.9rem;
    margin-bottom: 0.3rem;
    display: inline-block;
}
.ds-header-title {
    font-family: 'Fraunces', serif;
    font-weight: 500;
    font-size: 2.1rem;
    color: var(--ink);
    letter-spacing: -0.01em;
    margin: 0;
}
.ds-caption {
    font-family: 'Nunito', sans-serif;
    font-weight: 600;
    color: var(--ink-muted);
    font-size: 0.98rem;
    margin-top: 0.35rem;
}

/* ---- Tabs ---- */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(243, 236, 225, 0.55);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border-radius: 14px;
    padding: 5px;
    gap: 2px;
    border: 1px solid var(--border-soft);
}
[data-testid="stTabs"] button[role="tab"] {
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
    font-size: 0.88rem;
    color: var(--ink-muted);
    background: transparent;
    border-radius: 10px !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: var(--rose-deep);
    background: var(--card-solid) !important;
    box-shadow: var(--shadow-soft);
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: transparent !important; }
[data-testid="stTabs"] [data-baseweb="tab-border"] { background-color: transparent !important; }
[data-testid="stTabs"] [data-baseweb="tab-panel"] { padding-top: 1.6rem !important; }

/* ---- Inputs & uploader ---- */
[data-testid="stTextInput"] input, [data-testid="stFileUploaderDropzone"] {
    background: var(--card) !important;
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1.5px solid var(--border-soft) !important;
    color: var(--ink) !important;
    border-radius: 14px !important;
    font-family: 'Nunito', sans-serif;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--rose) !important;
    box-shadow: 0 0 0 3px var(--rose-wash);
}
[data-testid="stFileUploaderDropzone"] { border-style: dashed !important; padding: 1.2rem !important; }

/* ---- Buttons ---- */
.stButton > button {
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
    background: var(--rose-deep) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.55rem 1.3rem !important;
    box-shadow: var(--shadow-soft);
    transition: transform 0.18s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.18s ease, filter 0.18s ease;
}
.stButton > button:hover { filter: brightness(1.04); transform: translateY(-1px); box-shadow: var(--shadow-lift); }
.stButton > button:active { transform: translateY(0) scale(0.99); }
.stButton > button:disabled {
    background: var(--cream-2) !important;
    color: var(--ink-muted) !important;
    box-shadow: none;
}

/* ---- Metrics ---- */
[data-testid="stMetric"] {
    background: var(--card);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--border-soft);
    border-radius: 16px;
    padding: 1rem 1.1rem;
    box-shadow: var(--shadow-soft);
}
[data-testid="stMetricLabel"] {
    font-family: 'Nunito', sans-serif;
    color: var(--ink-muted);
    font-weight: 700;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
[data-testid="stMetricValue"] {
    font-family: 'Fraunces', serif;
    color: var(--ink);
    font-weight: 500;
}

/* ---- Dataframes & alerts ---- */
[data-testid="stDataFrame"] {
    background: var(--card);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--border-soft);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: var(--shadow-soft);
}

[data-testid="stAlert"] {
    background: var(--card) !important;
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border-radius: 14px;
    font-family: 'Nunito', sans-serif;
    border: 1px solid var(--border-soft);
}

hr { border-color: var(--border-soft) !important; margin: 1.6rem 0 !important; }

h1, h2, h3 { font-family: 'Fraunces', serif !important; font-weight: 500 !important; color: var(--ink) !important; }

/* ---- Circular health gauge — a soft, glowing ring rather than an alert ---- */
.ds-gauge-wrap {
    display: flex;
    align-items: center;
    gap: 1.6rem;
    background: var(--card);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--border-soft);
    border-radius: 20px;
    padding: 1.3rem 1.6rem;
    box-shadow: var(--shadow-soft);
}
.ds-gauge-svg circle.ds-gauge-track { fill: none; stroke: var(--cream-2); stroke-width: 9; }
.ds-gauge-svg circle.ds-gauge-fill {
    fill: none;
    stroke-width: 9;
    stroke-linecap: round;
    transform: rotate(-90deg);
    transform-origin: 50% 50%;
    transition: stroke-dashoffset 1.1s cubic-bezier(0.16, 1, 0.3, 1);
}
.ds-gauge-value {
    font-family: 'Fraunces', serif;
    font-size: 1.4rem;
    font-weight: 500;
    fill: var(--ink);
}
.ds-gauge-status {
    font-family: 'Nunito', sans-serif;
    font-size: 0.95rem;
    font-weight: 800;
    letter-spacing: 0.02em;
}
.ds-gauge-sub {
    font-family: 'Nunito', sans-serif;
    color: var(--ink-muted);
    font-weight: 600;
    font-size: 0.82rem;
    margin-top: 2px;
}

@media (prefers-reduced-motion: reduce) {
    .ds-fade-in {
        animation: none !important;
    }
    .ds-gauge-fill { transition: none !important; }
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# API helpers
# --------------------------------------------------------------------------

def api_get(path: str, params: dict | None = None) -> dict | list | None:
    try:
        resp = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=15)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Could not reach the DataSentry API at {API_BASE_URL}. Is `uvicorn api.main:app` running?")
        st.stop()
    except requests.exceptions.HTTPError as exc:
        st.error(f"API error: {exc}")
        return None


def api_post_upload(file, key_columns: str | None) -> dict | None:
    try:
        files = {"file": (file.name, file.getvalue(), "text/csv")}
        params = {"key_columns": key_columns} if key_columns else {}
        resp = requests.post(f"{API_BASE_URL}/audit/upload", files=files, params=params, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Could not reach the DataSentry API at {API_BASE_URL}. Is `uvicorn api.main:app` running?")
        return None
    except requests.exceptions.HTTPError as exc:
        st.error(f"Audit failed: {exc.response.text}")
        return None


def api_post_db_table(connection_string: str, table_name: str, key_columns: str | None) -> dict | None:
    try:
        body = {
            "connection_string": connection_string,
            "table_name": table_name,
        }
        if key_columns:
            body["options"] = {"key_columns": [c.strip() for c in key_columns.split(",")]}
        resp = requests.post(f"{API_BASE_URL}/audit/db-table", json=body, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Could not reach the DataSentry API at {API_BASE_URL}. Is `uvicorn api.main:app` running?")
        return None
    except requests.exceptions.HTTPError as exc:
        st.error(f"Audit failed: {exc.response.text}")
        return None


# --------------------------------------------------------------------------
# UI sections
# --------------------------------------------------------------------------

def render_score_gauge(score: float) -> None:
    score = min(max(score, 0.0), 100.0)

    if score >= 85:
        signal, label = "var(--sage-deep)", "Healthy"
    elif score >= 60:
        signal, label = "var(--amber-deep)", "Needs a little care"
    else:
        signal, label = "var(--rose-deep)", "Needs attention"

    radius = 42
    circumference = 2 * 3.14159265 * radius
    offset = circumference * (1 - score / 100)

    gauge_html = f"""
    <div class="ds-gauge-wrap ds-fade-in">
        <svg class="ds-gauge-svg" width="110" height="110" viewBox="0 0 110 110">
            <circle class="ds-gauge-track" cx="55" cy="55" r="{radius}"></circle>
            <circle class="ds-gauge-fill" cx="55" cy="55" r="{radius}"
                stroke="{signal}"
                stroke-dasharray="{circumference:.2f}"
                stroke-dashoffset="{offset:.2f}"></circle>
            <text x="55" y="61" text-anchor="middle" class="ds-gauge-value">{score:.1f}</text>
        </svg>
        <div>
            <div class="ds-gauge-status" style="color: {signal};">{label}</div>
            <div class="ds-gauge-sub">Health score, out of 100</div>
        </div>
    </div>
    """
    st.markdown(gauge_html, unsafe_allow_html=True)


def render_audit_result(result: dict) -> None:
    st.subheader("Audit result")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", result["row_count"])
    c2.metric("Columns", result["column_count"])
    c3.metric("Severity-weighted cost", f"${result['total_cost']:,.2f}")
    c4.metric("Audit run ID", result["id"])
    st.caption(
        "The cost figure is a configurable heuristic (issue count × your own per-issue weights), "
        "not a validated financial estimate. Adjust it in `config/cost_config.yaml`."
    )

    render_score_gauge(result["health_score"])

    st.divider()
    render_issue_drilldown(result["id"])


def render_issue_drilldown(audit_run_id: int) -> None:
    detail = api_get(f"/audit-runs/{audit_run_id}")
    if not detail:
        st.warning("Could not load issue detail for this audit run.")
        return

    st.subheader("Column profile")
    if detail["column_stats"]:
        stats_df = pd.DataFrame(detail["column_stats"])
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
    else:
        st.write("No column statistics available.")

    st.subheader(f"Issues found ({len(detail['issues'])})")
    if detail["issues"]:
        issues_df = pd.DataFrame(detail["issues"])
        issue_counts = issues_df["issue_type"].value_counts()
        col_chart, col_table = st.columns([1, 2])
        with col_chart:
            st.bar_chart(issue_counts)
        with col_table:
            st.dataframe(issues_df, use_container_width=True, hide_index=True)
    else:
        st.success("No issues found — this dataset is clean.")


def render_trend(source_id: int) -> None:
    history = api_get(f"/trends/{source_id}")
    if not history:
        st.info("No audit history yet for this source. Run an audit to start tracking trends.")
        return

    df = pd.DataFrame(history)
    df["run_at"] = pd.to_datetime(df["run_at"])
    df = df.sort_values("run_at")

    st.subheader("Health score over time")
    st.line_chart(df.set_index("run_at")["health_score"])

    st.subheader("Severity-weighted cost over time")
    st.line_chart(df.set_index("run_at")["total_cost"])

    st.subheader("Run history")
    st.dataframe(
        df[["id", "run_at", "row_count", "column_count", "health_score", "total_cost"]],
        use_container_width=True,
        hide_index=True,
    )


# --------------------------------------------------------------------------
# Page layout
# --------------------------------------------------------------------------

st.markdown(
    """
    <div class="ds-header ds-fade-in">
        <div class="ds-header-mark">💛</div>
        <p class="ds-header-title">DataSentry</p>
        <p class="ds-caption">A gentle way to see how your data is really doing.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

ENABLE_DB_AUDIT_UI = os.environ.get("ENABLE_DB_AUDIT_UI", "false").lower() == "true"

if "last_result" not in st.session_state:
    st.session_state.last_result = None

tab_upload, tab_db, tab_sources, tab_trends = st.tabs(
    ["Upload CSV", "Connect DB table", "Sources & history", "Trends"]
)

with tab_upload:
    st.subheader("Audit a CSV file")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    key_columns_input = st.text_input(
        "Key column(s) for duplicate detection (comma-separated, optional)",
        placeholder="e.g. customer_id",
        key="upload_key_columns",
    )

    if st.button("Run audit", type="primary", disabled=uploaded_file is None):
        with st.spinner("Running audit..."):
            result = api_post_upload(uploaded_file, key_columns_input or None)
        if result:
            st.session_state.last_result = result

    if st.session_state.last_result:
        st.divider()
        render_audit_result(st.session_state.last_result)

with tab_db:
    st.subheader("Audit a live database table")

    if not ENABLE_DB_AUDIT_UI:
        st.info(
            "This feature is disabled in the public demo. Entering live database "
            "credentials into a hosted web form is a real security risk — passwords "
            "can pass through server memory, logs, and crash traces even when "
            "nothing is intentionally stored.\n\n"
            "The underlying capability (`POST /audit/db-table`) still exists in the "
            "API and works the same as CSV auditing — it's just not exposed as an "
            "open credential-entry form on a publicly hosted demo. To try it, run "
            "the API locally and set the `ENABLE_DB_AUDIT_UI=true` environment "
            "variable before starting the dashboard, or call the endpoint directly "
            "against a database you control."
        )
    else:
        st.caption("Connects to an external database using the connection string you provide — nothing is stored beyond the audit results.")
        connection_string = st.text_input(
            "SQLAlchemy connection string",
            placeholder="postgresql://user:password@host:5432/dbname",
        )
        table_name = st.text_input("Table name", placeholder="e.g. orders")
        db_key_columns_input = st.text_input(
            "Key column(s) for duplicate detection (comma-separated, optional)",
            placeholder="e.g. order_id",
            key="db_key_columns",
        )

        if st.button("Run audit", type="primary", key="db_audit_button",
                     disabled=not (connection_string and table_name)):
            with st.spinner("Connecting and running audit..."):
                result = api_post_db_table(connection_string, table_name, db_key_columns_input or None)
            if result:
                st.session_state.last_result = result

        if st.session_state.last_result:
            st.divider()
            render_audit_result(st.session_state.last_result)

with tab_sources:
    st.subheader("Audited sources")
    sources = api_get("/sources")
    if sources:
        sources_df = pd.DataFrame(sources)
        st.dataframe(sources_df, use_container_width=True, hide_index=True)
    else:
        st.info("No sources audited yet. Upload a CSV or connect a DB table to get started.")

with tab_trends:
    st.subheader("Quality trend by source")
    sources = api_get("/sources")
    if not sources:
        st.info("No sources audited yet. Run an audit first to see trends.")
    else:
        source_options = {f"{s['name']} (id={s['id']})": s["id"] for s in sources}
        selected_label = st.selectbox("Choose a source", list(source_options.keys()))
        if selected_label:
            render_trend(source_options[selected_label])
