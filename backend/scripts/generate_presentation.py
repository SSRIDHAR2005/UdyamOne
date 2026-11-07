import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path="docs/business-case/UdyamOne_Business_Case_10_Slides.pptx"):
    prs = Presentation()
    # 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    crimson = RGBColor(225, 29, 72)     # #E11D48
    slate_dark = RGBColor(15, 23, 42)   # #0F172A
    slate_muted = RGBColor(100, 116, 139) # #64748B
    white = RGBColor(255, 255, 255)
    card_bg = RGBColor(248, 250, 252)
    border_gray = RGBColor(226, 232, 240)

    slides_data = [
        {
            "num": "Slide 1",
            "title": "Executive Summary & Product Vision",
            "subtitle": "Project UdyamOne · Airtel SYNC / YTL Hackathon 2026 · Enterprise Track A",
            "points": [
                ("Product Name & Tagline", "UdyamOne — 'One Conversation. One Smart Bundle. One Connected Business.'"),
                ("Strategic Imperative", "India's 6.3 Crore MSMEs require integrated connectivity and digital tools (Broadband, SIMs, POS, Cloud, WhatsApp, Security). Today, Accel Business sells fragmented single products via slow physical visits."),
                ("Transformational Solution", "An AI-powered digital acquisition and onboarding platform engineered to compress the sales cycle from 17.6 days (baseline) to 4.5 days (target projection) and slash blended CAC by 68% (from ₹15,000 baseline to ₹4,800 target projection)."),
                ("Enterprise Quality Bar", "Production-grade microservices with DPDP Act 2023 compliance, native OCR anomaly detection, and predictive lead scoring grounded in Accel's 25-SKU catalogue.")
            ]
        },
        {
            "num": "Slide 2",
            "title": "Acquisition Funnel Problem Diagnosis",
            "subtitle": "Data Ground Truth: 5,000 SMB Leads Analysis (April–June 2026 Baseline)",
            "table": {
                "headers": ["Funnel Stage", "Baseline Leads", "Stage Conversion", "Drop Count", "Root Cause in Historical Leads"],
                "rows": [
                    ["1. Leads Generated", "5,000", "100.0%", "-", "Digital marketing & inbound partner inquiries"],
                    ["2. Contacted", "3,406", "68.1%", "1,594", "Unreachable numbers, friction in cold tele-calling"],
                    ["3. Needs Assessed", "1,974", "58.0%", "1,432", "Business owners lack time for scheduled in-person reps"],
                    ["4. Quote Accepted", "861", "43.6%", "1,113 (STEEPEST)", "3-5 day quote delay, obscure SKU codes, price pushback"],
                    ["5. KYC Complete", "588", "68.3%", "273", "Manual paperwork fatigue, missing GST/Udyam certificates"],
                    ["6. Activated", "368", "62.6%", "220", "Unpredictable cable delays (>21 days), customer chased status 3x"]
                ]
            },
            "callout": "Key Takeaway: The steepest drop occurs between Needs Assessed and Quote Accepted (1,113 dropped leads, -56.4%). Instant AI multi-product bundling solves this exact chokepoint."
        },
        {
            "num": "Slide 3",
            "title": "Priority MSME Customer Segments",
            "subtitle": "Tailored Solutions for Diverse Small Business Archetypes Across India",
            "cards": [
                ("Micro Retail & Services (55%)", "Kiranas, salons, pharmacies", "Cheap broadband, soundbox/POS, 1-2 SIMs, WhatsApp CRM", "High volume, very price sensitive"),
                ("Professional Offices (25%)", "Clinics, CA firms, coaching centers", "99.9% uptime fiber, Google/Office 365, automated cloud backup", "High margin, medium sensitivity"),
                ("Small Multi-Site Chains (15%)", "Restaurants, retail chains", "Multi-branch fiber, 4G/5G failover (P09), centralized cloud CCTV", "High LTV, low churn"),
                ("Small Manufacturers (5%)", "Auto parts, textiles, fabrication", "1:1 Dedicated Leased Line (P06), IoT machine sensors, firewall", "Strategic high-ARPU accounts")
            ]
        },
        {
            "num": "Slide 4",
            "title": "Proposed Solution & Customer Journey",
            "subtitle": "Seamless End-to-End Digital Experience Under 3 Minutes",
            "points": [
                ("0–30s Voice/Discovery", "Interactive regional advisor (English, Hindi, Tamil) assessing business type, employee count, and digital pain points."),
                ("30–60s Instant Bundling", "Deterministic algorithm generates 3 tailored tiers (Essential, Growth, Advanced) grounded in Accel's 25-SKU catalogue with zero hallucinations."),
                ("60–90s Transparent Quote", "Interactive add-on configurator with dependency validation, real-time 18% GST calculation, and instant PDF download."),
                ("90–150s Smart Digital KYC", "DPDP Act 2023 purpose consent, instant mock GSTIN & Udyam lookups, and OCR defect detection (handling expired utility bills and name mismatches)."),
                ("Day 1–4 Tracked Fulfillment", "Proactive 7-stage order status tracker with assigned field engineer contact details and automatic delay alerts.")
            ]
        },
        {
            "num": "Slide 5",
            "title": "Catalogue-Grounded AI Recommendation Architecture",
            "subtitle": "Mathematical Constraint Solver Grounded in Accel Business Rules",
            "points": [
                ("Zero Hallucination Guarantee", "Strict adherence to product_catalogue.csv. Nonexistent speeds, fabricated prices, and unauthorized discounts are mathematically impossible."),
                ("Geographic Feasibility", "Enforces available_city_tiers (e.g. Leased lines restricted to Tier 1/2 hubs; AirFiber available across all tiers)."),
                ("Business Eligibility Rules", "Automated enforcement of min_employees (e.g. 25+ for P06 Leased Line) and min_sites constraints."),
                ("Prerequisite Dependency Validation", "Enforces requires_one_of rules (e.g. P09 Failover requires primary fiber P01-P06; P22 IoT requires gateway P21)."),
                ("Regulatory Compliance Check", "Flags products requiring mandatory GSTIN (requires_gstin=Y) before contract finalization.")
            ]
        },
        {
            "num": "Slide 6",
            "title": "Smart KYC & Regulatory Transformation",
            "subtitle": "Transforming 5-Day Document Verification into Sub-Minute Digital Assurance",
            "points": [
                ("DPDP Act, 2023 Compliance", "Enforces purpose-bound explicit consent notice (DPDP-2026-V1.0) with immutable audit logging and zero data leakage."),
                ("Sub-Second Registry Lookups", "Instant programmatic validation against 3,534 GSTIN records and 2,723 Udyam certificates in mock databases."),
                ("Intelligent OCR Anomaly Detection", "Detects planted edge cases: expired address proofs (>90 days from 2026-07-15), trade vs. legal name mismatches, cancelled GSTINs, and incomplete scans."),
                ("Prescriptive Error Recovery", "Instead of hard rejection, provides actionable corrective instructions (e.g., 'Upload utility bill dated after April 16, 2026').")
            ]
        },
        {
            "num": "Slide 7",
            "title": "Business Model, Pricing & Value Proposition",
            "subtitle": "Win-Win Economics for Small Business Customers and Accel Business",
            "points": [
                ("Transparent Pricing Formula", "Monthly Recurring = Sum of (Product Unit Prices x Quantity) + 18% GST. No hidden fees or predatory introductory lock-ins."),
                ("Customer Value Proposition", "15–25% savings compared to purchasing broadband, cloud, SIMs, and cybersecurity piecemeal, with unified billing and single-SLA support."),
                ("Operator ARPU Expansion", "Shifts micro-merchants from low-ARPU consumer broadband (₹699) to enterprise bundles averaging ₹2,500–₹7,200/month on 12-month contracted tenures."),
                ("Churn Reduction", "Multi-product bundle stickiness reduces annualized customer churn from 28% to under 9%.")
            ]
        },
        {
            "num": "Slide 8",
            "title": "Partner-Assisted Go-to-Market Strategy",
            "subtitle": "Multiplying Channel Partner Productivity Through Predictive Intelligence",
            "points": [
                ("Synergy, Not Substitution", "Empowers 250+ enterprise channel partners rather than disintermediating them. Sales reps become trusted digital transformation advisors."),
                ("Predictive Lead Scoring Model", "Random Forest classifier evaluates pre-conversion features (lead source, city tier, employee count, GSTIN availability) to prioritize partner callbacks."),
                ("One-Click Journey Recovery", "Partners generate secure 'Resume Journey' links for dropped leads, allowing customers to resume right where they left off."),
                ("Attribution & Protected Commission", "Full commission credited to the originating partner upon digital activation, eliminating channel friction.")
            ]
        },
        {
            "num": "Slide 9",
            "title": "Rollout Plan, Target KPIs & Funnel Impact",
            "subtitle": "Measurable Impact: Baseline Historical vs. UdyamOne Targets",
            "table": {
                "headers": ["Strategic KPI", "Baseline (smb_leads.csv)", "UdyamOne Target Projection", "Business Justification"],
                "rows": [
                    ["Lead-to-Activation Conversion", "7.36% (368 / 5,000)", "24.50% (Target)", "3.3x funnel lift via instant transparent quotes"],
                    ["Sales Cycle Duration", "17.6 Days", "4.5 Days (Target)", "74% cycle compression with self-serve digital KYC"],
                    ["Blended Customer Acquisition Cost", "₹15,000 per SMB", "₹4,800 (Target)", "68% CAC reduction via self-serve onboarding"],
                    ["Customer Status Chase Inquiries", "3.0 calls / lead", "0.3 calls (Target)", "90% support load reduction via 7-stage live tracking"],
                    ["Average Monthly Bundle ARPU", "₹6,900 / month", "₹7,200 (Target)", "Higher cloud & cybersecurity add-on attachment"]
                ]
            },
            "callout": "Rollout Timeline: Phase 1 (M1-M3) in 5 Tier-1 Metros -> Phase 2 (M4-M6) in 15 Industrial Hubs -> Phase 3 (M7-M12) Pan-India."
        },
        {
            "num": "Slide 10",
            "title": "Risk Management & Competitive Safeguards",
            "subtitle": "Proactive Mitigation of Telecom Operational & Market Uncertainties",
            "points": [
                ("Last-Mile Fiber Cabling Delays", "Mitigation: Automatic fallback dispatch of plug-and-play Biz 5G AirFiber (P04) if fiber feasibility exceeds 48 hours."),
                ("Unregistered Micro-Enterprise Funnel Drop", "Mitigation: GSTIN leads convert 4.8x higher in baseline data. Integrated 1-click Udyam registration assistance brings micro-kiranas into the formal economy."),
                ("DPDP Act Privacy Liability", "Mitigation: Built-in granular purpose consent (DPDP-2026-V1.0), TLS 1.3 encryption, automatic data purging, and zero third-party tracking."),
                ("Channel Partner Resistance", "Mitigation: Commission transparency dashboard, guaranteed partner credit, and prioritized lead dispatch.")
            ]
        }
    ]

    for data in slides_data:
        slide = prs.slides.add_slide(prs.slide_layouts[6]) # blank layout

        # Top Accent Line
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = crimson
        top_bar.line.fill.background()

        # Header Box
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_num = tf.paragraphs[0]
        p_num.text = f"{data['num'].upper()} · ACCEL BUSINESS ENTERPRISE ACQUISITION"
        p_num.font.size = Pt(10)
        p_num.font.bold = True
        p_num.font.color.rgb = crimson

        p_title = tf.add_paragraph()
        p_title.text = data["title"]
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = slate_dark

        p_sub = tf.add_paragraph()
        p_sub.text = data["subtitle"]
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = slate_muted

        # Body Content
        if "points" in data:
            left_pos = Inches(0.8)
            top_pos = Inches(1.7)
            width = Inches(11.733)
            height = Inches(5.2)

            box = slide.shapes.add_textbox(left_pos, top_pos, width, height)
            tf_b = box.text_frame
            tf_b.word_wrap = True

            for idx, (head, desc) in enumerate(data["points"]):
                p = tf_b.paragraphs[0] if idx == 0 else tf_b.add_paragraph()
                p.space_before = Pt(12)
                p.space_after = Pt(4)

                run_bullet = p.add_run()
                run_bullet.text = "▪  "
                run_bullet.font.bold = True
                run_bullet.font.size = Pt(13)
                run_bullet.font.color.rgb = crimson

                run_head = p.add_run()
                run_head.text = f"{head}: "
                run_head.font.bold = True
                run_head.font.size = Pt(13)
                run_head.font.color.rgb = slate_dark

                run_desc = p.add_run()
                run_desc.text = desc
                run_desc.font.size = Pt(12.5)
                run_desc.font.color.rgb = slate_muted

        elif "table" in data:
            tbl_info = data["table"]
            rows = len(tbl_info["rows"]) + 1
            cols = len(tbl_info["headers"])
            
            top_pos = Inches(1.7)
            left_pos = Inches(0.8)
            width = Inches(11.733)
            height = Inches(3.8)

            table_shape = slide.shapes.add_table(rows, cols, left_pos, top_pos, width, height)
            table = table_shape.table

            for c_idx, h_text in enumerate(tbl_info["headers"]):
                cell = table.cell(0, c_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = slate_dark
                p = cell.text_frame.paragraphs[0]
                p.text = h_text
                p.font.bold = True
                p.font.size = Pt(11)
                p.font.color.rgb = white

            for r_idx, row_vals in enumerate(tbl_info["rows"]):
                for c_idx, val in enumerate(row_vals):
                    cell = table.cell(r_idx + 1, c_idx)
                    cell.fill.solid()
                    if r_idx % 2 == 0:
                        cell.fill.fore_color.rgb = RGBColor(241, 245, 249)
                    else:
                        cell.fill.fore_color.rgb = white
                    p = cell.text_frame.paragraphs[0]
                    p.text = val
                    p.font.size = Pt(10.5)
                    p.font.color.rgb = slate_dark
                    if "STEEPEST" in val or "3.3x" in val:
                        p.font.bold = True
                        p.font.color.rgb = crimson

            if "callout" in data:
                c_box = slide.shapes.add_textbox(Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.9))
                tf_c = c_box.text_frame
                tf_c.word_wrap = True
                p_c = tf_c.paragraphs[0]
                p_c.text = data["callout"]
                p_c.font.bold = True
                p_c.font.size = Pt(11.5)
                p_c.font.color.rgb = crimson

        elif "cards" in data:
            cards = data["cards"]
            c_width = Inches(5.6)
            c_height = Inches(2.4)
            coords = [
                (Inches(0.8), Inches(1.8)),
                (Inches(6.8), Inches(1.8)),
                (Inches(0.8), Inches(4.5)),
                (Inches(6.8), Inches(4.5))
            ]

            for idx, (title, sub, prod, sens) in enumerate(cards):
                x, y = coords[idx]
                bg_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, c_width, c_height)
                bg_card.fill.solid()
                bg_card.fill.fore_color.rgb = card_bg
                bg_card.line.color.rgb = border_gray

                c_box = slide.shapes.add_textbox(x + Inches(0.2), y + Inches(0.15), c_width - Inches(0.4), c_height - Inches(0.3))
                tf_card = c_box.text_frame
                tf_card.word_wrap = True

                p1 = tf_card.paragraphs[0]
                p1.text = title
                p1.font.bold = True
                p1.font.size = Pt(13)
                p1.font.color.rgb = crimson

                p2 = tf_card.add_paragraph()
                p2.text = f"Archetype: {sub}"
                p2.font.size = Pt(10.5)
                p2.font.bold = True
                p2.font.color.rgb = slate_dark

                p3 = tf_card.add_paragraph()
                p3.text = f"Key Products: {prod}"
                p3.font.size = Pt(10.5)
                p3.font.color.rgb = slate_muted

                p4 = tf_card.add_paragraph()
                p4.text = f"Economics: {sens}"
                p4.font.size = Pt(10)
                p4.font.italic = True
                p4.font.color.rgb = slate_muted

        # Footer
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.733), Inches(0.4))
        tf_f = footer_box.text_frame
        p_foot = tf_f.paragraphs[0]
        p_foot.text = "UdyamOne · Airtel SYNC 2026 Enterprise Track A · Accel Business Confidential Mock Submission"
        p_foot.font.size = Pt(8.5)
        p_foot.font.color.rgb = slate_muted

    prs.save(output_path)
    print(f"Successfully generated 10-slide deck at: {output_path}")

if __name__ == "__main__":
    out = "docs/business-case/UdyamOne_Business_Case_10_Slides.pptx"
    if len(sys.argv) > 1:
        out = sys.argv[1]
    create_deck(out)

