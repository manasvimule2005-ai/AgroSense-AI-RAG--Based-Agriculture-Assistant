"""
AgroSense AI - Soil Health Card Evaluator View
Interactive calculator adhering to ICAR & FAO Soil Health Card benchmarks with precision fertilizer recommendations.
"""

import streamlit as st
import pandas as pd
import json
from src.modules.soil_calculator import SoilHealthEvaluator
from src.database.db import save_soil_record, get_recent_soil_records
from src.ui.components import render_section_header, render_metric


def render_soil_view():
    """Renders the Soil Health Card evaluator interface."""
    st.subheader("🧪 Soil Health Card & Fertilizer Calculator")
    st.caption("Calculate soil fertility indices, diagnose pH/salinity stress, and compute tailored fertilizer dosages according to ICAR benchmarks.")

    tab1, tab2 = st.tabs(["📝 New Soil Test Evaluation", "📜 Historical Soil Tests"])

    with tab1:
        # Quick Presets for fast testing
        st.markdown("**⚡ Quick Test Presets (Click to autofill parameters):**")
        p_col1, p_col2, p_col3, p_col4 = st.columns(4)

        if "soil_params" not in st.session_state:
            st.session_state["soil_params"] = {
                "farmer": "Ramesh Kumar", "loc": "Plot 4, Sector B", "crop": "Rice (Paddy)",
                "ph": 7.2, "ec": 0.65, "oc": 0.48, "n": 245.0, "p": 19.5, "k": 210.0, "zn": 0.55, "s": 12.5
            }

        with p_col1:
            if st.button("🌱 Optimal Alluvial Loam", use_container_width=True):
                st.session_state["soil_params"] = {
                    "farmer": "Suresh Patel", "loc": "North Field, Anand", "crop": "Wheat",
                    "ph": 7.1, "ec": 0.45, "oc": 0.82, "n": 380.0, "p": 35.0, "k": 280.0, "zn": 0.85, "s": 18.0
                }
                st.rerun()

        with p_col2:
            if st.button("⚠️ Acidic Red Soil (Low pH)", use_container_width=True):
                st.session_state["soil_params"] = {
                    "farmer": "Bijoy Das", "loc": "Tea Belt, Jorhat", "crop": "Rice (Paddy)",
                    "ph": 5.2, "ec": 0.35, "oc": 0.65, "n": 220.0, "p": 14.0, "k": 130.0, "zn": 0.40, "s": 8.0
                }
                st.rerun()

        with p_col3:
            if st.button("⚠️ Alkaline Sodic (High pH)", use_container_width=True):
                st.session_state["soil_params"] = {
                    "farmer": "Harpreet Singh", "loc": "Karnal Belt, Haryana", "crop": "Wheat",
                    "ph": 8.9, "ec": 1.20, "oc": 0.32, "n": 180.0, "p": 12.0, "k": 310.0, "zn": 0.35, "s": 7.5
                }
                st.rerun()

        with p_col4:
            if st.button("🌊 Coastal Saline Soil", use_container_width=True):
                st.session_state["soil_params"] = {
                    "farmer": "Narasimha Rao", "loc": "Krishna Delta, AP", "crop": "Cotton",
                    "ph": 7.8, "ec": 3.40, "oc": 0.40, "n": 210.0, "p": 18.0, "k": 260.0, "zn": 0.50, "s": 11.0
                }
                st.rerun()

        p = st.session_state["soil_params"]

        with st.form("soil_evaluation_form"):
            st.markdown("#### 🌾 Farm & Field Details")
            fcol1, fcol2, fcol3 = st.columns(3)
            with fcol1:
                farmer_name = st.text_input("Farmer Name", value=p["farmer"])
            with fcol2:
                field_location = st.text_input("Field / Village Location", value=p["loc"])
            with fcol3:
                crop_options = ["Rice (Paddy)", "Wheat", "Maize", "Tomato", "Cotton", "Chickpea", "Groundnut", "Mustard", "Vegetables"]
                c_idx = crop_options.index(p["crop"]) if p["crop"] in crop_options else 0
                target_crop = st.selectbox("Target Crop for Next Season", crop_options, index=c_idx)

            st.markdown("#### 🔬 Laboratory Soil Test Parameters")
            pcol1, pcol2, pcol3 = st.columns(3)
            with pcol1:
                ph = st.number_input("Soil pH (Reaction)", min_value=3.5, max_value=11.0, value=float(p["ph"]), step=0.1, help="Optimal: 6.5 - 7.5. <6.0 = Acidic, >8.5 = Sodic/Alkaline")
                ec = st.number_input("Electrical Conductivity (EC, dS/m)", min_value=0.0, max_value=15.0, value=float(p["ec"]), step=0.05, help="Normal: <1.0 dS/m. >2.0 = Saline")
                oc = st.number_input("Organic Carbon (OC, %)", min_value=0.05, max_value=4.0, value=float(p["oc"]), step=0.02, help="Low: <0.50%, Medium: 0.50-0.75%, High: >0.75%")

            with pcol2:
                n = st.number_input("Available Nitrogen (N, kg/ha)", min_value=50.0, max_value=1000.0, value=float(p["n"]), step=5.0, help="Low: <280, Medium: 280-560, High: >560 kg/ha")
                p_val = st.number_input("Available Phosphorus (P2O5, kg/ha)", min_value=5.0, max_value=150.0, value=float(p["p"]), step=1.0, help="Low: <23, Medium: 23-56, High: >56 kg/ha")
                k = st.number_input("Available Potassium (K2O, kg/ha)", min_value=30.0, max_value=800.0, value=float(p["k"]), step=5.0, help="Low: <144, Medium: 144-336, High: >336 kg/ha")

            with pcol3:
                zn = st.number_input("Available Zinc (Zn, ppm)", min_value=0.1, max_value=5.0, value=float(p["zn"]), step=0.05, help="Deficient: <0.60 ppm, Adequate: >=0.60 ppm")
                s = st.number_input("Available Sulfur (S, ppm)", min_value=1.0, max_value=50.0, value=float(p["s"]), step=0.5, help="Deficient: <10.0 ppm, Sufficient: >=10.0 ppm")

            submitted = st.form_submit_button("🌱 Compute Soil Health Index & Prescription", type="primary", use_container_width=True)

        if submitted:
            result = SoilHealthEvaluator.evaluate(
                ph=ph, ec=ec, oc=oc, n=n, p=p_val, k=k, zn=zn, s=s, target_crop=target_crop
            )

            # Persist record in SQLite
            summary_txt = f"Score: {result['health_score']}/100, Grade: {result['grade']}"
            rec_id = save_soil_record(
                farmer_name=farmer_name,
                field_location=field_location,
                target_crop=target_crop,
                ph=ph, ec=ec, oc=oc, n=n, p=p_val, k=k,
                status_summary=summary_txt,
                recommendations=result
            )

            # Store in session state for action buttons outside form
            st.session_state["latest_soil_result"] = {
                "id": rec_id,
                "farmer": farmer_name,
                "loc": field_location,
                "crop": target_crop,
                "result": result
            }

        # If we have an evaluation result in session state
        if "latest_soil_result" in st.session_state:
            latest = st.session_state["latest_soil_result"]
            res = latest["result"]

            st.markdown("<hr style='border:1px solid #E8F5E9; margin:1.2rem 0'>", unsafe_allow_html=True)
            st.markdown("### 📋 Soil Health Card Diagnostic Report")

            # Score and Grade Banner
            scol1, scol2, scol3 = st.columns(3)
            with scol1:
                render_metric("Soil Health Index", f"{res['health_score']} / 100", "Composite fertility score", "🌱")
            with scol2:
                render_metric("Fertility Grade", res['grade'].split('(')[0].strip(), res['grade'], "🏷️")
            with scol3:
                render_metric("Target Crop", latest['crop'], f"Field: {latest['loc']}", "🌾")

            # Parameter Rating Table
            render_section_header("Parameter Evaluation Breakdown", "📊")
            table_data = []
            for param, data in res["ratings"].items():
                table_data.append({
                    "Parameter": param.upper(),
                    "Tested Value": data["value"],
                    "Rating / Status": data["status"]
                })
            st.dataframe(pd.DataFrame(table_data), use_container_width=True)

            # Prescriptions
            render_section_header("Precision Fertilizer & Soil Amendment Schedule", "🌾")
            for p_rec in res["prescriptions"]:
                st.info(f"**{p_rec['parameter']} [{p_rec['status']}]:**\n\n{p_rec['recommendation']}")

            # Interactive Action Buttons
            act_col1, act_col2, _ = st.columns([1.5, 1.5, 2])
            with act_col1:
                if st.button("💬 Consult AI on Reclamation Plan", type="primary", use_container_width=True):
                    st.session_state["pending_query"] = (
                        f"I have a soil test report for my {latest['crop']} crop with pH {res['ratings']['ph']['value']} ({res['ratings']['ph']['status']}), "
                        f"EC {res['ratings']['ec']['value']}, Organic Carbon {res['ratings']['oc']['value']}%, "
                        f"N {res['ratings']['n']['value']} kg/ha, P {res['ratings']['p']['value']} kg/ha, and K {res['ratings']['k']['value']} kg/ha. "
                        f"Provide a comprehensive soil reclamation, green manuring, and fertilizer plan."
                    )
                    st.session_state["nav_selection"] = "💬 AI Assistant"
                    st.rerun()

            with act_col2:
                report_json = json.dumps(latest, indent=2, default=str)
                st.download_button(
                    "📥 Export Health Card (JSON)",
                    data=report_json,
                    file_name=f"soil_health_card_{latest['farmer'].replace(' ', '_')}.json",
                    mime="application/json",
                    use_container_width=True
                )

    with tab2:
        st.markdown("#### 📜 Recent Soil Test History")
        records = get_recent_soil_records(limit=25)
        if not records:
            st.info("No saved soil test records yet. Run an evaluation above to store historical cards.")
        else:
            hist_df = pd.DataFrame([{
                "Date": r["timestamp"],
                "Farmer": r["farmer_name"],
                "Location": r["field_location"],
                "Crop": r["target_crop"],
                "pH": r["ph"],
                "EC": r["ec"],
                "OC (%)": r["oc"],
                "N": r["n"],
                "P": r["p"],
                "K": r["k"],
                "Evaluation": r["status_summary"]
            } for r in records])
            st.dataframe(hist_df, use_container_width=True)
