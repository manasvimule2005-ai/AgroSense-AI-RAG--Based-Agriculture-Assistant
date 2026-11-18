"""
AgroSense AI - Pest & Disease Doctor View
Symptom-based diagnostic matching with biological, cultural, and chemical IPM controls,
interactive plant-part diagnostic matrix, and pesticide safety calculator.
"""

import streamlit as st
from src.modules.pest_diagnosis import PestDiagnosisManager
from src.ui.components import render_section_header, render_metric, navigate_to


def render_pests_view():
    """Renders the pest and disease diagnostic doctor."""
    st.subheader("🐛 Pest & Disease Diagnostic Doctor")
    st.caption("Identify crop damage, leaf discoloration, fungal spots, and stem borers with verified IPM treatment protocols.")

    pest_mgr = PestDiagnosisManager()

    tab1, tab2, tab3 = st.tabs(["🔍 Symptom Diagnostic Doctor", "🔬 Plant Part Matrix", "⚠️ Pesticide Safety & PHI"])

    # ── TAB 1: SYMPTOM DIAGNOSTIC DOCTOR ────────────────────────────
    with tab1:
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
        else:
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
                            navigate_to(
                                "💬 AI Assistant",
                                f"Provide step-by-step verified IPM protocol, biological remedies, and safe chemical dosages for managing {p_name} in {affected}."
                            )

                    st.caption(f"🏛️ Source Standard: `{item.get('source', 'ICAR Crop Protection Division')}`")
                    st.markdown("<hr style='border:1px solid #F1F8E9; margin:0.85rem 0'>", unsafe_allow_html=True)

    # ── TAB 2: PLANT PART DIAGNOSTIC MATRIX ──────────────────────────
    with tab2:
        render_section_header("Diagnostic Matrix by Affected Anatomy", "🔬")
        st.caption("Select where the damage is occurring on the plant to narrow down potential culprits:")

        mcol1, mcol2 = st.columns(2)
        with mcol1:
            plant_part = st.selectbox(
                "Plant Part Showing Symptoms",
                ["All Parts", "Leaves & Foliage", "Stems & Shoots", "Whorls & Central Growing Point", "Roots & Collar", "Flowers, Bolls & Fruits"]
            )
        with mcol2:
            symptom_category = st.selectbox(
                "Primary Symptom Appearance",
                ["All Symptoms", "Holes, Boring & Chewing Damage", "Spots, Lesions & Concentric Rings", "Yellowing, Curling & Honeydew", "Wilting, Lodging & Root Decay"]
            )

        # Keyword mapping for anatomical matrix
        part_keywords = {
            "Leaves & Foliage": ["leaf", "leaves", "foliage", "stripe", "pustule", "spot"],
            "Stems & Shoots": ["stem", "shoot", "stalk", "borer", "deadheart", "collar"],
            "Whorls & Central Growing Point": ["whorl", "deadheart", "bud", "central shoot"],
            "Roots & Collar": ["root", "wilt", "collar", "decay", "damping"],
            "Flowers, Bolls & Fruits": ["boll", "fruit", "flower", "cob", "ear", "pod"]
        }

        # Filter all pests against keywords
        all_p = pest_mgr.get_all_pests()
        matched_matrix = []
        for p in all_p:
            text = (p.get("symptoms", "") + " " + p.get("name", "")).lower()
            part_match = True
            if plant_part != "All Parts":
                part_match = any(kw in text for kw in part_keywords.get(plant_part, []))
            
            symptom_match = True
            if symptom_category == "Holes, Boring & Chewing Damage":
                symptom_match = any(k in text for k in ["hole", "bore", "chew", "windowpane", "caterpillar", "borer", "larva"])
            elif symptom_category == "Spots, Lesions & Concentric Rings":
                symptom_match = any(k in text for k in ["spot", "lesion", "ring", "blast", "rust", "pustule", "concentric"])
            elif symptom_category == "Yellowing, Curling & Honeydew":
                symptom_match = any(k in text for k in ["yellow", "curl", "honeydew", "sooty", "whitefly", "aphid", "chlorosis"])
            elif symptom_category == "Wilting, Lodging & Root Decay":
                symptom_match = any(k in text for k in ["wilt", "lodge", "decay", "rot", "deadheart", "droop"])

            if part_match and symptom_match:
                matched_matrix.append(p)

        st.markdown(f"**Identified {len(matched_matrix)} potential disease/pest candidates:**")
        for p in matched_matrix:
            with st.expander(f"⚠️ {p['name']} ({p.get('type', 'Pest')}) — Affecting: {p.get('affected_crops', 'All')}"):
                st.markdown(f"**Damage Symptoms:** {p.get('symptoms', '')}")
                st.markdown(f"**Biological Solution:** {p.get('biological_cultural_control', '')}")
                st.markdown(f"**Chemical Solution:** {p.get('chemical_control', '')}")
                if st.button(f"💬 Ask AI about {p['name']}", key=f"mat_ask_{p['name']}"):
                    navigate_to("💬 AI Assistant", f"How do I diagnose and treat {p['name']} on {plant_part}?")

    # ── TAB 3: PESTICIDE SAFETY & PHI ────────────────────────────────
    with tab3:
        render_section_header("Pesticide Safety & Pre-Harvest Interval (PHI) Reference", "⚠️")
        st.caption("Verified guidelines on safe withholding periods, PPE, and IRAC resistance management:")

        chemicals = [
            {"Chemical": "Emamectin benzoate 5 SG", "Target": "Fall Armyworm, Bollworms", "Dosage": "0.4 g/L", "PHI (Days)": 7, "Toxicity Class": "Class III (Slightly Hazardous)", "PPE Required": "Gloves, Mask, Eye Goggles"},
            {"Chemical": "Chlorantraniliprole 18.5 SC", "Target": "Stem Borers, Armyworms", "Dosage": "0.3 ml/L", "PHI (Days)": 14, "Toxicity Class": "Class IV (Practically Non-toxic)", "PPE Required": "Gloves, Mask"},
            {"Chemical": "Mancozeb 75 WP", "Target": "Early/Late Blight, Rust", "Dosage": "2.5 g/L", "PHI (Days)": 15, "Toxicity Class": "Class III (Caution)", "PPE Required": "Face Shield, Full Sleeves, Gloves"},
            {"Chemical": "Flonicamid 50 WG", "Target": "Whiteflies, Aphids, Jassids", "Dosage": "0.3 g/L", "PHI (Days)": 10, "Toxicity Class": "Class IV (Low Toxicity to Bees)", "PPE Required": "Gloves, Dust Mask"},
            {"Chemical": "Propiconazole 25 EC", "Target": "Sheath Blight, Karnal Bunt, Rust", "Dosage": "1.0 ml/L", "PHI (Days)": 21, "Toxicity Class": "Class II (Moderately Hazardous)", "PPE Required": "Respirator, Protective Suit, Rubber Gloves"},
            {"Chemical": "Spinosad 45 SC", "Target": "Thrips, Helicoverpa, Leaf Miner", "Dosage": "0.3 ml/L", "PHI (Days)": 3, "Toxicity Class": "Class IV (Eco-friendly bio-chemical)", "PPE Required": "Basic Gloves, Mask"}
        ]

        st.dataframe(pd.DataFrame(chemicals), use_container_width=True, hide_index=True)

        st.warning(
            "🛡️ **Critical Golden Rules for Chemical Sprays:**\n\n"
            "1. **Pre-Harvest Interval (PHI):** Never harvest crops before the stated PHI days have elapsed to ensure chemical residues break down below Maximum Residue Limits (MRL).\n"
            "2. **Spray Timing:** Spray during early morning (6:30–9:00 AM) or late afternoon (4:00–6:00 PM) to minimize honeybee toxicity and spray evaporation.\n"
            "3. **Rotation:** Never use the same chemical active ingredient consecutively; rotate modes of action to prevent pest resistance."
        )

        if st.button("💬 Ask AI on Safe Organic Alternatives", type="primary"):
            navigate_to("💬 AI Assistant", "What are the most effective organic bio-pesticides (Neem oil, Beauveria bassiana, Trichoderma) and how to prepare them?")
