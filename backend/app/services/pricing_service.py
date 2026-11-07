import uuid
import datetime
from typing import List, Dict, Any, Tuple, Optional
from app.services.catalogue_service import catalogue_service
from app.schemas.domain import ProductSelection

class PricingService:
    def __init__(self):
        self.quotes: Dict[str, Any] = {}

    def get_quote(self, quote_id: str) -> Optional[Dict[str, Any]]:
        return self.quotes.get(quote_id)

    def calculate_quote(
        self,
        business_details: Dict[str, Any],
        selected_products: List[ProductSelection],
        tier_name: str = "Custom"
    ) -> Dict[str, Any]:
        """
        Calculates quote totals strictly adhering to product_catalogue.csv.
        Total Monthly Cost = Sum of (product.price_inr_per_month * quantity)
        Total Initial Cost = Sum of (product.one_time_setup_inr * quantity)
        """
        product_ids = [sp.product_id for sp in selected_products]
        city_tier = int(business_details.get("city_tier", 1))
        employees = int(business_details.get("employee_count", 1))
        sites = int(business_details.get("num_sites", 1))
        has_gstin = bool(business_details.get("has_gstin", False))

        line_items = []
        total_monthly_recurring = 0.0
        total_one_time_setup = 0.0
        max_contract_months = 1
        standalone_total = 0.0
        validation_warnings = []

        # Deduplicate and group by product_id
        grouped: Dict[str, ProductSelection] = {}
        for sp in selected_products:
            if sp.product_id in grouped:
                grouped[sp.product_id].quantity += sp.quantity
            else:
                grouped[sp.product_id] = ProductSelection(
                    product_id=sp.product_id,
                    quantity=sp.quantity,
                    is_addon=sp.is_addon
                )

        for pid, sel in grouped.items():
            product = catalogue_service.get_product(pid)
            if not product:
                validation_warnings.append(f"Product {pid} not found in official catalogue.")
                continue

            # Check eligibility
            elig = catalogue_service.check_eligibility(
                product_id=pid,
                city_tier=city_tier,
                employee_count=employees,
                num_sites=sites,
                has_gstin=has_gstin,
                selected_product_ids=list(grouped.keys())
            )

            if not elig["eligible"]:
                for r in elig["reasons"]:
                    validation_warnings.append(f"{product['product_name']}: {r}")

            unit_price = product["price_inr_per_month"]
            unit_setup = product["one_time_setup_inr"]
            max_price = product["price_max_inr_per_month"]
            
            # Monthly cost for this item
            item_monthly = unit_price * sel.quantity
            item_setup = unit_setup * (sites if "per site" in product["unit"] else 1)
            
            total_monthly_recurring += item_monthly
            total_one_time_setup += item_setup
            standalone_total += max_price * sel.quantity

            if product["min_contract_months"] > max_contract_months:
                max_contract_months = product["min_contract_months"]

            line_items.append({
                "product_id": pid,
                "product_name": product["product_name"],
                "category": product["category"],
                "description": product["description"],
                "unit": product["unit"],
                "quantity": sel.quantity,
                "unit_price_monthly_inr": unit_price,
                "unit_setup_inr": unit_setup,
                "total_monthly_inr": item_monthly,
                "total_setup_inr": item_setup,
                "contract_months": product["min_contract_months"],
                "typical_install_days": product["typical_install_days"],
                "is_addon": sel.is_addon,
                "is_eligible": elig["eligible"],
                "eligibility_reasons": elig["reasons"]
            })

        # Calculate Bundle Savings vs Standalone Maximums
        savings_inr = max(0.0, standalone_total - total_monthly_recurring)
        
        # Configurable GST calculation (assumed 18% standard telecom baseline)
        custom_tax = business_details.get("custom_gst_percent")
        gst_percent = float(custom_tax) if custom_tax is not None else 18.0
        gst_amount_monthly = round((total_monthly_recurring * gst_percent) / 100.0, 2)
        gst_amount_setup = round((total_one_time_setup * gst_percent) / 100.0, 2)
        total_first_month = total_monthly_recurring + gst_amount_monthly + total_one_time_setup + gst_amount_setup

        # Dates
        created_dt = datetime.datetime.strptime("2026-07-15T10:00:00", "%Y-%m-%dT%H:%M:%S")
        expires_dt = created_dt + datetime.timedelta(days=14)
        quote_id = f"UDY-QUO-2026-{uuid.uuid4().hex[:6].upper()}"

        terms = [
            f"Official quote generated under Accel Business SMB Plan Rules for {business_details.get('business_name', 'Client')}.",
            f"Commitment tenure: {max_contract_months} months with guaranteed SLA per product line.",
            "Recurring billing commences post successful installation and activation sign-off.",
            f"Configurable statutory tax assumption applied: GST @ {gst_percent}% (SAC 9984 baseline for telecom connectivity). Verified product-specific tax treatment (e.g. 0% pure software export or 12% standalone hardware) is finalized at ERP invoice creation.",
            "Valid for 14 days from issuance subject to local loop line feasibility confirmation."
        ]

        res = {
            "quote_id": quote_id,
            "created_at": created_dt.isoformat(),
            "expires_at": expires_dt.isoformat(),
            "business_name": business_details.get("business_name", "Valued Enterprise"),
            "segment": business_details.get("segment", "micro"),
            "city": business_details.get("city", "Bengaluru"),
            "city_tier": city_tier,
            "tier_name": tier_name,
            "items": line_items,
            "monthly_recurring_inr": round(total_monthly_recurring, 2),
            "one_time_setup_inr": round(total_one_time_setup, 2),
            "calculated_savings_inr": round(savings_inr, 2),
            "applicable_gst_percent": gst_percent,
            "applicable_gst_amount_monthly": gst_amount_monthly,
            "applicable_gst_amount_setup": gst_amount_setup,
            "tax_treatment": "assumed_standard_telecom_gst",
            "tax_disclosure": "Assumed statutory rate of 18% GST (CGST 9% + SGST 9% or IGST 18%). Verified tax treatment depends on specific product HSN/SAC codes at ERP billing.",
            "hsn_sac_category": "SAC 9984 (Telecommunications & Internet Services)",
            "total_first_month_inr": round(total_first_month, 2),
            "contract_months": max_contract_months,
            "validation_warnings": validation_warnings,
            "terms_and_conditions": terms
        }
        self.quotes[quote_id] = res
        return res

pricing_service = PricingService()

