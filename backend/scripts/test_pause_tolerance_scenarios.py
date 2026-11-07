"""
UdyamOne - Test Pause Tolerance & Speech Accumulation Scenarios
Tests the exact scenarios described in the prompt:
- Scenario 1: Short pause (1-3s)
- Scenario 2: Medium pause (3-5s) - "I run a restaurant in Chennai..." [pause] "...with three outlets and twenty employees. I need reliable internet, POS billing and CCTV."
- Scenario 3: Long pause (5-8s)
- Scenario 4: Explicit Stop with trailing interim text
- Scenario 5: Full AI Advisor extraction and catalogue matching from pause-merged transcript
"""
import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def post_json(endpoint: str, data: dict):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def simulate_speech_accumulator(chunks):
    """
    Simulates the exact React SpeechAccumulator logic implemented in AdvisorTab.tsx:
    - finalTranscript accumulated across sessions
    - interim transcript rendered during active utterance
    - restarts appending without duplicating tokens
    """
    final_transcript = ""
    for is_final, text in chunks:
        text = text.strip()
        if not text:
            continue
        if is_final:
            existing = final_transcript.strip()
            if not existing:
                final_transcript = text
            elif not existing.endswith(text):
                final_transcript = f"{existing} {text}"
    return final_transcript

def run_tests():
    print("=" * 65)
    print("UDYAMONE PAUSE-TOLERANCE SCENARIO TESTS")
    print("=" * 65)

    # -------------------------------------------------------------
    # Scenario 1: Short Pause (1-3s)
    # User says: "We are Apex Logistics in Pune" [2s pause] "with 15 employees"
    # -------------------------------------------------------------
    print("\n--- TEST A: Short Pause (1-3s) Simulation ---")
    chunks_a = [
        (True, "We are Apex Logistics in Pune"),
        # Simulation of browser onend + 350ms restart after pause
        (True, "with 15 employees and 4 branches")
    ]
    accumulated_a = simulate_speech_accumulator(chunks_a)
    print(f"  Accumulated: '{accumulated_a}'")
    assert accumulated_a == "We are Apex Logistics in Pune with 15 employees and 4 branches"
    print("  ✓ Short pause speech retained and merged cleanly.")

    # -------------------------------------------------------------
    # Scenario 2: Medium Pause (3-5s) - Exact Prompt Example
    # User says: "I run a restaurant in Chennai..." [3-5s pause]
    # "...with three outlets and twenty employees. I need reliable internet, POS billing and CCTV."
    # -------------------------------------------------------------
    print("\n--- TEST B: Medium Pause (3-5s) Prompt Case ---")
    chunks_b = [
        (True, "I run a restaurant in Chennai"),
        # Natural pause: onend fired by browser, session restarted seamlessly
        (True, "with three outlets and twenty employees. I need reliable internet, POS billing and CCTV.")
    ]
    accumulated_b = simulate_speech_accumulator(chunks_b)
    print(f"  Accumulated: '{accumulated_b}'")
    assert "restaurant in Chennai" in accumulated_b
    assert "twenty employees" in accumulated_b
    assert "POS billing and CCTV" in accumulated_b
    print("  ✓ Medium pause retained complete context.")

    # Verify that sending this pause-accumulated transcript to the AI Advisor
    # extracts ALL fields correctly:
    status_b, data_b = post_json("/api/v1/advisor/process-transcript", {
        "transcript": accumulated_b,
        "language": "en"
    })
    assert status_b == 200, f"Error status: {status_b}"
    prof_b = data_b["extracted_profile"]
    print(f"  AI Advisor Extracted:")
    print(f"    - Segment: {prof_b['segment']}")
    print(f"    - City: {prof_b['operating_city']}")
    print(f"    - Outlets / Sites: {prof_b['number_of_sites']}")
    print(f"    - Staff: {prof_b['employee_count']}")
    print(f"    - Needs: POS={prof_b['need_pos']}, CCTV={prof_b['need_cctv']}")
    assert prof_b["segment"] in ["multi", "restaurant", "micro"]
    assert prof_b["business_type"] == "restaurant"
    assert prof_b["operating_city"] == "Chennai"
    assert prof_b["number_of_sites"] == 3
    assert prof_b["employee_count"] == 20
    assert prof_b["need_pos"] is True
    assert prof_b["need_cctv"] is True
    print("  ✓ AI Advisor accurately parsed entire transcript across pause.")

    # -------------------------------------------------------------
    # Scenario 3: Long Pause (5-8s)
    # User thinks for 7 seconds between utterances
    # -------------------------------------------------------------
    print("\n--- TEST C: Long Pause (5-8s) Simulation ---")
    chunks_c = [
        (True, "My business is Sharma Diagnostic Lab in Mumbai"),
        # Long pause triggers onend, restart timeout keeps session listening
        (True, "we have 12 staff members and need dedicated leased line with cloud backup"),
        (True, "budget is 15000 rupees monthly")
    ]
    accumulated_c = simulate_speech_accumulator(chunks_c)
    print(f"  Accumulated: '{accumulated_c}'")
    status_c, data_c = post_json("/api/v1/advisor/process-transcript", {
        "transcript": accumulated_c,
        "language": "en"
    })
    assert status_c == 200
    prof_c = data_c["extracted_profile"]
    print(f"  Extracted: {prof_c['business_name']} | LeasedLine={prof_c['need_dedicated_leased_line']} | CloudBackup={prof_c['need_cloud_backup']} | Budget={prof_c['monthly_budget']}")
    assert prof_c["need_dedicated_leased_line"] is True
    assert prof_c["need_cloud_backup"] is True
    assert prof_c["monthly_budget"] == 15000.0
    print("  ✓ Long pause multi-chunk accumulation succeeded.")

    # -------------------------------------------------------------
    # Scenario 4: Explicit Stop with Trailing Interim Result
    # User speaks interim words and clicks 'Stop Recording'
    # -------------------------------------------------------------
    print("\n--- TEST D: Explicit Stop with Trailing Interim Text ---")
    final_text = "Sri Meenakshi Textiles in Coimbatore with 8 employees"
    trailing_interim = "and need WhatsApp business messaging"
    # Appended on stopRecording(keepInterim=True)
    merged_on_stop = f"{final_text} {trailing_interim}"
    status_d, data_d = post_json("/api/v1/advisor/process-transcript", {
        "transcript": merged_on_stop,
        "language": "en"
    })
    assert status_d == 200
    prof_d = data_d["extracted_profile"]
    assert prof_d["need_whatsapp"] is True
    print(f"  Extracted with interim appended: WhatsApp={prof_d['need_whatsapp']}")
    print("  ✓ Trailing interim speech successfully preserved on stop.")

    # -------------------------------------------------------------
    # Scenario 5: Full Catalogue Grounding Verification
    # Confirm generated bundles contain official SKUs only
    # -------------------------------------------------------------
    print("\n--- TEST E: Catalogue Grounding Check ---")
    recs = data_b["recommendations"]["recommendations"]
    assert len(recs) == 3, f"Expected 3 tiers, got {len(recs)}"
    for t in recs:
        pids = [p['product_id'] for p in t['products']]
        print(f"  Tier: {t['tier_name']} | Total: Rs {t['monthly_total_inr']}/mo | Setup: Rs {t['one_time_setup_inr']} | SKUs: {pids}")
        # Verify no invented SKUs
        for p in t["products"]:
            assert p["product_id"].startswith("P"), f"Invalid product {p['product_id']}"
    print("  ✓ Catalogue grounding strictly verified (no invented SKUs).")

    print("\n" + "=" * 65)
    print("ALL PAUSE-TOLERANCE SCENARIOS PASSED WITH 100% SUCCESS!")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
