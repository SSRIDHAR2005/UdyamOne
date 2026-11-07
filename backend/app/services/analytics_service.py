import pandas as pd
from typing import Dict, Any, List, Optional
from pathlib import Path
from app.core.config import settings

class AnalyticsService:
    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or (settings.DATA_DIR / "smb_leads.csv")
        self._cache = {}
        self.load_analytics()

    def load_analytics(self):
        if not self.data_path.exists():
            return

        df = pd.read_csv(self.data_path)
        
        # Funnel counts
        total_leads = len(df)
        contacted = len(df[df["contacted_date"].notna()])
        needs_assessed = len(df[df["needs_assessed_date"].notna()])
        quote_accepted = len(df[df["quote_accepted_date"].notna()])
        kyc_complete = len(df[df["kyc_complete_date"].notna()])
        activated = len(df[df["outcome"] == "Activated"])

        # Segment distribution
        seg_counts = df["segment"].value_counts(normalize=True).to_dict()
        seg_act = df[df["outcome"] == "Activated"]["segment"].value_counts().to_dict()

        # GSTIN impact
        gstin_act = df[df["has_gstin"] == "Y"]["outcome"].value_counts(normalize=True).to_dict().get("Activated", 0) * 100
        non_gstin_act = df[df["has_gstin"] == "N"]["outcome"].value_counts(normalize=True).to_dict().get("Activated", 0) * 100

        # Drop reasons
        drop_reasons = df["drop_reason"].value_counts().head(8).to_dict()

        # Baseline metrics from case study
        activated_df = df[df["outcome"] == "Activated"]
        avg_days = float(round(activated_df["days_lead_to_activation"].mean(), 1)) if len(activated_df) else 17.6
        avg_chases = float(round(activated_df["customer_follow_up_calls"].mean(), 1)) if len(activated_df) else 3.0
        avg_cac = float(round(activated_df["acquisition_cost_inr"].mean(), 0)) if len(activated_df) else 15000.0
        avg_arpu = float(round(activated_df["monthly_bundle_value_inr"].mean(), 0)) if len(activated_df) else 6900.0

        self._cache = {
            "historical_funnel": {
                "total_leads": total_leads,
                "contacted": contacted,
                "needs_assessed": needs_assessed,
                "quote_accepted": quote_accepted,
                "kyc_complete": kyc_complete,
                "activated": activated,
                "conversion_rate_pct": round((activated / total_leads) * 100, 2)
            },
            "steepest_drop": {
                "stage_from": "Needs assessed",
                "stage_to": "Quote accepted",
                "drop_count": needs_assessed - quote_accepted,
                "drop_percentage": round(((needs_assessed - quote_accepted) / needs_assessed) * 100, 1),
                "primary_reasons": ["Price too high", "Quote too complex to understand", "Quote took too long to arrive"]
            },
            "segments": {
                "distribution": {k: round(v * 100, 1) for k, v in seg_counts.items()},
                "activations_by_segment": seg_act
            },
            "gstin_advantage": {
                "with_gstin_conversion_pct": round(gstin_act, 1),
                "without_gstin_conversion_pct": round(non_gstin_act, 1),
                "lift_multiplier": round(gstin_act / max(0.1, non_gstin_act), 1)
            },
            "top_drop_reasons": [{"reason": k, "count": int(v)} for k, v in drop_reasons.items()],
            "benchmarks": {
                "historical_baseline": {
                    "lead_to_activation_days": avg_days,
                    "customer_status_chases": avg_chases,
                    "cac_inr": avg_cac,
                    "arpu_monthly_inr": avg_arpu,
                    "conversion_rate_pct": 7.36
                },
                "udyamone_projected_target": {
                    "lead_to_activation_days": 4.5,
                    "customer_status_chases": 0.3,
                    "cac_inr": 4800.0,
                    "arpu_monthly_inr": 7200.0,
                    "conversion_rate_pct": 24.5
                }
            }
        }

    def get_funnel_and_kpis(self) -> Dict[str, Any]:
        return self._cache

analytics_service = AnalyticsService()

