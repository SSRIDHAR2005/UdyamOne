import json
import re
import pandas as pd
from datetime import datetime

with open('kyc_ocr_dump_utf8.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

gst_reg = pd.read_csv('6ae1873397bc1_digital/YTL_TrackA_Udyam_Digital_Data/mock_gstin_registry.csv')
udyam_reg = pd.read_csv('6ae1873397bc1_digital/YTL_TrackA_Udyam_Digital_Data/mock_udyam_registry.csv')

gst_by_id = {str(row['gstin']).strip(): row for _, row in gst_reg.iterrows()}
udyam_by_id = {str(row['udyam_number']).strip(): row for _, row in udyam_reg.iterrows()}

TODAY = datetime.strptime("2026-07-15", "%Y-%m-%d")

print(f"{'Applicant':<10} | {'GSTIN':<16} | {'GST Status':<10} | {'Udyam':<20} | {'Bill Date':<10} | {'Days Old':<8} | {'Findings'}")
print("-" * 120)

for k in range(1, 13):
    p = f"K{k:02d}"
    gst_txt = data.get(f"{p}_gst_certificate.png", "")
    udyam_txt = data.get(f"{p}_udyam_certificate.png", "")
    sig_txt = data.get(f"{p}_signatory_id.png", "")
    addr_txt = data.get(f"{p}_address_proof.png", "")

    # Clean spaces around IDs
    cleaned_gst = re.sub(r'\s+', '', gst_txt)
    gst_match = re.search(r'[0-9]{2}[A-Z]{4}[A-Z0-9][0-9]{4}[A-Z0-9][1-9A-Z]Z[0-9A-Z]', cleaned_gst)
    gst_num = gst_match.group(0) if gst_match else 'None'
    
    cleaned_udyam = re.sub(r'\s+', '', udyam_txt)
    udyam_match = re.search(r'UDYAM-[A-Z]{2}-00-[0-9]{7}', cleaned_udyam)
    udyam_num = udyam_match.group(0) if udyam_match else ('MISSING' if f"{p}_udyam_certificate.png" not in data else 'None')

    # Date
    dates = re.findall(r'202[0-9]-[0-9]{2}-[0-9]{2}', addr_txt)
    bill_date = dates[0] if dates else 'None'
    days_old = 'N/A'
    if bill_date != 'None':
        d_obj = datetime.strptime(bill_date, "%Y-%m-%d")
        days_old = str((TODAY - d_obj).days)

    gst_row = gst_by_id.get(gst_num)
    gst_status = gst_row['status'] if gst_row is not None else 'NOT FOUND'

    findings = []
    if gst_status != 'Active':
        findings.append(f"GST {gst_status}")
    if udyam_num == 'MISSING':
        findings.append("Missing Udyam Doc")
    elif udyam_num not in udyam_by_id and udyam_num != 'None':
        findings.append("Udyam Not In Registry")
    
    if days_old != 'N/A' and int(days_old) > 90:
        findings.append(f"Address Proof Expired ({days_old}d > 90d)")

    # Name check
    if gst_row is not None:
        trade_name = str(gst_row['trade_name']).lower()
        if trade_name not in gst_txt.lower() and trade_name not in addr_txt.lower():
            findings.append("Name Mismatch")

    findings_str = "; ".join(findings) if findings else "VALID PASS"
    print(f"{p:<10} | {gst_num:<16} | {gst_status:<10} | {udyam_num:<20} | {bill_date:<10} | {days_old:<8} | {findings_str}")

