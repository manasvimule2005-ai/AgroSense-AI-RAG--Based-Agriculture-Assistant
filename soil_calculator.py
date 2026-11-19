"""
AgroSense AI - Soil Health Card Evaluator & Dosage Calculator
Implements standard ICAR and FAO rating benchmarks for chemical and physical soil parameters.
"""

from typing import Dict, Any, List


class SoilHealthEvaluator:
    """Evaluates Soil Health Card parameters and generates precision fertilizer/amendment schedules."""

    @staticmethod
    def evaluate(
        ph: float,
        ec: float,
        oc: float,
        n: float,
        p: float,
        k: float,
        zn: float = 0.8,
        s: float = 12.0,
        target_crop: str = "General"
    ) -> Dict[str, Any]:
        """Calculates ratings, overall health score (0-100), and tailored agronomic prescriptions."""

        ratings = {}
        prescriptions: List[Dict[str, str]] = []
        score = 100

        # 1. pH Evaluation
        if ph < 6.0:
            status = "Acidic (Deficient)"
            color = "red"
            action = "Apply agricultural lime (CaCO3) @ 2-4 tonnes/ha during land preparation to neutralize acidity and unlock bound phosphorus."
            score -= 15
        elif 6.0 <= ph <= 6.4:
            status = "Slightly Acidic"
            color = "orange"
            action = "Incorporate well-decomposed organic matter/FYM and avoid acid-forming fertilizers like ammonium sulphate."
            score -= 5
        elif 6.5 <= ph <= 7.8:
            status = "Optimal / Neutral"
            color = "green"
            action = "Soil pH is ideal for most nutrient absorption. Maintain with regular balanced organic inputs."
        elif 7.9 <= ph <= 8.5:
            status = "Moderately Alkaline"
            color = "orange"
            action = "Apply organic mulch and acidifying organic manures (FYM 10 t/ha). Monitor iron and zinc availability."
            score -= 5
        else:
            status = "Sodic / Highly Alkaline"
            color = "red"
            action = "Incorporate Agricultural Gypsum (CaSO4·2H2O) @ 3-5 tonnes/ha followed by ponding and leaching. Green manure with Dhaincha (Sesbania)."
            score -= 20
        ratings["ph"] = {"value": ph, "status": status, "color": color}
        prescriptions.append({"parameter": "Soil Reaction (pH)", "status": status, "recommendation": action})

        # 2. Electrical Conductivity (EC - Salinity)
        if ec < 1.0:
            status = "Normal (Non-saline)"
            color = "green"
            action = "Safe for germination and root development of all standard field crops."
        elif 1.0 <= ec <= 2.0:
            status = "Slightly Saline"
            color = "orange"
            action = "Slight yield impact on salt-sensitive crops. Improve drainage and use furrow/raised bed planting."
            score -= 10
        else:
            status = "Saline (Injurious)"
            color = "red"
            action = "High soluble salts! Perform deep leaching with quality freshwater and establish sub-surface drainage. Grow salt-tolerant varieties."
            score -= 20
        ratings["ec"] = {"value": ec, "status": status, "color": color}
        prescriptions.append({"parameter": "Electrical Conductivity (EC)", "status": status, "recommendation": action})

        # 3. Organic Carbon (OC)
        if oc < 0.50:
            status = "Low (Deficient)"
            color = "red"
            action = "Apply Farmyard Manure (FYM) @ 10-15 tonnes/ha or Vermicompost @ 2.5 t/ha. Practice green manuring with Sunnhemp or Dhaincha."
            score -= 15
        elif 0.50 <= oc <= 0.75:
            status = "Medium (Adequate)"
            color = "orange"
            action = "Maintain organic matter by retaining crop residues and applying 5-7 tonnes FYM/ha annually."
        else:
            status = "High (Optimal)"
            color = "green"
            action = "Excellent organic carbon reservoir supporting beneficial soil microbes and high moisture retention."
        ratings["oc"] = {"value": oc, "status": status, "color": color}
        prescriptions.append({"parameter": "Organic Carbon (OC)", "status": status, "recommendation": action})

        # 4. Available Nitrogen (N)
        if n < 280:
            status = "Low (Deficient)"
            color = "red"
            action = "Increase baseline nitrogen recommendation by 25%. Split urea into 3 applications (basal, tillering, panicle/flowering). Inoculate with Azotobacter/Rhizobium."
            score -= 15
        elif 280 <= n <= 560:
            status = "Medium (Optimal)"
            color = "green"
            action = "Follow recommended fertilizer doses for target crop in split applications."
        else:
            status = "High (Excessive)"
            color = "blue"
            action = "Reduce chemical nitrogen dose by 25% to avoid lodging, pest susceptibility, and groundwater nitrate leaching."
            score -= 5
        ratings["n"] = {"value": n, "status": status, "color": color}
        prescriptions.append({"parameter": "Available Nitrogen (N)", "status": status, "recommendation": action})

        # 5. Available Phosphorus (P2O5)
        if p < 23:
            status = "Low (Deficient)"
            color = "red"
            action = "Apply Single Super Phosphate (SSP) or DAP as basal dose. Treat seeds with Phosphate Solubilizing Bacteria (PSB) @ 10g/kg."
            score -= 10
        elif 23 <= p <= 56:
            status = "Medium (Optimal)"
            color = "green"
            action = "Maintain standard basal phosphorus schedule."
        else:
            status = "High (Excessive)"
            color = "blue"
            action = "Withhold additional phosphate fertilizer for this crop season to prevent zinc and iron antagonism."
        ratings["p"] = {"value": p, "status": status, "color": color}
        prescriptions.append({"parameter": "Available Phosphorus (P)", "status": status, "recommendation": action})

        # 6. Available Potassium (K2O)
        if k < 144:
            status = "Low (Deficient)"
            color = "red"
            action = "Apply Muriate of Potash (MOP / KCl) @ 40-60 kg/ha in 2 splits to enhance drought tolerance and disease resistance."
            score -= 10
        elif 144 <= k <= 336:
            status = "Medium (Optimal)"
            color = "green"
            action = "Apply maintenance dosage of potassium as per crop recommendation."
        else:
            status = "High (Excessive)"
            color = "blue"
            action = "No supplementary potash needed; existing soil reserve is sufficient."
        ratings["k"] = {"value": k, "status": status, "color": color}
        prescriptions.append({"parameter": "Available Potassium (K)", "status": status, "recommendation": action})

        # 7. Micronutrients: Zinc (Zn) and Sulfur (S)
        if zn < 0.60:
            status_zn = "Deficient"
            prescriptions.append({
                "parameter": "Zinc (Zn)",
                "status": status_zn,
                "recommendation": "Soil application of Zinc Sulphate (ZnSO4·7H2O) @ 25 kg/ha or foliar spray of 0.5% ZnSO4 + 0.25% lime at active tillering."
            })
            score -= 5
        else:
            status_zn = "Adequate"

        if s < 10.0:
            status_s = "Deficient"
            prescriptions.append({
                "parameter": "Sulfur (S)",
                "status": status_s,
                "recommendation": "Apply Bentonite Sulfur or Gypsum @ 20-25 kg S/ha, especially critical for oilseeds, pulses, and mustard."
            })
            score -= 5
        else:
            status_s = "Adequate"

        ratings["zn"] = {"value": zn, "status": status_zn, "color": "red" if status_zn == "Deficient" else "green"}
        ratings["s"] = {"value": s, "status": status_s, "color": "red" if status_s == "Deficient" else "green"}

        final_score = max(20, min(100, score))
        if final_score >= 80:
            grade = "A (High Fertility & Health)"
            badge_color = "#2E7D32"
        elif final_score >= 60:
            grade = "B (Moderate Fertility - Minor Deficiencies)"
            badge_color = "#F57C00"
        else:
            grade = "C (Degraded / Significant Deficiencies)"
            badge_color = "#D32F2F"

        return {
            "health_score": final_score,
            "grade": grade,
            "badge_color": badge_color,
            "ratings": ratings,
            "prescriptions": prescriptions,
            "target_crop": target_crop
        }
