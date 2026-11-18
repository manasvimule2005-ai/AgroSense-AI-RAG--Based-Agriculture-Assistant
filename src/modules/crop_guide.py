"""
AgroSense AI - Crop Advisory & Agronomy Directory
Provides structured retrieval, season/soil filtering, and critical irrigation advisory for staple crops.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from src.config import CROPS_CSV


class CropGuideManager:
    """Manages crop catalogue and agronomic recommendations."""

    def __init__(self, csv_path=CROPS_CSV):
        self.csv_path = csv_path
        self._df = None
        self._load_data()

    def _load_data(self):
        if self.csv_path.exists():
            self._df = pd.read_csv(self.csv_path)
        else:
            self._df = pd.DataFrame()

    def get_all_crops(self) -> List[Dict[str, Any]]:
        if self._df is None or self._df.empty:
            return []
        return self._df.to_dict(orient="records")

    def get_crop_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        if self._df is None or self._df.empty:
            return None
        matches = self._df[self._df["crop_name"].str.contains(name, case=False, na=False)]
        if not matches.empty:
            return matches.iloc[0].to_dict()
        return None

    def filter_crops(self, season: Optional[str] = None, category: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
        if self._df is None or self._df.empty:
            return []
        filtered = self._df.copy()
        if season and season != "All Seasons":
            filtered = filtered[filtered["season"].str.contains(season, case=False, na=False)]
        if category and category != "All Categories":
            filtered = filtered[filtered["category"].str.contains(category, case=False, na=False)]
        if query:
            q = query.lower()
            mask = (
                filtered["crop_name"].str.lower().str.contains(q, na=False) |
                filtered["soil_type"].str.lower().str.contains(q, na=False) |
                filtered["key_agronomy_tips"].str.lower().str.contains(q, na=False)
            )
            filtered = filtered[mask]
        return filtered.to_dict(orient="records")

    def get_seasons(self) -> List[str]:
        if self._df is None or self._df.empty:
            return []
        return ["All Seasons", "Kharif", "Rabi", "Zaid / Summer"]

    def get_categories(self) -> List[str]:
        if self._df is None or self._df.empty:
            return []
        cats = sorted(self._df["category"].dropna().unique().tolist())
        return ["All Categories"] + cats
