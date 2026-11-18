"""
AgroSense AI - Usage Analytics & Telemetry View
Visualizes RAG query trends, response latency distribution, source citation frequency,
and soil test history with interactive Plotly charts and 1-click telemetry simulation.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import random
from datetime import datetime, timedelta
from src.database.db import get_db_connection, get_analytics_summary, log_analytics
from src.ui.components import render_metric, render_section_header


def _fetch_analytics_df() -> pd.DataFrame:
    """Fetches all analytics events from SQLite."""
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(
                "SELECT timestamp, query_text, provider, latency_ms, sources_count FROM analytics_events ORDER BY id ASC",
                conn
            )
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["date"] = df["timestamp"].dt.date
        return df
    except Exception:
        return pd.DataFrame()


def _fetch_soil_df() -> pd.DataFrame:
    """Fetches soil test records from SQLite."""
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(
                "SELECT timestamp, farmer_name, target_crop, ph, ec, oc, n, p, k, status_summary FROM soil_records ORDER BY id ASC",
                conn
            )
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    except Exception:
        return pd.DataFrame()


def _seed_demo_analytics():
    """Seeds realistic agricultural telemetry events for testing and demonstration."""
    sample_queries = [
        ("How to control Yellow Stem Borer in rice?", "AgroSense Offline RAG Engine", 45.2, 4),
        ("What is the critical irrigation stage for wheat?", "AgroSense Offline RAG Engine", 52.8, 4),
        ("How to reclaim sodic soil using agricultural gypsum?", "AgroSense Offline RAG Engine", 38.1, 3),
        ("Early Blight symptoms and fungicide dosage for tomato?", "Google Gemini 1.5 Flash", 420.5, 4),
        ("What are the symptoms of Fall Armyworm in maize?", "AgroSense Offline RAG Engine", 49.3, 4),
        ("Best sowing window for Bt Cotton in black soil?", "Google Gemini 1.5 Flash", 385.0, 3),
        ("How much urea per acre for Rabi wheat at CRI stage?", "AgroSense Offline RAG Engine", 41.6, 4),
        ("Brown Plant Hopper hopperburn biological control in paddy", "AgroSense Offline RAG Engine", 55.4, 4),
        ("Zinc deficiency treatment in alluvial loam soil", "Google Gemini 1.5 Flash", 410.2, 3),
        ("Whitefly chemical vs neem spray rotation in cotton", "AgroSense Offline RAG Engine", 47.9, 4),
    ]
    for q, p, lat, src in sample_queries:
        log_analytics(q, p, lat + random.uniform(-10, 15), src)


def render_analytics_view():
    """Renders the usage analytics and telemetry dashboard."""
    st.subheader("📊 Usage Analytics & System Telemetry")
    st.caption("Real-time insights into AI query patterns, response latency, source citation distribution, and soil diagnostics history.")

    summary = get_analytics_summary()
    analytics_df = _fetch_analytics_df()
    soil_df = _fetch_soil_df()

    # ── KPI Metrics Row ──────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric("Total AI Queries", summary["total_queries"], "Processed via RAG pipeline", "💬")
    with col2:
        render_metric("Avg Response Time", f"{summary['avg_latency_ms']:.0f} ms", "End-to-end pipeline latency", "⚡")
    with col3:
        render_metric("Soil Tests Run", summary["total_soil_tests"], "ICAR-benchmarked evaluations", "🧪")
    with col4:
        render_metric("Chat Messages", summary["total_messages"], "Total conversation turns", "📝")

    st.markdown("<hr style='border:1px solid #E8F5E9; margin:0.85rem 0'>", unsafe_allow_html=True)

    # If database has no queries, offer 1-click simulation button
    if analytics_df.empty:
        st.info("📈 **Telemetry is currently empty.** Click the button below to seed demo analytics data, or ask questions in the **AI Assistant** tab.")
        if st.button("🚀 Populate Demo Telemetry Data (1-Click)", type="primary"):
            _seed_demo_analytics()
            st.success("Generated realistic agronomic queries and telemetry!")
            st.rerun()

    # ── Tab Layout ───────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📈 Query Trends & Providers", "⚡ Latency Analysis", "🌱 Soil Diagnostics Overview"])

    with tab1:
        if not analytics_df.empty:
            _render_query_trends(analytics_df)
        else:
            st.caption("No queries to display yet.")

    with tab2:
        if not analytics_df.empty:
            _render_latency_analysis(analytics_df)
        else:
            st.caption("No latency telemetry to display yet.")

    with tab3:
        _render_soil_analytics(soil_df)


def _render_query_trends(df: pd.DataFrame):
    """Renders query volume over time and provider distribution charts."""
    render_section_header("Query Volume & Engine Distribution", "📈")

    col_l, col_r = st.columns([2, 1])

    with col_l:
        if "date" in df.columns and not df["date"].empty:
            daily_counts = df.groupby("date").size().reset_index(name="queries")
            fig_line = go.Figure()
            fig_line.add_trace(go.Bar(
                x=daily_counts["date"],
                y=daily_counts["queries"],
                name="Daily Queries",
                marker_color="#2E7D32",
                marker_line_color="#1B5E20",
                marker_line_width=1,
            ))
            fig_line.update_layout(
                title="Daily Query Frequency",
                xaxis_title="Date",
                yaxis_title="Queries",
                plot_bgcolor="#FAFAFA",
                paper_bgcolor="#ffffff",
                font=dict(family="Plus Jakarta Sans, sans-serif", size=11),
                title_font=dict(size=13, color="#1B5E20"),
                margin=dict(l=10, r=10, t=35, b=10),
                height=280,
                showlegend=False,
            )
            fig_line.update_xaxes(showgrid=False)
            fig_line.update_yaxes(showgrid=True, gridcolor="#F1F8E9")
            st.plotly_chart(fig_line, use_container_width=True)

    with col_r:
        if "provider" in df.columns and not df["provider"].empty:
            provider_counts = df["provider"].value_counts().reset_index()
            provider_counts.columns = ["Provider", "Count"]
            fig_pie = px.pie(
                provider_counts,
                names="Provider",
                values="Count",
                title="Engine Distribution",
                color_discrete_sequence=["#2E7D32", "#66BB6A", "#A5D6A7", "#FF8F00", "#1565C0"]
            )
            fig_pie.update_layout(
                font=dict(family="Plus Jakarta Sans, sans-serif", size=11),
                title_font=dict(size=13, color="#1B5E20"),
                margin=dict(l=5, r=5, t=35, b=5),
                height=280,
                legend=dict(orientation="v", font=dict(size=9))
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True)

    # Source citation frequency
    render_section_header("Source Citation Distribution", "📚")
    if "sources_count" in df.columns:
        src_dist = df["sources_count"].value_counts().sort_index().reset_index()
        src_dist.columns = ["Sources Cited", "Frequency"]
        fig_bar = px.bar(
            src_dist,
            x="Sources Cited",
            y="Frequency",
            title="Number of Verified Documents Cited per Query",
            color="Frequency",
            color_continuous_scale=["#C8E6C9", "#2E7D32"],
        )
        fig_bar.update_layout(
            plot_bgcolor="#FAFAFA",
            paper_bgcolor="#ffffff",
            font=dict(family="Plus Jakarta Sans, sans-serif", size=11),
            title_font=dict(size=13, color="#1B5E20"),
            margin=dict(l=10, r=10, t=35, b=10),
            height=240,
            coloraxis_showscale=False
        )
        fig_bar.update_xaxes(showgrid=False, type="category")
        fig_bar.update_yaxes(showgrid=True, gridcolor="#F1F8E9")
        st.plotly_chart(fig_bar, use_container_width=True)

    # Recent queries table
    render_section_header("Recent Query Log (Last 15 Inquiries)", "🗒️")
    display_df = df[["timestamp", "query_text", "provider", "latency_ms", "sources_count"]].tail(15).copy()
    display_df.columns = ["Timestamp", "Query", "Engine", "Latency (ms)", "Sources"]
    display_df["Timestamp"] = display_df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    display_df = display_df.iloc[::-1].reset_index(drop=True)
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def _render_latency_analysis(df: pd.DataFrame):
    """Renders latency histogram and box plot."""
    render_section_header("Pipeline Response Latency Breakdown", "⚡")

    col_l, col_r = st.columns(2)

    with col_l:
        fig_hist = px.histogram(
            df,
            x="latency_ms",
            nbins=15,
            title="Latency Frequency Histogram",
            labels={"latency_ms": "Response Time (ms)"},
            color_discrete_sequence=["#43A047"]
        )
        fig_hist.update_layout(
            plot_bgcolor="#FAFAFA",
            paper_bgcolor="#ffffff",
            font=dict(family="Plus Jakarta Sans, sans-serif", size=11),
            title_font=dict(size=13, color="#1B5E20"),
            margin=dict(l=10, r=10, t=35, b=10),
            height=280,
            showlegend=False
        )
        fig_hist.update_xaxes(showgrid=True, gridcolor="#F1F8E9")
        fig_hist.update_yaxes(showgrid=True, gridcolor="#F1F8E9")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_r:
        fig_box = px.box(
            df,
            y="latency_ms",
            x="provider",
            title="Latency by AI Engine",
            labels={"latency_ms": "Latency (ms)", "provider": "Provider"},
            color="provider",
            color_discrete_sequence=["#2E7D32", "#66BB6A", "#A5D6A7", "#FF8F00", "#1565C0"]
        )
        fig_box.update_layout(
            plot_bgcolor="#FAFAFA",
            paper_bgcolor="#ffffff",
            font=dict(family="Plus Jakarta Sans, sans-serif", size=11),
            title_font=dict(size=13, color="#1B5E20"),
            margin=dict(l=10, r=10, t=35, b=10),
            height=280,
            showlegend=False
        )
        fig_box.update_xaxes(showgrid=False)
        fig_box.update_yaxes(showgrid=True, gridcolor="#F1F8E9")
        st.plotly_chart(fig_box, use_container_width=True)

    lat = df["latency_ms"]
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Fastest Query", f"{lat.min():.0f} ms")
    s2.metric("Mean Latency", f"{lat.mean():.0f} ms")
    s3.metric("Median Latency", f"{lat.median():.0f} ms")
    s4.metric("Longest Query", f"{lat.max():.0f} ms")


def _render_soil_analytics(df: pd.DataFrame):
    """Renders soil health analytics charts."""
    render_section_header("Soil Health Diagnostic Overview", "🌱")

    if df.empty:
        st.info("No soil test records found. Run a Soil Health Card evaluation in the **Soil Health Card** tab to populate charts here.")
        return

    col_l, col_r = st.columns(2)

    with col_l:
        crop_counts = df["target_crop"].value_counts().reset_index()
        crop_counts.columns = ["Crop", "Tests"]
        fig_crop = px.bar(
            crop_counts,
            x="Crop",
            y="Tests",
            title="Tests by Target Crop",
            color="Tests",
            color_continuous_scale=["#C8E6C9", "#1B5E20"]
        )
        fig_crop.update_layout(
            plot_bgcolor="#FAFAFA",
            paper_bgcolor="#ffffff",
            font=dict(family="Plus Jakarta Sans, sans-serif", size=11),
            title_font=dict(size=13, color="#1B5E20"),
            margin=dict(l=10, r=10, t=35, b=10),
            height=260,
            coloraxis_showscale=False,
            xaxis_tickangle=-25
        )
        st.plotly_chart(fig_crop, use_container_width=True)

    with col_r:
        fig_ph = px.scatter(
            df,
            x=df.index,
            y="ph",
            color="target_crop",
            title="Soil pH Distribution Across Tests",
            labels={"x": "Sample #", "ph": "Soil pH"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_ph.add_hline(y=6.5, line_dash="dash", line_color="#2E7D32", annotation_text="Min Optimal")
        fig_ph.add_hline(y=7.8, line_dash="dash", line_color="#E65100", annotation_text="Max Optimal")
        fig_ph.update_layout(
            plot_bgcolor="#FAFAFA",
            paper_bgcolor="#ffffff",
            font=dict(family="Plus Jakarta Sans, sans-serif", size=11),
            title_font=dict(size=13, color="#1B5E20"),
            margin=dict(l=10, r=10, t=35, b=10),
            height=260,
            legend=dict(font=dict(size=9))
        )
        st.plotly_chart(fig_ph, use_container_width=True)

    # Full table
    render_section_header("Complete Soil Test History", "📋")
    display = df[["timestamp", "farmer_name", "target_crop", "ph", "ec", "oc", "n", "p", "k", "status_summary"]].copy()
    display.columns = ["Date", "Farmer", "Crop", "pH", "EC", "OC%", "N", "P", "K", "Evaluation"]
    display["Date"] = display["Date"].dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(display.iloc[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)
