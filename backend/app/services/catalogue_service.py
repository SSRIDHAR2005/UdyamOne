import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.core.config import settings

class CatalogueService:
    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or (settings.DATA_DIR / "product_catalogue.csv")
        self.products: Dict[str, Dict[str, Any]] = {}
        self.load_catalogue()

    def load_catalogue(self):
        self.products.clear()
        if not self.data_path.exists():
            raise FileNotFoundError(f"Catalogue file not found at {self.data_path}")

        with open(self.data_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = row["product_id"].strip()
                city_tiers = [int(t.strip()) for t in row["available_city_tiers"].split(";") if t.strip()]
                requires_one_of = [p.strip() for p in row["requires_one_of"].split("|") if p.strip()] if row.get("requires_one_of") else []
                target_segs = [s.strip() for s in row["target_segments"].split(";") if s.strip()]

                self.products[pid] = {
                    "product_id": pid,
                    "category": row["category"].strip(),
                    "product_name": row["product_name"].strip(),
                    "description": row["description"].strip(),
                    "unit": row["unit"].strip(),
                    "price_min_inr_per_month": float(row["price_min_inr_per_month"]),
                    "price_max_inr_per_month": float(row["price_max_inr_per_month"]),
                    "price_inr_per_month": float(row["price_min_inr_per_month"]),  # baseline standard
                    "one_time_setup_inr": float(row["one_time_setup_inr"]),
                    "min_contract_months": int(row["min_contract_months"]),
                    "available_city_tiers": city_tiers,
                    "min_employees": int(row["min_employees"]),
                    "min_sites": int(row["min_sites"]),
                    "requires_gstin": row["requires_gstin"].strip().upper() == "Y",
                    "requires_one_of": requires_one_of,
                    "typical_install_days": int(row["typical_install_days"]),
                    "target_segments": target_segs
                }

    def get_all_products(self) -> List[Dict[str, Any]]:
        return list(self.products.values())

    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        return self.products.get(product_id)

    def check_eligibility(
        self,
        product_id: str,
        city_tier: int,
        employee_count: int,
        num_sites: int,
        has_gstin: bool,
        selected_product_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        p = self.get_product(product_id)
        if not p:
            return {"eligible": False, "reasons": ["Product does not exist in catalogue"]}

        reasons = []
        # Check tier
        if city_tier not in p["available_city_tiers"]:
            reasons.append(f"Not available in City Tier {city_tier} (Available in Tier: {p['available_city_tiers']})")

        # Check employee count
        if employee_count < p["min_employees"]:
            reasons.append(f"Requires minimum {p['min_employees']} employees (Business has {employee_count})")

        # Check site count
        if num_sites < p["min_sites"]:
            reasons.append(f"Requires minimum {p['min_sites']} sites (Business has {num_sites})")

        # Check GSTIN requirement
        if p["requires_gstin"] and not has_gstin:
            reasons.append(f"Requires valid, active GSTIN ({p['product_name']} is restricted to tax-registered enterprises)")

        # Check dependencies
        if p["requires_one_of"] and selected_product_ids is not None:
            has_dep = any(dep in selected_product_ids for dep in p["requires_one_of"])
            if not has_dep:
                dep_names = [self.get_product(d)["product_name"] if self.get_product(d) else d for d in p["requires_one_of"]]
                reasons.append(f"Requires one of prerequisite connectivity links: {', '.join(dep_names)}")

        return {
            "eligible": len(reasons) == 0,
            "reasons": reasons
        }

catalogue_service = CatalogueService()

