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
    if score >= 85:
        color, label = "🟢", "Healthy"
    elif score >= 60:
        color, label = "🟡", "Needs attention"
    else:
        color, label = "🔴", "Poor"

    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Health score", f"{score:.1f}/100")
    with col2:
        st.write(f"{color} **{label}**")
        st.progress(min(max(score / 100, 0.0), 1.0))


def render_audit_result(result: dict) -> None:
    st.subheader("Audit result")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", result["row_count"])
    c2.metric("Columns", result["column_count"])
    c3.metric("Estimated cost", f"${result['total_cost']:,.2f}")
    c4.metric("Audit run ID", result["id"])

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

    st.subheader("Estimated cost over time")
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

st.title("🛡️ DataSentry")
st.caption("Data quality auditing — upload a CSV or connect to a live database table.")

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
