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

st.set_page_config(page_title="DataSentry", page_icon="🛡️", layout="wide")


# --------------------------------------------------------------------------
# Theme — clean, professional, light. One calm primary accent (indigo),
# muted status colors, a single consistent typeface, restrained motion:
# a smooth once-only entrance and subtle hover feedback, nothing looping
# or glowing. Built for a boardroom, not a demo reel.
# --------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg:           #F7F8FA;
    --surface:      #FFFFFF;
    --surface-2:    #F1F3F6;
    --border:       #E4E7EC;
    --text:         #101828;
    --text-muted:   #667085;
    --primary:      #4F46E5;
    --primary-dark: #4338CA;
    --primary-wash: rgba(79, 70, 229, 0.08);
    --success:      #16A34A;
    --success-wash: rgba(22, 163, 74, 0.09);
    --warning:      #D97706;
    --warning-wash: rgba(217, 119, 6, 0.10);
    --danger:       #DC2626;
    --danger-wash:  rgba(220, 38, 38, 0.09);
    --shadow-sm:    0 1px 2px rgba(16, 24, 40, 0.05);
    --shadow-md:    0 4px 10px rgba(16, 24, 40, 0.06), 0 1px 3px rgba(16, 24, 40, 0.05);
    --shadow-lg:    0 8px 20px rgba(16, 24, 40, 0.08);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'Inter', -apple-system, sans-serif;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { visibility: hidden; }
#MainMenu, footer { visibility: hidden; }

.block-container { padding-top: 2.2rem; max-width: 1080px; }

/* ---- Restrained entrance — settles once, visible by default ---- */
.ds-fade-in {
    opacity: 0.001;
    animation: ds-fade-up 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes ds-fade-up {
    from { opacity: 0.001; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ---- Header ---- */
.ds-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.1rem 1.5rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    box-shadow: var(--shadow-sm);
    margin-bottom: 0.4rem;
}
.ds-header-left { display: flex; align-items: center; gap: 0.7rem; }
.ds-header-mark {
    width: 38px; height: 38px;
    display: flex; align-items: center; justify-content: center;
    background: var(--primary-wash);
    border-radius: 9px;
    font-size: 1.15rem;
}
.ds-header-title {
    font-family: 'Inter', sans-serif;
    font-weight: 800;
    font-size: 1.2rem;
    color: var(--text);
    letter-spacing: -0.01em;
    margin: 0;
    line-height: 1.1;
}
.ds-caption {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    color: var(--text-muted);
    font-size: 0.82rem;
    margin: 0;
}
.ds-header-badge {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--primary);
    background: var(--primary-wash);
    padding: 4px 10px;
    border-radius: 20px;
}

/* ---- Tabs ---- */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--surface-2);
    border-radius: 10px;
    padding: 4px;
    gap: 2px;
    border: 1px solid var(--border);
}
[data-testid="stTabs"] button[role="tab"] {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--text-muted);
    background: transparent;
    border-radius: 7px !important;
    transition: color 0.15s ease;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: var(--primary) !important;
    background: var(--surface) !important;
    box-shadow: var(--shadow-sm);
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: transparent !important; }
[data-testid="stTabs"] [data-baseweb="tab-border"] { background-color: transparent !important; }
[data-testid="stTabs"] [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

/* ---- Inputs & uploader ---- */
[data-testid="stTextInput"] input, [data-testid="stFileUploaderDropzone"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px var(--primary-wash);
}
[data-testid="stFileUploaderDropzone"] { border-style: dashed !important; padding: 1.1rem !important; }

/* ---- Buttons ---- */
.stButton > button {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.88rem;
    background: var(--primary) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.15rem !important;
    box-shadow: var(--shadow-sm);
    transition: background 0.15s ease, transform 0.1s ease, box-shadow 0.15s ease;
}
.stButton > button:hover { background: var(--primary-dark) !important; box-shadow: var(--shadow-md); }
.stButton > button:active { transform: scale(0.98); }
.stButton > button:disabled {
    background: var(--surface-2) !important;
    color: var(--text-muted) !important;
    box-shadow: none;
}

/* ---- Metrics ---- */
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.9rem 1rem;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.15s ease, transform 0.15s ease;
}
[data-testid="stMetric"]:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif;
    color: var(--text-muted);
    font-weight: 600;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif;
    color: var(--text);
    font-weight: 700;
}

/* ---- Dataframes & alerts ---- */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}

[data-testid="stAlert"] {
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
}

hr { border-color: var(--border) !important; margin: 1.4rem 0 !important; }

/* ---- Selectbox / dropdown — previously unstyled, caused theme mismatch ---- */
[data-baseweb="select"] > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}
[data-baseweb="select"] * {
    color: var(--text) !important;
    background: transparent !important;
    font-family: 'Inter', sans-serif !important;
}
[data-baseweb="select"] svg { fill: var(--text-muted) !important; }
[data-baseweb="popover"], [data-baseweb="menu"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    box-shadow: var(--shadow-lg) !important;
}
[data-baseweb="menu"] li {
    color: var(--text) !important;
    background: var(--surface) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
}
[data-baseweb="menu"] li:hover {
    background: var(--primary-wash) !important;
    color: var(--primary) !important;
}

/* ---- Force consistent text contrast across every generic element ---- */
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] span,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] div {
    color: inherit;
}
[data-testid="stMarkdownContainer"] p { color: var(--text) !important; }
[data-testid="stCaptionContainer"], .stCaption, [data-testid="stCaptionContainer"] p {
    color: var(--text-muted) !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stAlert"] p, [data-testid="stAlert"] span, [data-testid="stAlert"] div {
    color: var(--text) !important;
}
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploader"] label {
    color: var(--text-muted) !important;
}
[data-testid="stFileUploader"] button {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 7px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
}
[data-testid="stFileUploader"] button:hover { border-color: var(--primary) !important; color: var(--primary) !important; }
[data-testid="stTextInput"] input::placeholder { color: var(--text-muted) !important; opacity: 0.7 !important; }
[data-testid="stSpinner"] p { color: var(--text-muted) !important; font-family: 'Inter', sans-serif !important; }
[data-testid="stTextInput"] label { color: var(--text) !important; font-family: 'Inter', sans-serif !important; font-weight: 500 !important; }
[data-testid="stDataFrame"] * { color: var(--text) !important; }
[data-testid="stExpander"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; }
[data-testid="stExpander"] summary { color: var(--text) !important; font-weight: 600 !important; }

h1, h2, h3 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    color: var(--text) !important;
}

/* ---- Circular health gauge — clean, single fill animation on load ---- */
.ds-gauge-wrap {
    display: flex;
    align-items: center;
    gap: 1.4rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.15rem 1.4rem;
    box-shadow: var(--shadow-sm);
}
.ds-gauge-svg circle.ds-gauge-track { fill: none; stroke: var(--surface-2); stroke-width: 8; }
.ds-gauge-svg circle.ds-gauge-fill {
    fill: none;
    stroke-width: 8;
    stroke-linecap: round;
    transform: rotate(-90deg);
    transform-origin: 50% 50%;
    transition: stroke-dashoffset 1s cubic-bezier(0.16, 1, 0.3, 1);
}
.ds-gauge-value {
    font-family: 'Inter', sans-serif;
    font-size: 1.35rem;
    font-weight: 800;
    fill: var(--text);
}
.ds-gauge-status {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
}
.ds-gauge-sub {
    font-family: 'Inter', sans-serif;
    color: var(--text-muted);
    font-weight: 500;
    font-size: 0.8rem;
    margin-top: 2px;
}

@media (prefers-reduced-motion: reduce) {
    .ds-fade-in { animation: none !important; opacity: 1 !important; }
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
        signal, label = "var(--success)", "Healthy"
    elif score >= 60:
        signal, label = "var(--warning)", "Needs attention"
    else:
        signal, label = "var(--danger)", "Critical"

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
        <div class="ds-header-left">
            <div class="ds-header-mark">🛡️</div>
            <div>
                <p class="ds-header-title">DataSentry</p>
                <p class="ds-caption">Data quality auditing — upload a CSV or connect a live table.</p>
            </div>
        </div>
        <span class="ds-header-badge">Audit engine</span>
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