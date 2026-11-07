import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from app.core.config import settings

class LeadScoringService:
    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or (settings.DATA_DIR / "smb_leads.csv")
        self.model = None
        self.feature_names = []
        self.metrics = {}
        self.train_baseline_model()

    def train_baseline_model(self):
        if not self.data_path.exists():
            return

        df = pd.read_csv(self.data_path)
        
        # Target: Activated (1) vs Dropped (0)
        y = (df["outcome"] == "Activated").astype(int)

        # STRICTLY PRE-CONVERSION FEATURES ONLY (Prevent Data Leakage)
        features = pd.DataFrame()
        features["is_tier_1"] = (df["city_tier"] == 1).astype(int)
        features["employee_count"] = df["employee_count"].fillna(1)
        features["num_sites"] = df["num_sites"].fillna(1)
        features["has_gstin"] = (df["has_gstin"] == "Y").astype(int)
        features["has_udyam"] = (df["has_udyam"] == "Y").astype(int)
        features["monthly_spend"] = df["monthly_telecom_spend_inr"].fillna(1500)

        # Lead source encoding
        for src in df["lead_source"].unique():
            features[f"src_{src}"] = (df["lead_source"] == src).astype(int)

        # Segment encoding (handling both short keys and full dataset strings)
        for seg in df["segment"].unique():
            features[f"seg_{seg}"] = (df["segment"] == seg).astype(int)

        # Current internet
        for ci in df["current_internet"].dropna().unique():
            features[f"ci_{ci}"] = (df["current_internet"] == ci).astype(int)

        self.feature_names = list(features.columns)

        X_train, X_test, y_train, y_test = train_test_split(
            features, y, test_size=0.25, random_state=42, stratify=y
        )

        clf = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            class_weight="balanced",
            random_state=42
        )
        clf.fit(X_train, y_train)
        self.model = clf

        y_pred = clf.predict(X_test)
        y_prob = clf.predict_proba(X_test)[:, 1]

        self.metrics = {
            "total_samples": len(df),
            "activation_rate_baseline": float(round(y.mean() * 100, 2)),
            "precision": float(round(precision_score(y_test, y_pred, zero_division=0), 3)),
            "recall": float(round(recall_score(y_test, y_pred), 3)),
            "f1_score": float(round(f1_score(y_test, y_pred), 3)),
            "roc_auc": float(round(roc_auc_score(y_test, y_prob), 3)),
            "model_type": "RandomForestClassifier (Pre-conversion features strictly, zero leakage)"
        }

    def predict_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        if self.model is None:
            return {"priority": "MEDIUM", "score": 50, "factors": ["Default heuristic"], "recommended_action": "Standard partner follow-up"}

        row = {f: 0 for f in self.feature_names}
        row["is_tier_1"] = 1 if lead_data.get("city_tier") == 1 else 0
        row["employee_count"] = float(lead_data.get("employee_count", 1))
        row["num_sites"] = float(lead_data.get("num_sites", 1))
        row["has_gstin"] = 1 if lead_data.get("has_gstin") in [True, "Y", "y", 1] else 0
        row["has_udyam"] = 1 if lead_data.get("has_udyam") in [True, "Y", "y", 1] else 0
        row["monthly_spend"] = float(lead_data.get("monthly_telecom_spend_inr", 1500))

        lead_src = lead_data.get("lead_source", "Website form")
        for col in self.feature_names:
            if col.startswith("src_") and col == f"src_{lead_src}":
                row[col] = 1

        seg = str(lead_data.get("segment", "micro")).lower()
        # Match segment variants
        for col in self.feature_names:
            if col.startswith("seg_"):
                if seg in col.lower():
                    row[col] = 1

        X = pd.DataFrame([row])[self.feature_names]
        prob = float(self.model.predict_proba(X)[0][1])
        score = int(prob * 100)

        # Risk and Priority
        if score >= 55:
            priority = "HIGH"
        elif score >= 35:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        factors = []
        if row["has_gstin"] == 1:
            factors.append("GSTIN available (Historical 9.6% conversion vs 2.0% without)")
        else:
            factors.append("Missing GSTIN documentation (4.8× drop-off risk at quote/KYC)")

        if row["monthly_spend"] >= 3000:
            factors.append("High current telecom spend indicates high budget fit")
        elif row["monthly_spend"] < 1000:
            factors.append("Low budget sensitivity requires affordable Essential bundle")

        if row["num_sites"] > 1:
            factors.append("Multi-site complexity requires central account manager")

        drop = str(lead_data.get("drop_reason", ""))
        stage = str(lead_data.get("stage_reached", "Lead"))

        if not row["has_gstin"]:
            action = "Offer guided Udyam/GST registration support or consumer-to-business transition"
        elif stage == "Needs assessed" or "quote" in drop.lower() or "price" in drop.lower():
            action = "Send instant digital quote with custom add-on toggle and flexible tenure"
        elif stage == "KYC complete" or "install" in drop.lower():
            action = "Fast-track last-mile fiber survey and dispatch appointment reminder"
        elif row["num_sites"] > 1:
            action = "Assign enterprise field relationship manager for multi-site feasibility"
        else:
            action = "Dispatch WhatsApp self-service bundle selection link"

        return {
            "lead_id": lead_data.get("lead_id"),
            "conversion_probability": round(prob, 3),
            "lead_score": score,
            "lead_priority": priority,
            "key_factors": factors,
            "recommended_next_action": action,
            "model_metadata": self.metrics
        }

lead_scoring_service = LeadScoringService()
