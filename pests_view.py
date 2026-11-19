"""
AgroSense AI - Pest & Disease Doctor View
Symptom-based diagnostic matching with biological, cultural, and chemical Integrated Pest Management (IPM) controls.
"""

import streamlit as st
from src.modules.pest_diagnosis import PestDiagnosisManager
from src.ui.components import render_section_header


def render_pests_view():
    """Renders the pest and disease diagnostic doctor."""
    st.subheader("🐛 Pest & Disease Diagnostic Doctor")
    st.caption("Identify crop damage, leaf discoloration, fungal spots, and stem borers with verified IPM treatment protocols.")

    pest_mgr = PestDiagnosisManager()

    # Quick Symptom Chips
    st.markdown("**🔍 Common Symptoms & Pathogens (Quick Filter):**")
    chip_labels = ["All", "Stem Borer", "Blast", "Rust", "Early Blight", "Fall Armyworm", "Whitefly", "Wilt"]
    quick_cols = st.columns(len(chip_labels))
    preset_symptom = None
    for i, chip in enumerate(chip_labels):
        with quick_cols[i]:
            if st.button(chip, key=f"pest_quick_{i}", use_container_width=True):
                preset_symptom = "" if chip == "All" else chip

    # Search and Filter Controls
    col1, col2 = st.columns([2, 1])
    with col1:
        symptom_query = st.text_input(
            "🔎 Describe Observed Symptoms or Plant Signs",
            value=preset_symptom if preset_symptom is not None else "",
            placeholder="e.g. dead hearts in stems, yellow stripes on leaves, concentric rings..."
        )
    with col2:
        crops_list = pest_mgr.get_crop_list()
        selected_crop = st.selectbox("Filter by Affected Crop", crops_list)

    # Diagnose
    diagnoses = pest_mgr.diagnose(crop=selected_crop, symptom_query=symptom_query)

    st.markdown(f"**Found {len(diagnoses)} matching pest/disease profiles:**")
    st.markdown("<hr style='border:1px solid #E8F5E9; margin:0.75rem 0'>", unsafe_allow_html=True)

    if not diagnoses:
        st.info("No diagnostic matches found. Try using simpler terms like 'yellow', 'holes', 'spots', or 'wilting'.")
        return

    for i, item in enumerate(diagnoses):
        p_name = item['name']
        severity = item.get("severity", "Moderate")
        p_type = item.get("type", "Pest")
        affected = item.get('affected_crops', 'All Crops')

        badge_class = "badge-severe" if severity == "Severe" else "badge-high" if severity == "High" else "badge-optimal"

        with st.container():
            st.markdown(
                f"""
                <div class="agri-card">
                    <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px;">
                        <h3 style="color: #C62828; margin: 0; font-size: 1.3rem; font-weight: 700;">⚠️ {p_name}</h3>
                        <div>
                            <span class="{badge_class}">Severity: {severity}</span>
                            <span class="badge-info" style="margin-left: 6px;">Type: {p_type}</span>
                        </div>
                    </div>
                    <div style="margin-top: 6px; color: #455A64; font-size: 0.92rem;">
                        <strong>Affected Crops:</strong> {affected}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Symptoms
            st.markdown(f"**🔍 Observed Symptoms & Plant Damage:**\n\n{item.get('symptoms', 'N/A')}")

            # Control protocols side-by-side
            tcol1, tcol2 = st.columns(2)
            with tcol1:
                st.success(
                    f"**🌿 Biological & Cultural Control (IPM 1st Line):**\n\n"
                    f"{item.get('biological_cultural_control', 'N/A')}"
                )
            with tcol2:
                st.warning(
                    f"**🧪 Chemical Control & Dosages (Emergency ETL):**\n\n"
                    f"{item.get('chemical_control', 'N/A')}"
                )

            # Direct AI Consultation Button
            act_col1, _ = st.columns([1.5, 3.5])
            with act_col1:
                if st.button(f"💬 Consult AI on {p_name} Treatment", key=f"ask_pest_{i}", type="primary", use_container_width=True):
                    st.session_state["pending_query"] = (
                        f"Provide step-by-step verified IPM protocol, biological remedies, and safe chemical dosages for managing {p_name} in {affected}."
                    )
                    st.session_state["nav_selection"] = "💬 AI Assistant"
                    st.rerun()

            st.caption(f"🏛️ Source Standard: `{item.get('source', 'ICAR Crop Protection Division')}`")
            st.markdown("<hr style='border:1px solid #F1F8E9; margin:0.85rem 0'>", unsafe_allow_html=True)
