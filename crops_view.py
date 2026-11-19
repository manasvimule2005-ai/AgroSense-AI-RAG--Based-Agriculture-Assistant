"""
AgroSense AI - Crop Advisory Guide View
Interactive catalogue for staple crops with environmental criteria, sowing calendars,
irrigation parameters, and direct one-click AI consultation.
"""

import streamlit as st
from src.modules.crop_guide import CropGuideManager
from src.ui.components import render_section_header


def render_crops_view():
    """Renders the crop advisory directory."""
    st.subheader("🌿 Crop Advisory & Cultivation Directory")
    st.caption("Agronomic guidelines, sowing calendars, water requirements, and soil compatibility curated from ICAR institutes.")

    crop_mgr = CropGuideManager()

    # Search and Filter Controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search Crop Name, Soil, or Practice", placeholder="e.g. Wheat, Loam, Rice, Maize...")
    with col2:
        seasons = crop_mgr.get_seasons()
        selected_season = st.selectbox("Season", seasons)
    with col3:
        categories = crop_mgr.get_categories()
        selected_category = st.selectbox("Crop Category", categories)

    # Filtered results
    crops = crop_mgr.filter_crops(
        season=selected_season,
        category=selected_category,
        query=search_query
    )

    st.markdown(f"**Showing {len(crops)} verified crop records matching criteria:**")
    st.markdown("<hr style='border:1px solid #E8F5E9; margin:0.75rem 0'>", unsafe_allow_html=True)

    if not crops:
        st.warning("No crops found matching the specified filters. Try clearing the search query.")
        return

    # Render Crop Cards
    for i, crop in enumerate(crops):
        c_name = crop['crop_name']
        s_name = crop.get('scientific_name', '')
        category = crop.get('category', 'Cereal')
        season = crop.get('season', 'Kharif')

        with st.container():
            st.markdown(
                f"""
                <div class="agri-card">
                    <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px;">
                        <h3 style="color: #1B5E20; margin: 0; font-size: 1.35rem; font-weight: 700;">
                            🌾 {c_name} 
                            <span style="font-size: 0.88rem; color: #546E7A; font-style: italic; font-weight: 400;">({s_name})</span>
                        </h3>
                        <div>
                            <span class="badge-optimal">{category}</span>
                            <span class="badge-info" style="margin-left: 6px;">Season: {season}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Details Grid
            dcol1, dcol2, dcol3, dcol4 = st.columns(4)
            with dcol1:
                st.markdown(f"**📅 Sowing Window:**\n\n{crop.get('sowing_window', 'N/A')}")
            with dcol2:
                st.markdown(f"**🌾 Harvest Window:**\n\n{crop.get('harvest_window', 'N/A')}")
            with dcol3:
                st.markdown(f"**💧 Water Need:**\n\n{crop.get('water_requirement_mm', 'N/A')} mm")
            with dcol4:
                st.markdown(f"**🌡️ Optimal Temp:**\n\n{crop.get('optimal_temperature_c', 'N/A')}")

            scol1, scol2 = st.columns([1, 2])
            with scol1:
                st.markdown(f"**🌱 Soil Compatibility:**\n\n{crop.get('soil_type', 'N/A')}")
            with scol2:
                st.markdown(f"**💡 Key Agronomy Tips:**\n\n{crop.get('key_agronomy_tips', 'N/A')}")

            # Interactive action row with functional buttons
            bcol1, bcol2, _ = st.columns([1.2, 1.2, 2.6])
            with bcol1:
                if st.button(f"💬 Consult AI on {c_name}", key=f"ask_crop_{i}", type="primary", use_container_width=True):
                    st.session_state["pending_query"] = (
                        f"Give me verified ICAR cultivation best practices, fertilizer split, and pest management for {c_name}."
                    )
                    st.session_state["nav_selection"] = "💬 AI Assistant"
                    st.rerun()

            with bcol2:
                with st.expander("📋 View Quick Details"):
                    st.markdown(f"**Verified Institute Source:** `{crop.get('source', 'ICAR Standard Guidelines')}`")
                    st.markdown(f"**Growth Cycle:** `{season}` season")
                    st.markdown(f"**Optimal Irrigation:** `{crop.get('water_requirement_mm', 'N/A')} mm` total seasonal requirement.")

            st.markdown("<hr style='border:1px solid #F1F8E9; margin:0.85rem 0'>", unsafe_allow_html=True)
