"""
AgroSense AI - Usage Analytics & Telemetry View
Visualizes RAG query trends, response latency distribution, source citation frequency,
and soil test history with interactive Plotly charts.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
from src.database.db import get_db_connection, get_analytics_summary
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

    st.markdown("<hr style='border:1px solid #E8F5E9; margin:1rem 0'>", unsafe_allow_html=True)

    if analytics_df.empty:
        st.info(
            "📈 **No analytics data yet.** Start asking questions in the **AI Assistant** tab to generate telemetry. "
            "Charts will automatically populate as you use the system."
        )
        _render_placeholder_charts()
        return

    # ── Tab Layout ───────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📈 Query Trends", "⚡ Latency Analysis", "🗂️ Soil Diagnostics"])

    with tab1:
        _render_query_trends(analytics_df)

    with tab2:
        _render_latency_analysis(analytics_df)

    with tab3:
        _render_soil_analytics(soil_df)


def _render_query_trends(df: pd.DataFrame):
    """Renders query volume over time and provider distribution charts."""
    render_section_header("Query Volume Over Time", "📈")

    col_l, col_r = st.columns([2, 1])

    with col_l:
        if "date" in df.columns and not df["date"].empty:
            daily_counts = df.groupby("date").size().reset_index(name="queries")
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=daily_counts["date"],
                y=daily_counts["queries"],
                mode="lines+markers",
                name="Daily Queries",
                line=dict(color="#2E7D32", width=2.5, shape="spline"),
                marker=dict(size=7, color="#43A047", symbol="circle"),
                fill="tozeroy",
                fillcolor="rgba(46,125,50,0.08)"
            ))
            fig_line.update_layout(
                title="Daily Query Volume",
                xaxis_title="Date",
                yaxis_title="Queries",
                plot_bgcolor="#FAFAFA",
                paper_bgcolor="#ffffff",
                font=dict(family="Inter, sans-serif", size=12),
                title_font=dict(size=14, color="#1B5E20"),
                margin=dict(l=10, r=10, t=40, b=10),
                height=300,
                showlegend=False,
            )
            fig_line.update_xaxes(showgrid=True, gridcolor="#F1F8E9")
            fig_line.update_yaxes(showgrid=True, gridcolor="#F1F8E9")
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Not enough data to plot query trends yet.")

    with col_r:
        if "provider" in df.columns and not df["provider"].empty:
            provider_counts = df["provider"].value_counts().reset_index()
            provider_counts.columns = ["Provider", "Count"]
            fig_pie = px.pie(
                provider_counts,
                names="Provider",
                values="Count",
                title="LLM Provider Distribution",
                color_discrete_sequence=["#2E7D32", "#66BB6A", "#A5D6A7", "#FF8F00", "#1565C0"]
            )
            fig_pie.update_layout(
                font=dict(family="Inter, sans-serif", size=11),
                title_font=dict(size=13, color="#1B5E20"),
                margin=dict(l=5, r=5, t=40, b=5),
                height=300,
                legend=dict(orientation="v", font=dict(size=10))
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
            title="Number of Sources Retrieved per Query",
            color="Frequency",
            color_continuous_scale=["#C8E6C9", "#2E7D32"],
        )
        fig_bar.update_layout(
            plot_bgcolor="#FAFAFA",
            paper_bgcolor="#ffffff",
            font=dict(family="Inter, sans-serif", size=12),
            title_font=dict(size=13, color="#1B5E20"),
            margin=dict(l=10, r=10, t=40, b=10),
            height=250,
            coloraxis_showscale=False
        )
        fig_bar.update_xaxes(showgrid=False, type="category")
        fig_bar.update_yaxes(showgrid=True, gridcolor="#F1F8E9")
        st.plotly_chart(fig_bar, use_container_width=True)

    # Recent queries table
    render_section_header("Recent Query Log", "🗒️")
    display_df = df[["timestamp", "query_text", "provider", "latency_ms", "sources_count"]].tail(15).copy()
    display_df.columns = ["Timestamp", "Query", "Provider", "Latency (ms)", "Sources"]
    display_df["Timestamp"] = display_df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    display_df = display_df.iloc[::-1].reset_index(drop=True)
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def _render_latency_analysis(df: pd.DataFrame):
    """Renders latency histogram and box plot."""
    render_section_header("Response Latency Distribution", "⚡")

    if "latency_ms" not in df.columns or df["latency_ms"].empty:
        st.info("No latency data available yet.")
        return

    col_l, col_r = st.columns(2)

    with col_l:
        fig_hist = px.histogram(
            df,
            x="latency_ms",
            nbins=20,
            title="Latency Frequency Distribution",
            labels={"latency_ms": "Response Latency (ms)"},
            color_discrete_sequence=["#43A047"]
        )
        fig_hist.update_layout(
            plot_bgcolor="#FAFAFA",
            paper_bgcolor="#ffffff",
            font=dict(family="Inter, sans-serif", size=12),
            title_font=dict(size=13, color="#1B5E20"),
            margin=dict(l=10, r=10, t=40, b=10),
            height=300,
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
            title="Latency by Provider",
            labels={"latency_ms": "Latency (ms)", "provider": "Provider"},
            color="provider",
            color_discrete_sequence=["#2E7D32", "#66BB6A", "#A5D6A7", "#FF8F00", "#1565C0"]
        )
        fig_box.update_layout(
            plot_bgcolor="#FAFAFA",
            paper_bgcolor="#ffffff",
            font=dict(family="Inter, sans-serif", size=12),
            title_font=dict(size=13, color="#1B5E20"),
            margin=dict(l=10, r=10, t=40, b=10),
            height=300,
            showlegend=False
        )
        fig_box.update_xaxes(showgrid=False)
        fig_box.update_yaxes(showgrid=True, gridcolor="#F1F8E9")
        st.plotly_chart(fig_box, use_container_width=True)

    # Latency summary stats
    lat = df["latency_ms"]
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Min Latency", f"{lat.min():.0f} ms")
    s2.metric("Avg Latency", f"{lat.mean():.0f} ms")
    s3.metric("Median Latency", f"{lat.median():.0f} ms")
    s4.metric("Max Latency", f"{lat.max():.0f} ms")


def _render_soil_analytics(df: pd.DataFrame):
    """Renders soil health analytics charts."""
    render_section_header("Soil Health Diagnostics Overview", "🌱")

    if df.empty:
        st.info("No soil test records found. Run a Soil Health Card evaluation to see charts here.")
        return

    col_l, col_r = st.columns(2)

    with col_l:
        # Crop distribution
        crop_counts = df["target_crop"].value_counts().reset_index()
        crop_counts.columns = ["Crop", "Tests"]
        fig_crop = px.bar(
            crop_counts,
            x="Crop",
            y="Tests",
            title="Soil Tests by Target Crop",
            color="Tests",
            color_continuous_scale=["#C8E6C9", "#1B5E20"]
        )
        fig_crop.update_layout(
            plot_bgcolor="#FAFAFA",
            paper_bgcolor="#ffffff",
            font=dict(family="Inter, sans-serif", size=11),
            title_font=dict(size=13, color="#1B5E20"),
            margin=dict(l=10, r=10, t=40, b=10),
            height=280,
            coloraxis_showscale=False,
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig_crop, use_container_width=True)

    with col_r:
        # pH distribution scatter
        fig_ph = px.scatter(
            df,
            x=df.index,
            y="ph",
            color="target_crop",
            title="Soil pH Trend Across Tests",
            labels={"x": "Test #", "ph": "Soil pH"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_ph.add_hline(y=6.5, line_dash="dash", line_color="#2E7D32", annotation_text="Min Optimal")
        fig_ph.add_hline(y=7.8, line_dash="dash", line_color="#E65100", annotation_text="Max Optimal")
        fig_ph.update_layout(
            plot_bgcolor="#FAFAFA",
            paper_bgcolor="#ffffff",
            font=dict(family="Inter, sans-serif", size=11),
            title_font=dict(size=13, color="#1B5E20"),
            margin=dict(l=10, r=10, t=40, b=10),
            height=280,
            legend=dict(font=dict(size=9))
        )
        st.plotly_chart(fig_ph, use_container_width=True)

    # NPK radar - latest test
    render_section_header("Nutrient Profile — Latest Soil Test", "🔬")
    latest = df.iloc[-1]
    n_pct = min(100, (latest["n"] / 560) * 100)
    p_pct = min(100, (latest["p"] / 56) * 100)
    k_pct = min(100, (latest["k"] / 336) * 100)

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[n_pct, p_pct, k_pct, n_pct],
        theta=["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)", "Nitrogen (N)"],
        fill="toself",
        fillcolor="rgba(46,125,50,0.15)",
        line=dict(color="#2E7D32", width=2),
        name=f"Test (Crop: {latest['target_crop']})"
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[100, 100, 100, 100],
        theta=["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)", "Nitrogen (N)"],
        fill="toself",
        fillcolor="rgba(0,0,0,0.03)",
        line=dict(color="#CFD8DC", width=1, dash="dot"),
        name="Maximum Range"
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10)),
            angularaxis=dict(tickfont=dict(size=11, color="#37474F"))
        ),
        font=dict(family="Inter, sans-serif"),
        title=dict(text="NPK Availability (% of Optimal Range)", font=dict(size=13, color="#1B5E20")),
        margin=dict(l=20, r=20, t=50, b=20),
        height=320,
        showlegend=True,
        legend=dict(font=dict(size=10))
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Full table
    render_section_header("Complete Soil Test History", "📋")
    display = df[["timestamp", "farmer_name", "target_crop", "ph", "ec", "oc", "n", "p", "k", "status_summary"]].copy()
    display.columns = ["Date", "Farmer", "Crop", "pH", "EC", "OC%", "N", "P", "K", "Evaluation"]
    display["Date"] = display["Date"].dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(display.iloc[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)


def _render_placeholder_charts():
    """Renders sample placeholder charts when no data exists yet."""
    st.markdown("#### 📊 Preview: What Analytics Will Look Like")
    col1, col2 = st.columns(2)

    with col1:
        import numpy as np
        dates = pd.date_range("2026-11-01", periods=18, freq="D")
        vals = np.random.poisson(lam=5, size=18)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=vals,
            mode="lines+markers",
            line=dict(color="#A5D6A7", width=2, dash="dot"),
            fill="tozeroy", fillcolor="rgba(165,214,167,0.2)"
        ))
        fig.update_layout(
            title="Sample: Query Volume (Demo)",
            plot_bgcolor="#FAFAFA", paper_bgcolor="#ffffff",
            font=dict(family="Inter, sans-serif", size=11),
            title_font=dict(size=13, color="#78909C"),
            margin=dict(l=10, r=10, t=40, b=10), height=240,
            annotations=[dict(text="Demo — Start using AI Assistant to populate", showarrow=False,
                              xref="paper", yref="paper", x=0.5, y=0.5,
                              font=dict(size=12, color="#B0BEC5"))]
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.pie(
            values=[1], names=["Waiting for data..."],
            color_discrete_sequence=["#ECEFF1"],
            title="Sample: Provider Distribution (Demo)"
        )
        fig2.update_layout(
            font=dict(family="Inter, sans-serif", size=11),
            title_font=dict(size=13, color="#78909C"),
            margin=dict(l=5, r=5, t=40, b=5), height=240
        )
        st.plotly_chart(fig2, use_container_width=True)
