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
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

API_BASE_URL = st.secrets.get(
    "DATASENTRY_API_URL",
    "http://127.0.0.1:8000"
)
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

    /* Colorful chart/accent palette — used for KPI accents and Plotly charts */
    --chart-1: #4F46E5;  /* indigo   */
    --chart-2: #0EA5E9;  /* sky      */
    --chart-3: #F59E0B;  /* amber    */
    --chart-4: #EC4899;  /* pink     */
    --chart-5: #14B8A6;  /* teal     */
    --chart-6: #EF4444;  /* red      */
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

/* ---- Metrics — heavier cards with a colorful top accent per position ---- */
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.1rem;
    box-shadow: var(--shadow-md);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--chart-1);
}
div[data-testid="column"]:nth-of-type(4n+1) [data-testid="stMetric"]::before { background: var(--chart-1); }
div[data-testid="column"]:nth-of-type(4n+2) [data-testid="stMetric"]::before { background: var(--chart-2); }
div[data-testid="column"]:nth-of-type(4n+3) [data-testid="stMetric"]::before { background: var(--chart-3); }
div[data-testid="column"]:nth-of-type(4n+4) [data-testid="stMetric"]::before { background: var(--chart-4); }
[data-testid="stMetric"]:hover { box-shadow: var(--shadow-lg); transform: translateY(-2px); }
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
    font-weight: 800;
    font-size: 1.5rem !important;
}

/* ---- Section panel — for grouping charts/tables into a card-like block ---- */
.ds-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.3rem 1.4rem;
    box-shadow: var(--shadow-md);
    margin-bottom: 1rem;
}
.ds-panel-title {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    color: var(--text);
    margin-bottom: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.ds-panel-title .ds-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
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

/* ---- Real bordered containers (st.container(border=True)) — used as panel
   cards so a chart's title and its chart actually share one card, instead
   of a styled title floating above an unstyled chart. ---- */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    box-shadow: var(--shadow-md) !important;
    padding: 0.4rem 0.2rem !important;
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

/* ---- Circular health gauge — clean, single fill animation on load.
   No border/shadow of its own — it now lives inside a real
   st.container(border=True), so its own card styling would double up. ---- */
.ds-gauge-wrap {
    display: flex;
    align-items: center;
    gap: 1.4rem;
    padding: 0.6rem 0.4rem;
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
        resp = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=45)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        st.warning(
            "The API took too long to respond. On the free tier it spins down after "
            "inactivity, and the first request can take 30–50 seconds to wake it up. "
            "Please wait a moment and try again."
        )
        return None
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
        resp = requests.post(f"{API_BASE_URL}/audit/upload", files=files, params=params, timeout=90)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        st.warning(
            "The API took too long to respond. On the free tier it spins down after "
            "inactivity, and the first request can take 30–50 seconds to wake it up. "
            "Please wait a moment and try again."
        )
        return None
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
        resp = requests.post(f"{API_BASE_URL}/audit/db-table", json=body, timeout=90)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        st.warning(
            "The API took too long to respond. On the free tier it spins down after "
            "inactivity, and the first request can take 30–50 seconds to wake it up. "
            "Please wait a moment and try again."
        )
        return None
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
    <div class="ds-gauge-wrap">
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


CHART_PALETTE = ["#4F46E5", "#0EA5E9", "#F59E0B", "#EC4899", "#14B8A6", "#EF4444", "#8B5CF6", "#22C55E"]


def _plotly_layout_defaults(fig: go.Figure, height: int = 300) -> go.Figure:
    # Explicit white backgrounds (not transparent) and an explicit light
    # template — this makes charts render correctly regardless of whether
    # Streamlit's own theme resolves to light or dark. Transparent
    # backgrounds were the root cause of the washed-out "ghosting" look:
    # they let a dark background bleed through behind light chart text.
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, sans-serif", color="#101828", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, x=0.5, xanchor="center", font=dict(color="#101828")),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, color="#101828", tickfont=dict(color="#101828"))
    fig.update_yaxes(showgrid=True, gridcolor="#E4E7EC", zeroline=False, color="#101828", tickfont=dict(color="#101828"))
    return fig


def render_audit_result(result: dict) -> None:
    st.subheader("Audit result")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{result['row_count']:,}")
    c2.metric("Columns", result["column_count"])
    c3.metric("Severity-weighted cost", f"${result['total_cost']:,.2f}")
    c4.metric("Audit run ID", result["id"])
    st.caption(
        "The cost figure is a configurable heuristic (issue count × your own per-issue weights), "
        "not a validated financial estimate. Adjust it in `config/cost_config.yaml`."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    gauge_col, note_col = st.columns([1, 2])
    with gauge_col:
        with st.container(border=True):
            render_score_gauge(result["health_score"])
    with note_col:
        with st.container(border=True):
            st.markdown(
                '<div class="ds-panel-title"><span class="ds-dot" style="background: var(--primary);"></span>What this score means</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                "85+ is healthy, 60–84 needs attention, below 60 is critical. The score weighs "
                "nulls, duplicates, format issues, outliers, and rule violations equally by "
                "default — adjust the weighting in `engine/scoring.py` if one dimension "
                "matters more for your data."
            )

    st.divider()
    render_issue_drilldown(result["id"])


def render_issue_drilldown(audit_run_id: int) -> None:
    detail = api_get(f"/audit-runs/{audit_run_id}")
    if not detail:
        st.warning("Could not load issue detail for this audit run.")
        return

    st.subheader(f"Issues found ({len(detail['issues'])})")

    if detail["issues"]:
        issues_df = pd.DataFrame(detail["issues"])
        issue_counts = issues_df["issue_type"].value_counts().reset_index()
        issue_counts.columns = ["issue_type", "count"]

        col_chart, col_table = st.columns([1, 1.4])
        with col_chart:
            with st.container(border=True):
                st.markdown(
                    '<div class="ds-panel-title"><span class="ds-dot" style="background: var(--chart-4);"></span>Issue breakdown</div>',
                    unsafe_allow_html=True,
                )
                fig = px.pie(
                    issue_counts, names="issue_type", values="count",
                    hole=0.55, color_discrete_sequence=CHART_PALETTE,
                )
                fig.update_traces(
                    textposition="outside", textinfo="label+percent",
                    marker=dict(line=dict(color="#FFFFFF", width=2)),
                    hovertemplate="<b>%{label}</b><br>%{value} issues (%{percent})<extra></extra>",
                )
                st.plotly_chart(_plotly_layout_defaults(fig, height=290), use_container_width=True, config={"displayModeBar": False}, key=f"issue_breakdown_{audit_run_id}")
        with col_table:
            with st.container(border=True):
                st.markdown(
                    '<div class="ds-panel-title"><span class="ds-dot" style="background: var(--chart-1);"></span>Issue detail</div>',
                    unsafe_allow_html=True,
                )
                st.dataframe(issues_df, use_container_width=True, hide_index=True, height=250)
    else:
        st.success("No issues found — this dataset is clean.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Column profile")
    if detail["column_stats"]:
        stats_df = pd.DataFrame(detail["column_stats"])
        col_chart2, col_table2 = st.columns([1, 1.4])
        with col_chart2:
            with st.container(border=True):
                st.markdown(
                    '<div class="ds-panel-title"><span class="ds-dot" style="background: var(--chart-2);"></span>Null % by column</div>',
                    unsafe_allow_html=True,
                )
                sorted_stats = stats_df.sort_values("null_pct", ascending=True)
                fig2 = px.bar(
                    sorted_stats, x="null_pct", y="column_name",
                    orientation="h", color="null_pct", color_continuous_scale=["#0EA5E9", "#EF4444"],
                    labels={"null_pct": "% null", "column_name": ""},
                )
                fig2.update_traces(
                    marker=dict(line=dict(color="#FFFFFF", width=0.5)),
                    hovertemplate="<b>%{y}</b><br>%{x}% null<extra></extra>",
                )
                fig2.update_layout(coloraxis_showscale=False, bargap=0.35)
                st.plotly_chart(_plotly_layout_defaults(fig2, height=290), use_container_width=True, config={"displayModeBar": False}, key=f"null_profile_{audit_run_id}")
        with col_table2:
            with st.container(border=True):
                st.markdown(
                    '<div class="ds-panel-title"><span class="ds-dot" style="background: var(--chart-5);"></span>Column stats</div>',
                    unsafe_allow_html=True,
                )
                st.dataframe(stats_df, use_container_width=True, hide_index=True, height=250)
    else:
        st.write("No column statistics available.")


def render_trend(source_id: int) -> None:
    history = api_get(f"/trends/{source_id}")
    if not history:
        st.info("No audit history yet for this source. Run an audit to start tracking trends.")
        return

    df = pd.DataFrame(history)
    df["run_at"] = pd.to_datetime(df["run_at"])
    df = df.sort_values("run_at")

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown(
                '<div class="ds-panel-title"><span class="ds-dot" style="background: var(--chart-1);"></span>Health score over time</div>',
                unsafe_allow_html=True,
            )
            fig_score = go.Figure()
            fig_score.add_trace(go.Scatter(
                x=df["run_at"], y=df["health_score"], mode="lines+markers",
                line=dict(color="#4F46E5", width=3, shape="spline"),
                marker=dict(size=8, color="#4F46E5", line=dict(color="#FFFFFF", width=1.5)),
                fill="tozeroy", fillcolor="rgba(79, 70, 229, 0.10)",
                hovertemplate="<b>%{x|%b %d, %H:%M}</b><br>Score: %{y:.1f}<extra></extra>",
            ))
            fig_score.update_yaxes(range=[0, 105])
            st.plotly_chart(_plotly_layout_defaults(fig_score, height=270), use_container_width=True, config={"displayModeBar": False}, key=f"trend_score_{source_id}")
    with col_b:
        with st.container(border=True):
            st.markdown(
                '<div class="ds-panel-title"><span class="ds-dot" style="background: var(--chart-4);"></span>Severity-weighted cost over time</div>',
                unsafe_allow_html=True,
            )
            fig_cost = go.Figure()
            fig_cost.add_trace(go.Bar(
                x=df["run_at"], y=df["total_cost"],
                marker=dict(
                    color=df["total_cost"],
                    colorscale=[[0, "#14B8A6"], [0.5, "#F59E0B"], [1, "#EF4444"]],
                    line=dict(color="#FFFFFF", width=0.5),
                ),
                hovertemplate="<b>%{x|%b %d, %H:%M}</b><br>$%{y:,.2f}<extra></extra>",
            ))
            fig_cost.update_layout(bargap=0.3)
            st.plotly_chart(_plotly_layout_defaults(fig_cost, height=270), use_container_width=True, config={"displayModeBar": False}, key=f"trend_cost_{source_id}")

    st.markdown("<br>", unsafe_allow_html=True)
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

ENABLE_DB_AUDIT_UI = st.secrets.get(
    "ENABLE_DB_AUDIT_UI",
    "false"
).lower() == "true"
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