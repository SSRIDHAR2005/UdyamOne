# Project UdyamOne — 10-Slide Business Case Presentation
## Airtel SYNC | YTL Hackathon 2026 | Enterprise Track A

---

### Slide 1: Executive Summary & Vision
- **Product Name:** UdyamOne
- **Tagline:** One Conversation. One Smart Bundle. One Connected Business.
- **Strategic Opportunity:** India's 6 Crore+ MSMEs require multi-product digital bundles (Broadband, SIMs, POS, Cloud Email, WhatsApp, Security). Today, Accel Business sells piecemeal through slow field visits.
- **The Solution:** An AI-powered digital acquisition and self-serve onboarding platform that compresses the customer journey from 17.6 days down to 4.5 days, reducing Customer Acquisition Cost (CAC) by 68%.

---

### Slide 2: Acquisition Funnel Problem Diagnosis
*Source: `smb_leads.csv` (Synthetic Baseline, 5,000 Leads, Apr–Jun 2026)*

| Stage | Leads | Conversion % | Drop Count | Root Cause Identified in Data |
|---|---|---|---|---|
| 1. Leads Generated | 5,000 | 100% | - | - |
| 2. Contacted | 3,406 | 68.1% | 1,594 | Unreachable, cold outreach friction |
| 3. Needs Assessed | 1,974 | 58.0% | 1,432 | Owner lacked time for in-person sales visit |
| **4. Quote Accepted** | **861** | **43.6%** | **1,113 (STEEPEST)** | **Quotes took 3-5 days; complex SKU codes; high price pushback** |
| 5. KYC Complete | 588 | 68.3% | 273 | Missing GST/Udyam docs; long paperwork fatigue |
| 6. Activated | 368 | 62.6% | 220 | Installation delayed >21 days; customer chased status 3x |

**Net Activation Rate:** Only **7.36%** (368 activations) at a blended CAC of **₹15,000** per SMB.

---

### Slide 3: Priority MSME Customer Segments

1. **Micro Retail & Services (55% Base) — High Volume Anchor**
   - *Examples:* Kiranas, salons, pharmacies.
   - *Priorities:* Cheap broadband, reliable POS/UPI billing, 1-2 business SIMs, WhatsApp customer updates.
   - *Price Sensitivity:* Very high.
2. **Professional Offices (25% Base) — High Margin Early Adopters**
   - *Examples:* Diagnostic clinics, CA firms, coaching centers.
   - *Priorities:* 99.9% uptime, Google/Office cloud suite, patient/client data backup, endpoint antivirus.
   - *Price Sensitivity:* Medium.
3. **Small Multi-Site Businesses (15% Base) — High LTV Accounts**
   - *Examples:* Restaurant chains, multi-store retail.
   - *Priorities:* Central billing, 4G/5G failover router, centralized cloud CCTV, SD-WAN.
4. **Small Manufacturers (5% Base) — Enterprise Leased Line Target**
   - *Examples:* Auto component units, textile factories.
   - *Priorities:* 1:1 dedicated leased line, IoT machine uptime sensors, managed firewall.

---

### Slide 4: Proposed Solution & Customer Journey
- **0–30s Discovery:** Progressive questions in preferred regional language (English, Hindi, Tamil) with text-to-speech audio narration.
- **30–60s Recommendation:** 3 comparison tiers (Essential, Growth, Advanced) grounded strictly in Accel's 25-SKU catalogue.
- **60–90s Smart Quote:** Modular add-on configurator with dependency enforcement and real-time 18% GST recalculation. Downloadable quote PDF.
- **90–150s Instant KYC:** DPDP Act 2023 granular consent, sub-second GSTIN & Udyam lookups, native OCR validation with exception handling.
- **Day 1–4 Tracked Fulfillment:** Proactive 7-stage order status roadmap with assigned technician contact and delay alerts.

---

### Slide 5: Catalogue-Grounded AI Recommendation Architecture
- **Zero Hallucination Guarantee:** The AI advisor never fabricates nonexistent telecom plans or arbitrary pricing.
- **Mathematical Constraint Solver:**
  - `available_city_tiers`: Restricts city tier availability.
  - `min_employees` & `min_sites`: Enforces minimum scale requirements.
  - `requires_gstin`: Prevents unregistered sales of enterprise leased lines and SD-WAN.
  - `requires_one_of`: Automatically enforces technical prerequisites (e.g., P09 failover requires fiber P01|P02|P03|P05|P06).
- **Explainability:** Transparent "Why this recommendation" explanation and clear limitations for every tier.

---

### Slide 6: Smart KYC & Regulatory Transformation
- **Near-Instant Verification:** Replaces 3-5 days of physical paper collection with automated digital verification against 3,534 GSTINs and 2,723 Udyam certificates.
- **Automated Anomaly Detection:**
  - Flags expired utility bills (>90 days from `2026-07-15`).
  - Detects trade vs legal name mismatches.
  - Catches cancelled/suspended registrations immediately.
- **Prescriptive Correction:** Guides applicants on exact fixes instead of generating ambiguous rejection notices.

---

### Slide 7: Business Model, Pricing & Value Proposition
- **Transparent Formula:** Total Monthly Cost = Σ(Eligible Product Unit Prices) + 18% GST.
- **Customer Value:** 15–25% savings compared to buying disparate broadband, mobile, cloud, and security subscriptions separately.
- **Operator Value:**
  - Shifts customers from prepaid SIM churn to 12–24 month contracted B2B agreements.
  - Lifts average monthly bundle value from ₹2,500 (single product) to ₹6,900–₹7,200 (bundled ARPU).

---

### Slide 8: Partner-Assisted Go-to-Market Strategy
- **Synergy Over Substitution:** Channel partners and field sales are not replaced; their productivity is multiplied.
- **Predictive Partner Dashboard:** Partners receive leads scored by our Scikit-learn Random Forest model.
- **Targeted Human Intervention:** Sales reps intervene only when a lead stalls at quote acceptance or encounters a complex KYC anomaly.
- **Guaranteed Commission Protection:** Partner attribution codes ensure full commission payout on all digital activations.

---

### Slide 9: Rollout Plan, KPIs & Targets

| Metric | Historical Baseline (`smb_leads.csv`) | UdyamOne Target |
|---|---|---|
| **Lead-to-Activation Conversion** | 7.36% (368 / 5,000) | **24.50%** (3.3× Funnel Lift) |
| **Lead-to-Activation Cycle Time** | 17.6 Days | **4.5 Days** (-74% Cycle Compression) |
| **Customer Status Chases** | 3.0 Calls per Customer | **0.3 Calls** (-90% Support Load) |
| **Blended Customer Acquisition Cost** | ₹15,000 per Activated SMB | **₹4,800** (-68% CAC Reduction) |
| **Average Monthly ARPU** | ₹6,900 / month | **₹7,200 / month** (+4.3% Upsell Attachment) |

- **Phased Rollout:**
  - *Phase 1 (M1–M3):* 5 Tier 1 Metro Hubs with top 250 channel partners.
  - *Phase 2 (M4–M6):* 15 Tier 2 Industrial Hubs targeting micro retail and polyclinics.
  - *Phase 3 (M7–M12):* Pan-India expansion with automated WhatsApp onboarding integration.

---

### Slide 10: Risk Management & Mitigations
- **Civil Cabling Delays:** If fiber installation exceeds 48 hours, auto-dispatch plug-and-play Biz 5G AirFiber (P04) as an immediate bridge.
- **Unregistered Micro Businesses:** Dedicated Udyam micro registration assistance unlocks the 4.8× conversion lift between GSTIN and non-GSTIN leads.
- **Partner Channel Friction:** Zero channel conflict through partner revenue sharing and shared commission ledgers.

