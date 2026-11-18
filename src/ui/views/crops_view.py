"""
AgroSense AI - Crop Advisory Guide View
Interactive catalogue for staple crops with environmental criteria, sowing calendars,
side-by-side crop comparison, and farm water requirement calculator.
"""

import streamlit as st
import pandas as pd
from src.modules.crop_guide import CropGuideManager
from src.ui.components import render_section_header, render_metric, navigate_to


def render_crops_view():
    """Renders the crop advisory directory."""
    st.subheader("🌿 Crop Advisory & Cultivation Directory")
    st.caption("Agronomic guidelines, sowing calendars, water requirements, crop comparison, and irrigation calculators.")

    crop_mgr = CropGuideManager()
    all_crops = crop_mgr.get_all_crops()

    tab1, tab2, tab3 = st.tabs(["🌾 Crop Directory", "⚖️ Compare Two Crops", "💧 Irrigation Calculator"])

    # ── TAB 1: CROP DIRECTORY ───────────────────────────────────────
    with tab1:
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
        else:
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

                    # Action buttons
                    bcol1, bcol2, _ = st.columns([1.3, 1.3, 2.4])
                    with bcol1:
                        if st.button(f"💬 Consult AI on {c_name}", key=f"ask_crop_{i}", type="primary", use_container_width=True):
                            navigate_to(
                                "💬 AI Assistant",
                                f"Give me verified ICAR cultivation best practices, fertilizer split, and pest management for {c_name}."
                            )

                    with bcol2:
                        with st.expander("📋 View Quick Details"):
                            st.markdown(f"**Verified Institute Source:** `{crop.get('source', 'ICAR Standard Guidelines')}`")
                            st.markdown(f"**Growth Cycle:** `{season}` season")
                            st.markdown(f"**Optimal Irrigation:** `{crop.get('water_requirement_mm', 'N/A')} mm` total seasonal requirement.")

                    st.markdown("<hr style='border:1px solid #F1F8E9; margin:0.85rem 0'>", unsafe_allow_html=True)

    # ── TAB 2: CROP COMPARATOR ──────────────────────────────────────
    with tab2:
        render_section_header("Side-by-Side Crop Comparison", "⚖️")
        st.caption("Select two crops to compare their water needs, growing periods, temperature limits, and soil compatibility:")

        crop_names = [c["crop_name"] for c in all_crops]
        if len(crop_names) >= 2:
            ccol1, ccol2 = st.columns(2)
            with ccol1:
                crop_a_name = st.selectbox("Select Crop A", crop_names, index=0)
            with ccol2:
                crop_b_name = st.selectbox("Select Crop B", crop_names, index=1 if len(crop_names) > 1 else 0)

            crop_a = crop_mgr.get_crop_by_name(crop_a_name)
            crop_b = crop_mgr.get_crop_by_name(crop_b_name)

            if crop_a and crop_b:
                comp_data = [
                    {"Parameter": "Scientific Name", crop_a_name: crop_a.get("scientific_name", "N/A"), crop_b_name: crop_b.get("scientific_name", "N/A")},
                    {"Parameter": "Category", crop_a_name: crop_a.get("category", "N/A"), crop_b_name: crop_b.get("category", "N/A")},
                    {"Parameter": "Growing Season", crop_a_name: crop_a.get("season", "N/A"), crop_b_name: crop_b.get("season", "N/A")},
                    {"Parameter": "Sowing Period", crop_a_name: crop_a.get("sowing_window", "N/A"), crop_b_name: crop_b.get("sowing_window", "N/A")},
                    {"Parameter": "Harvest Period", crop_a_name: crop_a.get("harvest_window", "N/A"), crop_b_name: crop_b.get("harvest_window", "N/A")},
                    {"Parameter": "Water Requirement (mm)", crop_a_name: f"{crop_a.get('water_requirement_mm', 'N/A')} mm", crop_b_name: f"{crop_b.get('water_requirement_mm', 'N/A')} mm"},
                    {"Parameter": "Optimal Temperature", crop_a_name: crop_a.get("optimal_temperature_c", "N/A"), crop_b_name: crop_b.get("optimal_temperature_c", "N/A")},
                    {"Parameter": "Soil Preference", crop_a_name: crop_a.get("soil_type", "N/A"), crop_b_name: crop_b.get("soil_type", "N/A")},
                    {"Parameter": "Key Advisory Tip", crop_a_name: crop_a.get("key_agronomy_tips", "N/A"), crop_b_name: crop_b.get("key_agronomy_tips", "N/A")},
                ]
                st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)

                c_btn1, c_btn2, _ = st.columns([1.5, 1.5, 2])
                with c_btn1:
                    if st.button(f"💬 Ask AI: Compare {crop_a_name} vs {crop_b_name}", type="primary", use_container_width=True):
                        navigate_to("💬 AI Assistant", f"Compare the agronomic viability, profitability, water consumption, and soil requirements of {crop_a_name} vs {crop_b_name}.")

    # ── TAB 3: IRRIGATION CALCULATOR ─────────────────────────────────
    with tab3:
        render_section_header("Farm Seasonal Water Requirement Calculator", "💧")
        st.caption("Calculate the exact volume of water your farm will need based on crop water depth and field area:")

        ical1, ical2, ical3 = st.columns(3)
        with ical1:
            calc_crop_name = st.selectbox("Select Crop", crop_names, key="calc_crop")
            selected_calc_crop = crop_mgr.get_crop_by_name(calc_crop_name)
        with ical2:
            farm_size = st.number_input("Farm Area", min_value=0.25, max_value=500.0, value=2.0, step=0.5)
        with ical3:
            area_unit = st.selectbox("Area Unit", ["Acres", "Hectares"])

        # Conversion
        # 1 Acre = 4046.86 m2; 1 Hectare = 10,000 m2
        area_m2 = farm_size * 4046.86 if area_unit == "Acres" else farm_size * 10000.0
        depth_mm = 500
        if selected_calc_crop:
            try:
                # Handle range e.g. "450 - 650"
                w_str = str(selected_calc_crop.get("water_requirement_mm", "500"))
                if "-" in w_str:
                    parts = [float(p.strip()) for p in w_str.split("-") if p.strip()]
                    depth_mm = sum(parts) / len(parts)
                else:
                    depth_mm = float(w_str)
            except Exception:
                depth_mm = 500

        # Total Volume = Area (m2) * depth (m)
        depth_m = depth_mm / 1000.0
        total_m3 = round(area_m2 * depth_m, 1)
        total_liters = total_m3 * 1000
        # Standard flood irrigation pass is ~50mm depth
        num_passes = max(1, round(depth_mm / 50))
        drip_saving_m3 = round(total_m3 * 0.40, 1)

        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            render_metric("Total Water Needed", f"{total_m3:,.0f} m³", f"{total_liters:,.0f} Liters", "💧")
        with mcol2:
            render_metric("Crop Water Depth", f"{depth_mm:.0f} mm", f"{selected_calc_crop.get('season', 'Kharif')} season", "📏")
        with mcol3:
            render_metric("Recommended Passes", f"{num_passes} Irrigations", "~50 mm per flooding pass", "🔄")
        with mcol4:
            render_metric("Drip Savings Potential", f"{drip_saving_m3:,.0f} m³", "Save up to 40-50% water", "🌱")

        st.info(
            f"💡 **Irrigation Summary for {farm_size} {area_unit} of {calc_crop_name}:**\n\n"
            f"- Seasonal requirement: **{total_m3:,.0f} cubic meters ({total_liters:,.0f} Liters)** of water.\n"
            f"- Adopting **micro-drip irrigation** or sprinkler systems can conserve **{drip_saving_m3:,.0f} m³** of groundwater while preventing nutrient leaching.\n"
            f"- Critical stage: Check the Crop Guide card for moisture-sensitive flowering and fruit-setting stages."
        )

        if st.button(f"💬 Ask AI for {calc_crop_name} Irrigation Schedule", type="primary"):
            navigate_to("💬 AI Assistant", f"Provide a complete stage-by-stage critical irrigation schedule for {calc_crop_name} in {area_unit.lower()}.")
