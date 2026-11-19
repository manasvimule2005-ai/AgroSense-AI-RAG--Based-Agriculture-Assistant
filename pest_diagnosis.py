"""
AgroSense AI - Pest & Disease Diagnostic Engine
Provides symptom-based identification, severity ratings, and Integrated Pest Management (IPM) protocols.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from src.config import PESTS_CSV


class PestDiagnosisManager:
    """Diagnoses agricultural plant pests and diseases from symptoms."""

    def __init__(self, csv_path=PESTS_CSV):
        self.csv_path = csv_path
        self._df = None
        self._load_data()

    def _load_data(self):
        if self.csv_path.exists():
            self._df = pd.read_csv(self.csv_path)
        else:
            self._df = pd.DataFrame()

    def get_all_pests(self) -> List[Dict[str, Any]]:
        if self._df is None or self._df.empty:
            return []
        return self._df.to_dict(orient="records")

    def diagnose(self, crop: Optional[str] = None, symptom_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Matches reported symptoms and/or selected crop to pest/disease records with relevance scoring."""
        if self._df is None or self._df.empty:
            return []

        results = []
        query_words = set(symptom_query.lower().split()) if symptom_query else set()

        for _, row in self._df.iterrows():
            score = 0
            rec = row.to_dict()

            # Crop matching bonus
            affected_crops = str(rec.get("affected_crops", "")).lower()
            if crop and crop != "All Crops":
                if crop.lower() in affected_crops:
                    score += 5
                else:
                    # If a specific crop was picked and this pest doesn't affect it, deprioritize
                    if symptom_query:
                        score -= 2
                    else:
                        continue

            # Symptom query matching
            if query_words:
                symptoms_text = str(rec.get("symptoms", "")).lower()
                name_text = str(rec.get("name", "")).lower()
                combined_text = f"{symptoms_text} {name_text}"

                matched_keywords = []
                for word in query_words:
                    if len(word) > 2 and word in combined_text:
                        score += 3
                        matched_keywords.append(word)

                rec["matched_keywords"] = matched_keywords
                if score <= 0 and crop == "All Crops":
                    continue
            else:
                score += 1

            rec["relevance_score"] = score
            results.append(rec)

        # Sort descending by relevance score
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return results

    def get_crop_list(self) -> List[str]:
        if self._df is None or self._df.empty:
            return ["All Crops"]
        crops = set()
        for c in self._df["affected_crops"].dropna():
            for item in c.split(","):
                clean = item.strip()
                if clean:
                    crops.add(clean)
        return ["All Crops"] + sorted(list(crops))
