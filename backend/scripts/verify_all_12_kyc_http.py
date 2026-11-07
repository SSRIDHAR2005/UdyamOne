import urllib.request
import json

cases = [
    ("K01", "Sri Krishna Enterprises (K01)", "37IHKXV5167L1ZS", "", "FAILED", "Cancelled GSTIN in mock registry"),
    ("K02", "Harmony Dental Care (K02)", "19EOGXH4115Y1ZL", "UDYAM-WB-00-5053330", "PASS", "Active GSTIN & valid Udyam"),
    ("K03", "Ganesh Woodcraft (K03)", "27XUIXG0767D1ZP", "UDYAM-MH-00-9516696", "PASS", "Active GSTIN & valid Udyam"),
    ("K04", "Saffron Dental Care LLP (K04)", "27PZSXS1936O1ZH", "UDYAM-MH-00-6131836", "FAILED", "Corrupted/blank GST certificate image"),
    ("K05", "Balaji Realty LLP (K05)", "32TZAXB5481U1Z1", "UDYAM-KL-00-5521886", "REVIEW_REQUIRED", "Udyam declared but doc file missing"),
    ("K06", "Saffron Unisex Salon (K06)", "08YKZXS5189L1ZO", "UDYAM-RJ-00-6577157", "PASS", "Active GSTIN & valid Udyam"),
    ("K07", "Shri Physio Clinic (K07)", "07CPCXN0398P1ZT", "UDYAM-DL-00-9565547", "REVIEW_REQUIRED", "Trade name mismatch: Shri vs Neelgiri"),
    ("K08", "Green Leaf Legal Associates (K08)", "24XORXG9365M1Z3", "UDYAM-GJ-00-9158296", "PASS", "Active GSTIN & valid Udyam"),
    ("K09", "Kaveri Insurance Advisors (K09)", "37LDYXK0296F1ZB", "UDYAM-AP-00-9751562", "PASS", "Active GSTIN & valid Udyam"),
    ("K10", "Kaveri Stays LLP (K10)", "27QHJXK0658U1ZL", "UDYAM-MH-00-7183141", "PASS", "Active GSTIN & valid Udyam"),
    ("K11", "Trinity Bake House Pvt Ltd (K11)", "03KGZXT1320R1ZZ", "UDYAM-PB-00-9719478", "REVIEW_REQUIRED", "Expired address bill (>90 days old)"),
    ("K12", "Star Electronics (K12)", "37NBLXS1145E1ZU", "UDYAM-AP-00-5186772", "PASS", "Active GSTIN & valid Udyam")
]

url = "http://127.0.0.1:8000/api/v1/kyc/validate"
all_matched = True

print(f"{'ID':<5} | {'Expected':<16} | {'Actual Status':<16} | {'Match?':<7} | {'Ground Truth Condition'}")
print("-" * 80)

for cid, bname, gst, udy, expected, note in cases:
    payload = {
        "business_name": bname,
        "applicant_name": "Ramesh Kumar",
        "applicant_role": "Authorized Signatory",
        "gstin": gst if gst else None,
        "udyam_number": udy if udy else None,
        "consent": {
            "consent_given": True,
            "version": "DPDP-2026-V1.0",
            "purposes": {"gstin_lookup": True, "udyam_verification": True},
            "applicant_name": "Ramesh Kumar"
        }
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        actual = res["overall_status"]
        matched = (actual == expected)
        if not matched:
            all_matched = False
        print(f"{cid:<5} | {expected:<16} | {actual:<16} | {str(matched):<7} | {note}")
        if not matched:
            print("  DETECTED ISSUES:", res.get("detected_issues"))

print("-" * 80)
print(f"VERIFICATION RESULT: {'ALL 12/12 CASES MATCH GROUND TRUTH PERFECTLY!' if all_matched else 'FAILED'}")
