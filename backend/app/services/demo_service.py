from typing import Dict, Any, List

DEMO_SCENARIOS = [
    {
        "id": "scenario-kirana",
        "name": "Kirana Store (Micro Retail)",
        "business_name": "Ramesh Provision Store",
        "business_type": "retail",
        "segment": "micro",
        "city": "Jaipur",
        "city_tier": 2,
        "pincode": "302001",
        "employee_count": 3,
        "num_sites": 1,
        "monthly_budget_inr": 1800,
        "has_gstin": False,
        "gstin": None,
        "need_sims": 1,
        "need_pos": True,
        "need_whatsapp": True,
        "need_cctv": False,
        "need_cloud_email": False,
        "need_security": False,
        "need_failover_backup": False,
        "need_dedicated_leased_line": False,
        "preferred_language": "hi",
        "story": "High price sensitivity, needs stable connectivity for UPI payments, customer WhatsApp updates, and low entry barrier without complex paperwork."
    },
    {
        "id": "scenario-clinic",
        "name": "Polyclinic & CA Office (Professional Office)",
        "business_name": "Dr. Meera Diagnostic & Dental Clinic",
        "business_type": "clinic",
        "segment": "prof",
        "city": "Bengaluru",
        "city_tier": 1,
        "pincode": "560034",
        "employee_count": 8,
        "num_sites": 1,
        "monthly_budget_inr": 4500,
        "has_gstin": True,
        "gstin": "29CPSXS6426Z1ZL",
        "need_sims": 3,
        "need_pos": True,
        "need_whatsapp": True,
        "need_cctv": True,
        "cctv_cameras_count": 3,
        "need_cloud_email": True,
        "need_cloud_backup": True,
        "need_security": True,
        "need_failover_backup": False,
        "need_dedicated_leased_line": False,
        "preferred_language": "en",
        "story": "Requires high uptime, cloud backup of patient dental X-rays, secure domain email, and endpoint protection for patient data privacy."
    },
    {
        "id": "scenario-restaurant",
        "name": "3-Location Restaurant Chain (Multi-site)",
        "business_name": "Spice Route Kitchens",
        "business_type": "restaurant",
        "segment": "multi",
        "city": "Chennai",
        "city_tier": 1,
        "pincode": "600004",
        "employee_count": 22,
        "num_sites": 3,
        "monthly_budget_inr": 12000,
        "has_gstin": True,
        "gstin": "33MFTXS9954Q1Z9",
        "need_sims": 6,
        "need_pos": True,
        "need_whatsapp": True,
        "need_cctv": True,
        "cctv_cameras_count": 6,
        "need_cloud_email": True,
        "need_cloud_backup": False,
        "need_security": True,
        "need_failover_backup": True,
        "need_dedicated_leased_line": False,
        "preferred_language": "ta",
        "story": "Needs centralized billing across 3 outlets, automatic 4G/5G failover when primary fiber drops, and live CCTV streaming on owner's phone."
    },
    {
        "id": "scenario-manufacturer",
        "name": "Auto Parts Manufacturer (Small Industry)",
        "business_name": "Precision Auto Components Ltd",
        "business_type": "mfg",
        "segment": "mfg",
        "city": "Pune",
        "city_tier": 1,
        "pincode": "411018",
        "employee_count": 35,
        "num_sites": 1,
        "monthly_budget_inr": 35000,
        "has_gstin": True,
        "gstin": "27DGKXS9651J1Z2",
        "need_sims": 10,
        "need_pos": False,
        "need_whatsapp": False,
        "need_cctv": True,
        "cctv_cameras_count": 8,
        "need_cloud_email": True,
        "need_cloud_backup": True,
        "need_security": True,
        "need_failover_backup": True,
        "need_dedicated_leased_line": True,
        "preferred_language": "en",
        "story": "Industrial operation requiring 1:1 dedicated leased line, 99.9% SLA, machine monitoring IoT sensors, managed hardware firewall, and static IP."
    }
]

# Complete Catalog of all 12 KYC Specimen Test Cases
KYC_TEST_CASES = [
    {
        "id": "K01",
        "name": "Vindhya Tours & Travels (K01)",
        "gstin": "37IHKXV5167L1ZS",
        "udyam_number": None,
        "status_expected": "FAILED",
        "notes": "GSTIN is CANCELLED in mock registry; Udyam registration number is blank on certificate."
    },
    {
        "id": "K02",
        "name": "Harmony Dental Care (K02)",
        "gstin": "19EOGXH4115Y1ZL",
        "udyam_number": "UDYAM-WB-00-5053330",
        "status_expected": "PASS",
        "notes": "Valid clean KYC with active GSTIN, active Udyam, matching legal name, and recent electricity bill."
    },
    {
        "id": "K03",
        "name": "Ganesh Woodcraft (K03)",
        "gstin": "27XUIXG0767D1ZP",
        "udyam_number": "UDYAM-MH-00-9516696",
        "status_expected": "PASS",
        "notes": "Valid clean KYC with active GSTIN and active Udyam registration."
    },
    {
        "id": "K04",
        "name": "Saffron Dental Care LLP (K04)",
        "gstin": "27PZSXS1936O1ZH",
        "udyam_number": "UDYAM-MH-00-6131836",
        "status_expected": "FAILED",
        "notes": "Corrupted/blank GST certificate image (only title text exists, no table data)."
    },
    {
        "id": "K05",
        "name": "Balaji Realty LLP (K05)",
        "gstin": "32TZAXB5481U1Z1",
        "udyam_number": "UDYAM-KL-00-5521886",
        "status_expected": "REVIEW_REQUIRED",
        "notes": "Udyam registration number was declared but Udyam certificate file is missing from upload set."
    },
    {
        "id": "K06",
        "name": "Saffron Unisex Salon (K06)",
        "gstin": "08YKZXS5189L1ZO",
        "udyam_number": "UDYAM-RJ-00-6577157",
        "status_expected": "PASS",
        "notes": "Active GSTIN and active Udyam enterprise registration with valid recent address proof."
    },
    {
        "id": "K07",
        "name": "Shri Physio Clinic (K07)",
        "gstin": "07CPCXN0398P1ZT",
        "udyam_number": "UDYAM-DL-00-9565547",
        "status_expected": "REVIEW_REQUIRED",
        "notes": "Name mismatch: Application states 'Shri Physio Clinic' while document states 'Neelgiri Physio Clinic'."
    },
    {
        "id": "K08",
        "name": "Green Leaf Legal Associates (K08)",
        "gstin": "24XORXG9365M1Z3",
        "udyam_number": "UDYAM-GJ-00-9158296",
        "status_expected": "PASS",
        "notes": "Fully verified legal consultancy with active GSTIN and compliant documentation."
    },
    {
        "id": "K09",
        "name": "Kaveri Insurance Advisors (K09)",
        "gstin": "37LDYXK0296F1ZB",
        "udyam_number": "UDYAM-AP-00-9751562",
        "status_expected": "PASS",
        "notes": "Compliant financial advisory firm with active GSTIN and verified signatory identity."
    },
    {
        "id": "K10",
        "name": "Kaveri Stays LLP (K10)",
        "gstin": "27QHJXK0658U1ZL",
        "udyam_number": "UDYAM-MH-00-7183141",
        "status_expected": "PASS",
        "notes": "Compliant hospitality business with active GSTIN and matching registered address."
    },
    {
        "id": "K11",
        "name": "Trinity Bake House Pvt Ltd (K11)",
        "gstin": "03KGZXT1320R1ZZ",
        "udyam_number": "UDYAM-PB-00-9719478",
        "status_expected": "REVIEW_REQUIRED",
        "notes": "Expired utility bill: Bill date is 2025-10-31 (257 days old > 90 day limit from reference date 2026-07-15)."
    },
    {
        "id": "K12",
        "name": "Star Electronics (K12)",
        "gstin": "37NBLXS1145E1ZU",
        "udyam_number": "UDYAM-AP-00-5186772",
        "status_expected": "PASS",
        "notes": "Compliant retail electronics enterprise with active GSTIN and valid recent utility bill."
    }
]

class DemoService:
    def get_scenarios(self) -> List[Dict[str, Any]]:
        return DEMO_SCENARIOS

    def get_kyc_test_cases(self) -> List[Dict[str, Any]]:
        return KYC_TEST_CASES

demo_service = DemoService()
