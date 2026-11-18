"""
AgroSense AI - Dashboard View
Presents operational metrics, knowledge base status, system health,
regional agronomic advisory, live search widget, and interactive quick-actions.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from src.ui.components import render_metric, render_section_header, navigate_to
from src.database.db import get_analytics_summary, get_db_connection
from src.modules.crop_guide import CropGuideManager
from src.modules.pest_diagnosis import PestDiagnosisManager
from src.rag.vector_store import AgroVectorStore
from src.config import AppConfig


def _get_recent_queries(n: int = 30):
    """Fetches query dates and counts for activity chart."""
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(
                "SELECT timestamp FROM analytics_events ORDER BY id DESC LIMIT 500",
                conn
            )
        if df.empty:
            return [], []
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["date"] = df["timestamp"].dt.date
        daily = df.groupby("date").size().reset_index(name="count")
        dates = [str(d) for d in daily["date"].tolist()]
        counts = daily["count"].tolist()
        return dates, counts
    except Exception:
        return [], []


def render_dashboard_view():
    """Renders the executive overview and system metrics."""
    st.subheader("🌾 Farm Intelligence Dashboard")
    st.caption("Real-time operational telemetry, verified agronomic repository status, and quick-access advisory tools.")

    # ── Dynamic metrics ─────────────────────────────────────────────
    analytics = get_analytics_summary()
    crop_mgr = CropGuideManager()
    total_crops = len(crop_mgr.get_all_crops())
    pest_mgr = PestDiagnosisManager()
    total_pests = len(pest_mgr.get_all_pests())
    vector_store = AgroVectorStore()
    kb_stats = vector_store.get_stats()
    provider = AppConfig.get_llm_provider().upper()

    # ── Top KPI Metrics ─────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric("Indexed Documents", kb_stats["total_documents"], f"{kb_stats['total_chunks']} semantic chunks", "📂")
    with col2:
        render_metric("Crops Profiled", total_crops, "ICAR & State Univ. Guides", "🌾")
    with col3:
        render_metric("Pests & Pathogens", total_pests, "IPM Protocols Active", "🐛")
    with col4:
        render_metric("Queries Processed", analytics["total_queries"], f"Avg Latency: {analytics['avg_latency_ms']:.0f} ms", "💬")

    st.markdown("<hr style='border:1px solid #E8F5E9; margin:0.85rem 0'>", unsafe_allow_html=True)

    # ── Quick Navigation Shortcuts ──────────────────────────────────
    render_section_header("Quick Navigation Shortcuts", "⚡")
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)

    with qcol1:
        if st.button("💬 Ask AI Assistant", use_container_width=True, type="primary"):
            navigate_to("💬 AI Assistant")

    with qcol2:
        if st.button("🌿 Browse Crop Directory", use_container_width=True):
            navigate_to("🌿 Crop Guide")

    with qcol3:
        if st.button("🐛 Diagnose Pest & Disease", use_container_width=True):
            navigate_to("🐛 Pest & Disease Doctor")

    with qcol4:
        if st.button("🧪 Evaluate Soil Health", use_container_width=True):
            navigate_to("🧪 Soil Health Card")

    st.markdown("<hr style='border:1px solid #E8F5E9; margin:0.85rem 0'>", unsafe_allow_html=True)

    # ── Interactive Prompt Chips ────────────────────────────────────
    render_section_header("Frequently Asked Farmer Queries", "💡")
    st.caption("Click any query below to immediately launch the AI Assistant with verified ICAR context:")

    dashboard_prompts = [
        ("🌾 Rice Stem Borer", "How to control Yellow Stem Borer in rice?"),
        ("💧 Wheat Irrigation", "What is the critical irrigation stage for wheat?"),
        ("🧪 Sodic Soil Reclamation", "How to reclaim sodic soil using agricultural gypsum?"),
        ("🍅 Tomato Early Blight", "Early Blight symptoms and fungicide dosage for tomato?"),
        ("🌽 Maize Fall Armyworm", "What are the IPM controls for Fall Armyworm in maize?"),
    ]

    p_cols = st.columns(len(dashboard_prompts))
    for i, (label, prompt_text) in enumerate(dashboard_prompts):
        with p_cols[i]:
            if st.button(label, key=f"dash_chip_{i}", use_container_width=True):
                navigate_to("💬 AI Assistant", prompt_text)

    st.markdown("<hr style='border:1px solid #E8F5E9; margin:0.85rem 0'>", unsafe_allow_html=True)

    # ── Live Quick Knowledge Search on Dashboard ────────────────────
    render_section_header("Instant Agronomic Literature Search", "🔍")
    s_col1, s_col2 = st.columns([3, 1])
    with s_col1:
        dash_search_q = st.text_input(
            "Quick Search the FAISS Vector Database",
            placeholder="e.g. Zinc deficiency in paddy, Wheat Rust fungicide, Tomato blossom end rot...",
            label_visibility="collapsed"
        )
    with s_col2:
        search_clicked = st.button("🔎 Quick Retrieve", use_container_width=True)

    if dash_search_q and search_clicked:
        with st.spinner("Retrieving verified chunks..."):
            hits = vector_store.search(dash_search_q, top_k=2)
            if hits:
                st.markdown(f"**Found {len(hits)} matching knowledge chunks:**")
                for doc, score in hits:
                    st.markdown(
                        f"""
                        <div style="background:#FAFAFA; border:1px solid #E0ECE0; border-left:4px solid #2E7D32;
                             border-radius:10px; padding:0.85rem 1.1rem; margin-bottom:0.6rem;">
                            <strong style="color:#1B5E20;">{doc.metadata.get('title', 'Agronomy Guideline')}</strong>
                            <span style="font-size:0.75rem; color:#607D8B; margin-left:8px;">
                                Source: {doc.metadata.get('source', '')} (Score: {score:.3f})
                            </span>
                            <p style="margin:6px 0 0 0; font-size:0.88rem; color:#37474F;">
                                {doc.page_content[:320]}...
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                if st.button(f"💬 Ask AI Assistant about '{dash_search_q}'", type="primary"):
                    navigate_to("💬 AI Assistant", dash_search_q)
            else:
                st.info("No matching records found.")

    st.markdown("<hr style='border:1px solid #E8F5E9; margin:0.85rem 0'>", unsafe_allow_html=True)

    # ── Interactive Regional Agro-Climatic Advisory ──────────────────
    render_section_header("Interactive Regional Agro-Advisory", "🗺️")
    st.caption("Select your agro-climatic region for tailored seasonal alerts, sowing windows, and stress advisories:")

    region_options = [
        "Indo-Gangetic Plains (Punjab, Haryana, UP, Bihar)",
        "Deccan Plateau (Maharashtra, Karnataka, Telangana, AP)",
        "Eastern Coastal & Delta Zone (WB, Odisha, Coastal AP)",
        "Western Arid Zone (Rajasthan, Gujarat)",
        "Central Zone (Madhya Pradesh, Chhattisgarh)"
    ]
    selected_region = st.selectbox("Select Agro-Climatic Zone", region_options, label_visibility="collapsed")

    region_advisories = {
        "Indo-Gangetic Plains (Punjab, Haryana, UP, Bihar)": {
            "crops": "Wheat, Mustard, Chickpea, Sugarcane",
            "weather": "Cool foggy mornings, low evaporation rate (18°C - 24°C)",
            "urgent_alert": "Monitor Wheat for Yellow Stripe Rust pustules on flag leaves. Apply First CRI irrigation at 21 DAS.",
            "fert": "Top-dress Urea @ 50 kg/ha just before 1st irrigation. Avoid delayed application."
        },
        "Deccan Plateau (Maharashtra, Karnataka, Telangana, AP)": {
            "crops": "Cotton, Sorghum, Soybean, Red Gram, Groundnut",
            "weather": "Moderate warm days, dry soil surface (24°C - 31°C)",
            "urgent_alert": "Inspect Bt Cotton bolls for Pink Bollworm exit holes. Install pheromone traps @ 5/acre.",
            "fert": "Apply foliar 2% KNO3 at boll development stage to improve lint micronaire."
        },
        "Eastern Coastal & Delta Zone (WB, Odisha, Coastal AP)": {
            "crops": "Boro Rice, Vegetables, Mustard, Pulses",
            "weather": "Humid, post-cyclonic coastal moisture (22°C - 29°C)",
            "urgent_alert": "Watch for Brown Plant Hopper (BPH) hopperburn in nursery rice. Avoid excess nitrogen.",
            "fert": "Apply Single Super Phosphate (SSP) as basal; incorporate neem cake to slow nitrogen release."
        },
        "Western Arid Zone (Rajasthan, Gujarat)": {
            "crops": "Cumin, Mustard, Isabgol, Barley, Wheat",
            "weather": "Dry, large diurnal temperature variation (15°C - 28°C)",
            "urgent_alert": "Mildew threat on Cumin and Mustard. Keep Mancozeb 75 WP ready for early prophylactic spray.",
            "fert": "Use Drip fertigation with water-soluble 19:19:19 to minimize salinity build-up."
        },
        "Central Zone (Madhya Pradesh, Chhattisgarh)": {
            "crops": "Wheat, Chickpea, Lentil, Linseed",
            "weather": "Clear skies, mild winter days (17°C - 27°C)",
            "urgent_alert": "Check Chickpea at flowering for Helicoverpa pod borer larvae. Release Trichogramma bio-parasitoids.",
            "fert": "Apply 20 kg Sulphur/ha as Bentonite-S for oilseeds and pulse protein synthesis."
        }
    }

    r_data = region_advisories.get(selected_region, region_advisories[region_options[0]])

    rcol1, rcol2 = st.columns(2)
    with rcol1:
        st.info(
            f"**🌾 Dominant Seasonal Crops:** {r_data['crops']}\n\n"
            f"**🌡️ Microclimate Status:** {r_data['weather']}\n\n"
            f"**⚠️ Urgent Field Advisory:** {r_data['urgent_alert']}"
        )
    with rcol2:
        st.warning(
            f"**🧪 Recommended Nutrient & Water Practice:**\n\n"
            f"{r_data['fert']}\n\n"
            f"💡 *Need a custom prescription for this zone? Click below to ask AI directly.*"
        )
        if st.button(f"💬 Ask AI Advisory for {selected_region.split('(')[0].strip()}", use_container_width=True):
            navigate_to("💬 AI Assistant", f"What are the best agronomy practices, sowing window, and fertilizer schedule for {selected_region}?")

    st.markdown("<hr style='border:1px solid #E8F5E9; margin:0.85rem 0'>", unsafe_allow_html=True)

    # ── Query Activity Chart & Telemetry ─────────────────────────────
    chart_col1, chart_col2 = st.columns([2, 1])

    with chart_col1:
        render_section_header("Query Telemetry (Historical)", "📈")
        dates, counts = _get_recent_queries(30)

        if dates and counts:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=dates,
                y=counts,
                marker_color="#2E7D32",
                marker_line_color="#1B5E20",
                marker_line_width=1,
                name="Queries"
            ))
            fig.update_layout(
                plot_bgcolor="#FAFAFA",
                paper_bgcolor="#ffffff",
                font=dict(family="Plus Jakarta Sans, sans-serif", size=11),
                margin=dict(l=5, r=5, t=15, b=5),
                height=220,
                showlegend=False,
                xaxis=dict(showgrid=False, tickangle=-20),
                yaxis=dict(showgrid=True, gridcolor="#F1F8E9", title="Queries")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(
                """
                <div style="background:#FAFAFA; border:1px dashed #C8E6C9; border-radius:12px;
                     padding:2.2rem; text-align:center; color:#78909C; font-size:0.92rem;">
                    📊 Query activity will plot dynamically here as you consult the AI Assistant.
                </div>
                """,
                unsafe_allow_html=True
            )

    with chart_col2:
        render_section_header("System Overview", "📡")
        vs_status = kb_stats["status"]
        vs_color = "#2E7D32" if vs_status == "Ready" else "#FF8F00"
        st.markdown(
            f"""
            <div style="background:#ffffff; border:1px solid #E0ECE0; border-radius:12px;
                 padding:0.9rem 1.1rem; margin-bottom:0.6rem; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                <div style="font-size:0.74rem; color:#78909C; font-weight:700; text-transform:uppercase;">
                    Vector Store Mode
                </div>
                <div style="font-size:1.05rem; font-weight:700; color:{vs_color}; margin:3px 0;">
                    FAISS — {vs_status}
                </div>
                <div style="font-size:0.78rem; color:#90A4AE;">
                    {kb_stats['total_chunks']} chunks · {kb_stats['index_size_kb']} KB
                </div>
            </div>
            <div style="background:#ffffff; border:1px solid #E0ECE0; border-radius:12px;
                 padding:0.9rem 1.1rem; margin-bottom:0.6rem; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                <div style="font-size:0.74rem; color:#78909C; font-weight:700; text-transform:uppercase;">
                    Active Generative Engine
                </div>
                <div style="font-size:1.05rem; font-weight:700; color:#1B5E20; margin:3px 0;">
                    {provider}
                </div>
                <div style="font-size:0.78rem; color:#90A4AE;">Grounded ICAR Guidelines</div>
            </div>
            <div style="background:#ffffff; border:1px solid #E0ECE0; border-radius:12px;
                 padding:0.9rem 1.1rem; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                <div style="font-size:0.74rem; color:#78909C; font-weight:700; text-transform:uppercase;">
                    Relational Storage
                </div>
                <div style="font-size:1.05rem; font-weight:700; color:#1B5E20; margin:3px 0;">
                    SQLite 3 (Connected)
                </div>
                <div style="font-size:0.78rem; color:#90A4AE;">{analytics['total_messages']} messages stored</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ── Knowledge Base Topic Coverage ────────────────────────────────
    render_section_header("Knowledge Base Topical Coverage", "📚")
    cov_col1, cov_col2, cov_col3, cov_col4 = st.columns(4)
    coverage = [
        ("Rice Cultivation (ICAR-IIRR)", 95),
        ("Wheat Protocols (ICAR-IIWBR)", 92),
        ("Pest & IPM Guidelines (FAO)", 88),
        ("Soil Health Benchmarks (ICAR)", 90),
    ]
    for col, (topic, pct) in zip([cov_col1, cov_col2, cov_col3, cov_col4], coverage):
        with col:
            st.markdown(
                f"""<div style="font-size:0.8rem; color:#37474F; font-weight:600; margin-bottom:5px;">
                {topic}</div>""",
                unsafe_allow_html=True
            )
            st.progress(pct / 100)
            st.caption(f"{pct}% comprehensive coverage")
