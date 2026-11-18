"""
AgroSense AI - UI Components & Custom Styling
Defines reusable visual components, navigation helpers, cards, metrics, and premium agricultural styling.
"""

from typing import Any
import streamlit as st


def navigate_to(tab_name: str, pending_query: str = None):
    """Guaranteed safe navigation helper that adheres to Streamlit widget lifecycle."""
    st.session_state["redirect_to_tab"] = tab_name
    if pending_query:
        st.session_state["pending_query"] = pending_query
    st.rerun()


def inject_custom_css():
    """Injects high-quality, modern professional agricultural theme styling."""
    st.markdown(
        """
        <style>
        /* ── Google Fonts ── */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            letter-spacing: -0.01em;
        }

        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* ── Main Layout Container ── */
        .main .block-container {
            padding-top: 1.1rem;
            padding-bottom: 3.5rem;
            max-width: 1340px;
        }

        /* ── Custom Scrollbar ── */
        ::-webkit-scrollbar { width: 7px; height: 7px; }
        ::-webkit-scrollbar-track { background: #F1F8E9; border-radius: 4px; }
        ::-webkit-scrollbar-thumb { background: #81C784; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #4CAF50; }

        /* ── Top Header Banner ── */
        .agri-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: linear-gradient(135deg, #0d3b13 0%, #1b5e20 40%, #2e7d32 75%, #388e3c 100%);
            padding: 1.35rem 2.2rem;
            border-radius: 18px;
            color: #ffffff;
            margin-bottom: 1.6rem;
            box-shadow: 0 10px 30px rgba(13, 59, 19, 0.22), 0 2px 8px rgba(0,0,0,0.06);
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.12);
        }
        .agri-header::before {
            content: '';
            position: absolute;
            top: -50px; right: -50px;
            width: 220px; height: 220px;
            background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0) 70%);
            border-radius: 50%;
            pointer-events: none;
        }
        .agri-header::after {
            content: '';
            position: absolute;
            bottom: -70px; right: 120px;
            width: 260px; height: 260px;
            background: radial-gradient(circle, rgba(165,214,167,0.12) 0%, rgba(255,255,255,0) 70%);
            border-radius: 50%;
            pointer-events: none;
        }
        .agri-header-content {
            display: flex;
            align-items: center;
            gap: 20px;
            z-index: 1;
        }
        .agri-header-icon {
            font-size: 3rem;
            line-height: 1;
            filter: drop-shadow(0 4px 12px rgba(0,0,0,0.25));
        }
        .agri-header h1 {
            color: #ffffff !important;
            margin: 0;
            font-size: 1.95rem;
            font-weight: 800;
            letter-spacing: -0.8px;
            line-height: 1.15;
        }
        .agri-header p {
            color: #E8F5E9 !important;
            margin: 5px 0 0 0;
            font-size: 0.95rem;
            font-weight: 400;
            opacity: 0.95;
        }
        .header-badges {
            display: flex;
            gap: 8px;
            margin-top: 8px;
            flex-wrap: wrap;
        }
        .header-badge {
            background: rgba(255, 255, 255, 0.18);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.28);
            border-radius: 20px;
            padding: 3px 12px;
            font-size: 0.76rem;
            font-weight: 600;
            color: #ffffff;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }

        /* ── Metric Cards ── */
        .metric-card {
            background: #ffffff;
            border: 1px solid #E8F0E8;
            border-left: 4px solid #2E7D32;
            border-radius: 14px;
            padding: 1.1rem 1.35rem;
            box-shadow: 0 4px 14px rgba(46, 125, 50, 0.05), 0 1px 3px rgba(0,0,0,0.03);
            margin-bottom: 0.85rem;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
        }
        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 24px rgba(46, 125, 50, 0.12), 0 2px 6px rgba(0,0,0,0.04);
            border-color: #A5D6A7;
        }
        .metric-title {
            font-size: 0.74rem;
            color: #607D8B;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.9px;
        }
        .metric-val {
            font-size: 2.05rem;
            font-weight: 800;
            color: #1B5E20;
            margin: 5px 0 2px 0;
            line-height: 1.1;
            letter-spacing: -0.8px;
        }
        .metric-sub {
            font-size: 0.78rem;
            color: #78909C;
            font-weight: 500;
        }
        .metric-icon {
            font-size: 1.6rem;
            position: absolute;
            top: 1rem;
            right: 1.2rem;
            opacity: 0.85;
        }

        /* ── Agri Directory Cards (Crop & Pest) ── */
        .agri-card {
            background: #ffffff;
            border: 1px solid #E0EBE0;
            border-radius: 14px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        }
        .agri-card:hover {
            box-shadow: 0 10px 28px rgba(27, 94, 32, 0.09);
            border-color: #81C784;
            transform: translateY(-2px);
        }

        /* ── Status & Severity Badges ── */
        .badge-severe {
            background: linear-gradient(135deg, #FFEBEE, #FFCDD2);
            color: #B71C1C;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.74rem;
            font-weight: 700;
            border: 1px solid #EF9A9A;
            display: inline-block;
        }
        .badge-high {
            background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
            color: #E65100;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.74rem;
            font-weight: 700;
            border: 1px solid #FFCC80;
            display: inline-block;
        }
        .badge-optimal {
            background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
            color: #1B5E20;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.74rem;
            font-weight: 700;
            border: 1px solid #A5D6A7;
            display: inline-block;
        }
        .badge-info {
            background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
            color: #0D47A1;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.74rem;
            font-weight: 700;
            border: 1px solid #90CAF9;
            display: inline-block;
        }

        /* ── Citation Chips ── */
        .citation-chip {
            display: inline-flex;
            align-items: center;
            background: #F1F8E9;
            color: #2E7D32;
            font-size: 0.74rem;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 8px;
            border: 1px solid #C8E6C9;
            margin: 3px 5px 3px 0;
        }

        /* ── Section Headers ── */
        .section-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 1.4rem 0 0.8rem 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #E8F5E9;
        }
        .section-header h4 {
            margin: 0;
            color: #1B5E20;
            font-weight: 700;
            font-size: 1.08rem;
            letter-spacing: -0.3px;
        }

        /* ── Sidebar Styling ── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #F8FAF8 0%, #F1F6F1 100%);
            border-right: 1px solid #E0ECE0;
        }
        [data-testid="stSidebar"] .stRadio > div {
            gap: 4px;
        }
        [data-testid="stSidebar"] .stRadio label {
            border-radius: 10px;
            padding: 8px 12px;
            transition: all 0.18s ease;
            font-weight: 600;
            color: #263238;
        }
        [data-testid="stSidebar"] .stRadio label:hover {
            background: #E8F5E9;
            color: #1B5E20;
        }

        /* ── Buttons ── */
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            padding: 0.45rem 1.05rem;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            border: 1px solid #CFD8DC;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.08);
            border-color: #81C784;
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #2E7D32, #1B5E20);
            color: #ffffff;
            border: none;
            box-shadow: 0 4px 12px rgba(46, 125, 50, 0.25);
        }
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #388E3C, #2E7D32);
            box-shadow: 0 8px 20px rgba(46, 125, 50, 0.35);
        }

        /* ── Form Inputs ── */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            border-radius: 10px;
            border: 1px solid #CFD8DC;
            font-size: 0.94rem;
        }
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {
            border-color: #2E7D32;
            box-shadow: 0 0 0 2px rgba(46, 125, 50, 0.15);
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            background: #F1F8E9;
            border-radius: 12px;
            padding: 5px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 9px;
            font-weight: 600;
            color: #37474F;
            padding: 8px 16px;
        }
        .stTabs [aria-selected="true"] {
            background: #ffffff !important;
            color: #1B5E20 !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }

        /* ── Chat Messages ── */
        [data-testid="stChatMessage"] {
            border-radius: 14px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.03);
            border: 1px solid #ECEFF1;
        }

        /* ── Alert Callouts ── */
        .stAlert {
            border-radius: 12px;
            border-left-width: 5px;
        }

        /* ── Banner Boxes ── */
        .offline-banner {
            background: linear-gradient(135deg, #FFFDE7, #FFF9C4);
            border: 1px solid #FFE082;
            border-left: 5px solid #FF8F00;
            border-radius: 12px;
            padding: 0.85rem 1.2rem;
            margin-bottom: 1.1rem;
            font-size: 0.9rem;
            color: #4E342E;
        }

        /* ── Knowledge Base File Cards ── */
        .kb-file-card {
            background: #FAFAFA;
            border: 1px solid #ECEFF1;
            border-radius: 12px;
            padding: 0.9rem 1.25rem;
            margin-bottom: 0.65rem;
            transition: all 0.2s ease;
        }
        .kb-file-card:hover {
            background: #F1F8E9;
            border-color: #A5D6A7;
            transform: translateX(2px);
        }

        /* ── Dataframes ── */
        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #E0E0E0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_header():
    """Renders the top branding header."""
    st.markdown(
        """
        <div class="agri-header">
            <div class="agri-header-content">
                <div class="agri-header-icon">🌱</div>
                <div>
                    <h1>AgroSense AI</h1>
                    <p>Generative AI &amp; RAG Precision Agricultural Intelligence Assistant</p>
                    <div class="header-badges">
                        <span class="header-badge">🏛️ ICAR &amp; FAO Benchmarks</span>
                        <span class="header-badge">⚡ FAISS Vector Search</span>
                        <span class="header-badge">🔬 Precision Agronomy</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_metric(title: str, value: Any, subtext: str = "", icon: str = ""):
    """Renders a styled metric tile."""
    icon_html = f'<div class="metric-icon">{icon}</div>' if icon else ""
    st.markdown(
        f"""
        <div class="metric-card">
            {icon_html}
            <div class="metric-title">{title}</div>
            <div class="metric-val">{value}</div>
            <div class="metric-sub">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_section_header(title: str, icon: str = ""):
    """Renders a styled section header with divider."""
    icon_html = f'<span style="font-size: 1.35rem;">{icon}</span>' if icon else ""
    st.markdown(
        f"""
        <div class="section-header">
            {icon_html}
            <h4>{title}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
