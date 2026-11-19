"""
AgroSense AI – RAG-Based Agriculture Assistant
Main Streamlit Application Entrypoint
"""

import streamlit as st
from src.ui.components import inject_custom_css, render_header
from src.ui.views.dashboard_view import render_dashboard_view
from src.ui.views.chat_view import render_chat_view
from src.ui.views.crops_view import render_crops_view
from src.ui.views.pests_view import render_pests_view
from src.ui.views.soil_view import render_soil_view
from src.ui.views.kb_view import render_kb_view
from src.ui.views.settings_view import render_settings_view
from src.ui.views.analytics_view import render_analytics_view
from src.ui.views.history_view import render_history_view
from src.rag.vector_store import AgroVectorStore
from src.config import AppConfig

# ── Page Setup ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgroSense AI - Precision Agriculture Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom UI styling
inject_custom_css()

# Render top branding banner
render_header()

# ── Ensure FAISS index is initialized ──────────────────────────────
@st.cache_resource(show_spinner="🌱 Initializing Agricultural FAISS Vector Store...")
def get_initialized_vector_store():
    store = AgroVectorStore()
    if not store.is_indexed():
        store.build_index()
    else:
        store.load()
    return store

vector_store = get_initialized_vector_store()

# ── Navigation Options ──────────────────────────────────────────────
NAV_OPTIONS = [
    "🌾 Dashboard",
    "💬 AI Assistant",
    "🌿 Crop Guide",
    "🐛 Pest & Disease Doctor",
    "🧪 Soil Health Card",
    "📚 Knowledge Base",
    "📊 Analytics",
    "🗂️ Chat History",
    "⚙️ Settings",
]

# Ensure nav_selection is initialized in session state
if "nav_selection" not in st.session_state:
    st.session_state["nav_selection"] = NAV_OPTIONS[0]
elif st.session_state["nav_selection"] not in NAV_OPTIONS:
    st.session_state["nav_selection"] = NAV_OPTIONS[0]

# ── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 1.25rem; padding-bottom: 1rem;
             border-bottom: 1px solid #E0ECE0;">
            <div style="font-size: 2.8rem; margin-bottom: 0.2rem; filter: drop-shadow(0 2px 6px rgba(0,0,0,0.1));">🌾</div>
            <h2 style="margin: 0; color: #1B5E20; font-size: 1.35rem; font-weight: 800; letter-spacing: -0.4px;">
                AgroSense AI
            </h2>
            <span style="font-size: 0.78rem; color: #546E7A; font-weight: 600;">
                Precision Agronomy Assistant
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Sidebar Navigation Radio with key="nav_selection"
    selected_nav = st.radio(
        "Navigation Menu",
        NAV_OPTIONS,
        key="nav_selection",
        label_visibility="collapsed"
    )

    st.markdown("---")

    # ── System Status Panel ──────────────────────────────────────────
    provider = AppConfig.get_llm_provider().upper()
    kb_stats = vector_store.get_stats()
    vs_status_color = "#2E7D32" if kb_stats["status"] == "Ready" else "#FF8F00"

    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1px solid #E0ECE0; border-radius: 12px; padding: 0.85rem; box-shadow: 0 1px 4px rgba(0,0,0,0.03);">
            <div style="font-size: 0.74rem; color: #78909C; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">
                📡 System Telemetry
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 0.82rem; color: #455A64; font-weight: 500;">LLM Engine</span>
                <span style="font-size: 0.82rem; font-weight: 700; color: #1B5E20; background: #E8F5E9; padding: 2px 8px; border-radius: 6px;">{provider}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 0.82rem; color: #455A64; font-weight: 500;">Vector Store</span>
                <span style="font-size: 0.82rem; font-weight: 700; color: {vs_status_color}; background: #F1F8E9; padding: 2px 8px; border-radius: 6px;">{kb_stats['status']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.82rem; color: #455A64; font-weight: 500;">Indexed Chunks</span>
                <span style="font-size: 0.82rem; font-weight: 700; color: #37474F;">{kb_stats['total_chunks']} chunks</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Help / Support Info ──────────────────────────────────────────
    st.info(
        "📞 **Kisan Call Centre (India):**\n\n"
        "Toll-Free: `1800-180-1551`\n\n"
        "*Verified ICAR & FAO agronomic datasets integrated.*"
    )

    st.markdown(
        "<div style='text-align: center; font-size: 0.72rem; color: #90A4AE; margin-top: 1rem;'>"
        "AgroSense AI v1.2 · Precision Agriculture"
        "</div>",
        unsafe_allow_html=True
    )

# ── View Dispatcher ─────────────────────────────────────────────────
if selected_nav == "🌾 Dashboard":
    render_dashboard_view()
elif selected_nav == "💬 AI Assistant":
    render_chat_view()
elif selected_nav == "🌿 Crop Guide":
    render_crops_view()
elif selected_nav == "🐛 Pest & Disease Doctor":
    render_pests_view()
elif selected_nav == "🧪 Soil Health Card":
    render_soil_view()
elif selected_nav == "📚 Knowledge Base":
    render_kb_view()
elif selected_nav == "📊 Analytics":
    render_analytics_view()
elif selected_nav == "🗂️ Chat History":
    render_history_view()
elif selected_nav == "⚙️ Settings":
    render_settings_view()
