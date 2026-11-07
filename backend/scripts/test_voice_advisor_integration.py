"""
PROJECT UDYAMONE - VOICE TRANSCRIPT TO AI ADVISOR END-TO-END TEST SUITE
Verifies Requirement 8:
A. English voice input: Sri Lakshmi Stores in Chennai
B. Hindi voice input: Balaji Dental Clinic in Delhi
C. Tamil voice input: Sri Murugan Restaurant in Chennai
D. Manual fallback: User edits transcript and submits
E. Error handling: Empty transcript validation
"""

import urllib.request
import urllib.error
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def post_transcript(transcript: str, language: str = "en"):
    url = f"{BASE_URL}/advisor/process-transcript"
    payload = {"transcript": transcript, "language": language}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def test_a_english_journey():
    print("=================================================================")
    print("TEST A: English Voice Input (Sri Lakshmi Stores, Chennai)")
    print("=================================================================")
    transcript = (
        "I run a small grocery shop called Sri Lakshmi Stores in Chennai. "
        "I have one shop and around three employees. I need reliable internet "
        "for UPI payments, online billing and WhatsApp orders. I also want "
        "CCTV connectivity for security. My monthly budget is around 3000 rupees."
    )
    status, data = post_transcript(transcript, "en")
    assert status == 200, f"Expected 200, got {status}"
    
    prof = data["extracted_profile"]
    assert prof["business_name"] == "Sri Lakshmi Stores", f"Mismatch name: {prof['business_name']}"
    assert prof["business_category"] == "Retail / Grocery"
    assert prof["operating_city"] == "Chennai"
    assert prof["city_tier"] == 1
    assert prof["number_of_sites"] == 1
    assert prof["employee_count"] == 3
    assert prof["monthly_budget"] == 3000.0
    
    expected_reqs = ["Reliable internet", "UPI payments", "Online billing", "WhatsApp orders", "CCTV connectivity"]
    for req in expected_reqs:
        assert req in prof["requirements"], f"Missing requirement: {req}"
        
    matched = data["matched_catalogue_products"]
    matched_pids = [m["product_id"] for m in matched]
    print(f"  Extracted Business: {prof['business_name']} ({prof['business_category']}) in {prof['operating_city']}")
    print(f"  Scale & Budget: {prof['number_of_sites']} site(s), {prof['employee_count']} staff, Rs {prof['monthly_budget']}/mo")
    print(f"  Extracted Requirements: {prof['requirements']}")
    print(f"  Matched Catalogue Products ({len(matched)} SKUs): {matched_pids}")
    
    recs = data["recommendations"]["recommendations"]
    assert len(recs) == 3, f"Expected 3 tiers, got {len(recs)}"
    for r in recs:
        print(f"  -> Recommended Tier: {r['tier_name']} | Monthly: Rs {r['monthly_total_inr']} | Setup: Rs {r['one_time_setup_inr']}")
    print("TEST A PASSED!\n")

def test_b_hindi_journey():
    print("=================================================================")
    print("TEST B: Hindi Voice Input (Balaji Dental Clinic, Delhi)")
    print("=================================================================")
    transcript = "मेरी दिल्ली में बालाजी डेंटल क्लिनिक नाम की एक क्लिनिक है। हमारे पास 4 कर्मचारी हैं। मुझे ऑनलाइन बिलिंग, यूपीआई पेमेंट और सीसीटीवी सुरक्षा के लिए इंटरनेट चाहिए। मेरा मासिक बजट 5000 रुपये है।"
    status, data = post_transcript(transcript, "hi")
    assert status == 200, f"Expected 200, got {status}"
    
    prof = data["extracted_profile"]
    assert "बालाजी डेंटल क्लिनिक" in prof["business_name"], f"Name mismatch: {prof['business_name']}"
    assert prof["business_category"] == "Healthcare / Clinic"
    assert prof["operating_city"] == "Delhi"
    assert prof["employee_count"] == 4
    assert prof["monthly_budget"] == 5000.0
    
    print(f"  Extracted Business: {prof['business_name']} ({prof['business_category']}) in {prof['operating_city']}")
    print(f"  Scale & Budget: {prof['number_of_sites']} site(s), {prof['employee_count']} staff, Rs {prof['monthly_budget']}/mo")
    print(f"  Extracted Requirements: {prof['requirements']}")
    
    recs = data["recommendations"]["recommendations"]
    assert len(recs) == 3
    print(f"  Generated {len(recs)} catalogue tiers in Hindi successfully.")
    print("TEST B PASSED!\n")

def test_c_tamil_journey():
    print("=================================================================")
    print("TEST C: Tamil Voice Input (Sri Murugan Restaurant, Chennai)")
    print("=================================================================")
    transcript = "நான் சென்னையில் ஸ்ரீ முருகன் ரெஸ்டாரன்ட் என்ற உணவகம் நடத்துகிறேன். என்னிடம் 2 கடைகள் மற்றும் 6 ஊழியர்கள் உள்ளனர். எனக்கு ஆன்லைன் பில்லிங், வாட்ஸ்அப் ஆர்டர்கள் மற்றும் சிசிடிவி பாதுகாப்பு தேவை. என் மாதாந்திர பட்ஜெட் 8000 ரூபாய்."
    status, data = post_transcript(transcript, "ta")
    assert status == 200, f"Expected 200, got {status}"
    
    prof = data["extracted_profile"]
    assert "ஸ்ரீ முருகன் ரெஸ்டாரன்ட்" in prof["business_name"], f"Name mismatch: {prof['business_name']}"
    assert prof["business_category"] == "Restaurant / Hospitality"
    assert prof["operating_city"] == "Chennai"
    assert prof["number_of_sites"] == 2
    assert prof["employee_count"] == 6
    assert prof["monthly_budget"] == 8000.0
    
    print(f"  Extracted Business: {prof['business_name']} ({prof['business_category']}) in {prof['operating_city']}")
    print(f"  Scale & Budget: {prof['number_of_sites']} site(s), {prof['employee_count']} staff, Rs {prof['monthly_budget']}/mo")
    print(f"  Extracted Requirements: {prof['requirements']}")
    
    recs = data["recommendations"]["recommendations"]
    assert len(recs) == 3
    print(f"  Generated {len(recs)} catalogue tiers in Tamil successfully.")
    print("TEST C PASSED!\n")

def test_d_manual_fallback_journey():
    print("=================================================================")
    print("TEST D: Manual Fallback / Edited Transcript")
    print("=================================================================")
    # User captured rough speech and manually edited budget and staff
    edited_transcript = "We run Apex Manufacturing in Pune. We have 1 plant and 25 workers. We require dedicated leased line and CCTV security with budget 35000 inr."
    status, data = post_transcript(edited_transcript, "en")
    assert status == 200, f"Expected 200, got {status}"
    
    prof = data["extracted_profile"]
    assert "Apex Manufacturing" in prof["business_name"]
    assert prof["business_category"] == "Manufacturing / Industrial"
    assert prof["operating_city"] == "Pune"
    assert prof["employee_count"] == 25
    assert prof["monthly_budget"] == 35000.0
    assert "Dedicated leased line" in prof["requirements"]
    
    print(f"  Extracted Business: {prof['business_name']} ({prof['business_category']}) in {prof['operating_city']}")
    print(f"  Scale & Budget: {prof['employee_count']} staff, Rs {prof['monthly_budget']}/mo")
    print(f"  Requirements: {prof['requirements']}")
    print("TEST D PASSED!\n")

def test_e_empty_transcript_error_handling():
    print("=================================================================")
    print("TEST E: Error Handling for Empty Transcript")
    print("=================================================================")
    url = f"{BASE_URL}/advisor/process-transcript"
    payload = {"transcript": "   ", "language": "en"}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req)
        print("FAILED: Did not raise error for empty transcript!")
        sys.exit(1)
    except urllib.error.HTTPError as e:
        assert e.code == 400, f"Expected 400, got {e.code}"
        err_msg = json.loads(e.read().decode("utf-8"))["detail"]
        print(f"  Caught HTTP 400 as expected: '{err_msg}'")
        print("TEST E PASSED!\n")

if __name__ == "__main__":
    print("=================================================================")
    print("UDYAMONE VOICE TO AI ADVISOR END-TO-END HTTP TEST HARNESS")
    print("=================================================================\n")
    test_a_english_journey()
    test_b_hindi_journey()
    test_c_tamil_journey()
    test_d_manual_fallback_journey()
    test_e_empty_transcript_error_handling()
    print("=================================================================")
    print("ALL 5 VOICE TO AI ADVISOR INTEGRATION TESTS PASSED (100% LIVE HTTP)!")
    print("=================================================================")

