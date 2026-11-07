import pandas as pd
from pathlib import Path

csv_path = Path("backend/data/smb_leads.csv")
df = pd.read_csv(csv_path)

total = len(df)
contacted = len(df[df['contacted_date'].notna()])
needs = len(df[df['needs_assessed_date'].notna()])
quote = len(df[df['quote_accepted_date'].notna()])
kyc = len(df[df['kyc_complete_date'].notna()])
act = len(df[df['outcome'] == 'Activated'])

print(f"Total: {total}")
print(f"Contacted: {contacted} ({contacted/total*100:.1f}%)")
print(f"Needs Assessed: {needs} ({needs/total*100:.1f}%)")
print(f"Quote Accepted: {quote} ({quote/total*100:.1f}%)")
print(f"KYC Complete: {kyc} ({kyc/total*100:.1f}%)")
print(f"Activated: {act} ({act/total*100:.2f}%)")

drop_needs_quote = needs - quote
print(f"Needs->Quote Drop: {drop_needs_quote} ({drop_needs_quote/needs*100:.1f}%)")

g_y = df[df['has_gstin'] == 'Y']['outcome'].value_counts(normalize=True).get('Activated', 0) * 100
g_n = df[df['has_gstin'] == 'N']['outcome'].value_counts(normalize=True).get('Activated', 0) * 100
print(f"With GSTIN Conversion: {g_y:.2f}%")
print(f"Without GSTIN Conversion: {g_n:.2f}%")
print(f"GSTIN Lift: {g_y/g_n:.2f}x")

act_df = df[df['outcome'] == 'Activated']
print(f"Avg Lead to Activation Days: {act_df['days_lead_to_activation'].mean():.1f}")
print(f"Avg Follow-up Calls: {act_df['customer_follow_up_calls'].mean():.1f}")
print(f"Avg CAC: INR {act_df['acquisition_cost_inr'].mean():.0f}")
print(f"Avg Monthly ARPU: INR {act_df['monthly_bundle_value_inr'].mean():.0f}")

