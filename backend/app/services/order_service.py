import uuid
import datetime
from zoneinfo import ZoneInfo
from typing import Dict, Any, List, Optional
from app.core.config import settings

STAGES = [
    {"stage": "PLACED", "label": "Order Placed", "desc": "Order registered and initial verification commenced."},
    {"stage": "KYC_VERIFIED", "label": "KYC Verified", "desc": "Identity, GSTIN, and business address verified digitally."},
    {"stage": "CONFIRMED", "label": "Order Confirmed", "desc": "Commercial and technical booking sign-off complete."},
    {"stage": "FEASIBILITY_CHECKED", "label": "Network Feasibility", "desc": "Local distribution point & fiber loop capacity confirmed."},
    {"stage": "INSTALLATION_SCHEDULED", "label": "Installation Scheduled", "desc": "Dedicated technician appointment fixed with store manager."},
    {"stage": "INSTALLATION_IN_PROGRESS", "label": "Installation In Progress", "desc": "CPE deployment, router provisioning and line testing in progress."},
    {"stage": "ACTIVATED", "label": "Activation Completed", "desc": "Service live, SLA monitoring enabled, invoice dispatch scheduled."}
]

class OrderService:
    def __init__(self):
        # In-memory store alongside database
        self.orders: Dict[str, Dict[str, Any]] = {}
        self._init_demo_orders()

    def _init_demo_orders(self):
        # Seed an explicitly labeled demonstration order using dates relative
        # to the current local time; it is not presented as a customer record.
        demo_id = "ORD-2026-88219"
        ref_today = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
        day = datetime.timedelta(days=1)
        start = ref_today - 2 * day
        self.orders[demo_id] = {
            "order_id": demo_id,
            "order_number": demo_id,
            "created_at": start.isoformat(),
            "updated_at": ref_today.isoformat(),
            "quote_id": "UDY-QUO-2026-DEMO01",
            "business_name": "Saffron Bakers",
            "contact_name": "Sneha Rao",
            "contact_phone": "+91 98765 43210",
            "contact_email": "orders@saffronbakers.in",
            "installation_address": "Shop 83, Market Yard, Ludhiana, Punjab - 416059",
            "installation_address_source": "DEMO_SAMPLE",
            "city": "Ludhiana",
            "pincode": "416059",
            "monthly_amount_inr": 3195.0,
            "setup_charges_inr": 2500.0,
            "num_sites": 1,
            "items_summary": [
                {"name": "Biz Fibre 100", "qty": 1, "monthly": 999.0},
                {"name": "Business Postpaid 299", "qty": 2, "monthly": 598.0},
                {"name": "Cloud POS & Billing", "qty": 1, "monthly": 599.0},
                {"name": "WhatsApp Business API", "qty": 1, "monthly": 999.0}
            ],
            "current_status": "INSTALLATION_SCHEDULED",
            "status_history": [
                {"stage": "PLACED", "timestamp": start.isoformat(), "completed": True, "note": "Sample order placed in the UdyamOne demo tracker."},
                {"stage": "KYC_VERIFIED", "timestamp": (start + datetime.timedelta(minutes=5)).isoformat(), "completed": True, "note": "Sample KYC stage completed for demonstration."},
                {"stage": "CONFIRMED", "timestamp": (start + datetime.timedelta(hours=4)).isoformat(), "completed": True, "note": "Sample commercial booking confirmed."},
                {"stage": "FEASIBILITY_CHECKED", "timestamp": (ref_today - day).isoformat(), "completed": True, "note": "Sample network feasibility stage completed."},
                {"stage": "INSTALLATION_SCHEDULED", "timestamp": ref_today.isoformat(), "completed": True, "note": f"Sample appointment scheduled for {(ref_today + day).strftime('%d %b %Y')} (demo data)."},
                {"stage": "INSTALLATION_IN_PROGRESS", "timestamp": None, "completed": False, "note": "Awaiting the sample technician visit."},
                {"stage": "ACTIVATED", "timestamp": None, "completed": False, "note": "Activation is pending in this demonstration order."}
            ],
            "assigned_technician": "Ramesh Verma (Senior Fiber Specialist)",
            "technician_contact": "+91 98112 00445",
            "estimated_activation_date": (ref_today + datetime.timedelta(days=2)).isoformat(),
            "confirmed_appointment_date": (ref_today + day).isoformat(),
            "activated_at": None,
            "is_demo": True,
            "delay_alert": None,
            "notifications": [
                {"timestamp": (start + datetime.timedelta(minutes=6)).isoformat(), "channel": "SMS", "message": f"Sample order {demo_id} is confirmed in the demonstration tracker."},
                {"timestamp": ref_today.isoformat(), "channel": "WhatsApp", "message": f"Sample technician visit scheduled for {(ref_today + day).strftime('%d %b %Y')} (demo data)."}
            ]
        }

    def create_order(
        self,
        quote_data: Dict[str, Any],
        kyc_id: Optional[str],
        customer_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        now_dt = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
        order_num = f"ORD-{now_dt.year}-{uuid.uuid4().hex[:6].upper()}"
        
        # Calculate install days from quote items
        install_days = []
        items_summary = []
        for it in quote_data.get("items", []):
            items_summary.append({
                "name": it.get("product_name"),
                "qty": it.get("quantity", 1),
                "monthly": it.get("total_monthly_inr", 0)
            })
            days = it.get("typical_install_days", 5)
            if isinstance(days, (int, float)) and days > 0:
                install_days.append(int(days))

        max_install_days = max(install_days, default=5)
        est_act = now_dt + datetime.timedelta(days=max_install_days)

        history = []
        for s in STAGES:
            is_first = s["stage"] == "PLACED"
            is_kyc = s["stage"] == "KYC_VERIFIED" and kyc_id is not None
            completed = is_first or is_kyc
            ts = now_dt.isoformat() if completed else None
            note = "Digital checkout completed." if is_first else ("Instant automated KYC validated." if is_kyc else s["desc"])
            history.append({
                "stage": s["stage"],
                "timestamp": ts,
                "completed": completed,
                "note": note
            })

        order_obj = {
            "order_id": order_num,
            "order_number": order_num,
            "created_at": now_dt.isoformat(),
            "updated_at": now_dt.isoformat(),
            "quote_id": quote_data.get("quote_id", "MANUAL-QUOTE"),
            "kyc_id": kyc_id,
            "business_name": customer_info.get("business_name", quote_data.get("business_name")),
            "contact_name": customer_info.get("contact_name", "Business Owner"),
            "contact_phone": customer_info.get("contact_phone", "+91 98765 00000"),
            "contact_email": customer_info.get("contact_email", "contact@business.com"),
            "installation_address": customer_info.get("installation_address", "Registered Office"),
            "installation_address_source": customer_info.get("installation_address_source", "CUSTOMER_PROVIDED"),
            "city": customer_info.get("city", quote_data.get("city", "Bengaluru")),
            "pincode": customer_info.get("pincode", "560001"),
            "num_sites": int(quote_data.get("num_sites", 1)),
            "monthly_amount_inr": quote_data.get("monthly_recurring_inr", 1500.0),
            "setup_charges_inr": quote_data.get("one_time_setup_inr", 0.0),
            "items_summary": items_summary,
            "current_status": "KYC_VERIFIED" if kyc_id else "PLACED",
            "status_history": history,
            "assigned_technician": "Airtel Enterprise Field Unit 4",
            "technician_contact": "+91 1800-103-4444",
            "estimated_activation_date": est_act.isoformat(),
            "confirmed_appointment_date": None,
            "activated_at": None,
            "is_demo": False,
            "delay_alert": None,
            "notifications": [
                {"timestamp": now_dt.isoformat(), "channel": "SMS", "message": f"Accel Business: Order {order_num} successfully placed! Track status at udyamone.airtel.in"}
            ]
        }

        self.orders[order_num] = order_obj
        return order_obj

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        return self.orders.get(order_id)

    def update_order_status(self, order_id: str, new_stage: str, note: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if order_id not in self.orders:
            return None
        
        order = self.orders[order_id]
        order["current_status"] = new_stage
        order["updated_at"] = datetime.datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
        
        # Update history
        stage_idx = -1
        for i, s in enumerate(order["status_history"]):
            if s["stage"] == new_stage:
                stage_idx = i
                break
        
        if stage_idx != -1:
            for j in range(len(order["status_history"])):
                if j <= stage_idx:
                    order["status_history"][j]["completed"] = True
                    if not order["status_history"][j]["timestamp"]:
                        order["status_history"][j]["timestamp"] = datetime.datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
                else:
                    order["status_history"][j]["completed"] = False

            if note:
                order["status_history"][stage_idx]["note"] = note

        if new_stage == "ACTIVATED":
            order["activated_at"] = datetime.datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
            order["delay_alert"] = None
            order["notifications"].append({
                "timestamp": order["activated_at"],
                "channel": "WhatsApp",
                "message": f"Congratulations! Your business connectivity & cloud bundle is now ACTIVE."
            })

        return order

order_service = OrderService()

