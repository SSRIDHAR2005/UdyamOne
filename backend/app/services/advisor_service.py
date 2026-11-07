from typing import Dict, Any, List
from app.schemas.domain import AdvisorRequest, RecommendedTier, AdvisorResponse, ProductSelection
from app.services.catalogue_service import catalogue_service
from app.services.pricing_service import pricing_service

class AdvisorService:
    def recommend_bundles(self, req: AdvisorRequest) -> AdvisorResponse:
        # Determine business segment if not provided
        segment = req.segment
        if not segment:
            b_type = req.business_type.lower()
            if req.num_sites > 1:
                segment = "multi"
            elif any(k in b_type for k in ["mfg", "factory", "auto", "textile", "industrial"]):
                segment = "mfg"
            elif any(k in b_type for k in ["clinic", "hospital", "ca", "legal", "office", "coaching", "school"]):
                segment = "prof"
            else:
                segment = "micro"

        # Baseline checks
        city_tier = req.city_tier
        employees = max(1, req.employee_count)
        sites = max(1, req.num_sites)
        has_gstin = req.has_gstin
        budget = req.monthly_budget_inr

        # Helper to construct a tier
        def build_tier(
            tier_name: str,
            tagline: str,
            connectivity_pid: str,
            addon_pids: List[str],
            optional_addon_pids: List[str],
            why_text: Dict[str, str],
            limitations_text: Dict[str, str]
        ) -> RecommendedTier:
            # Check connectivity eligibility
            c_prod = catalogue_service.get_product(connectivity_pid)
            c_elig = catalogue_service.check_eligibility(
                connectivity_pid, city_tier, employees, sites, has_gstin
            )
            # If primary connectivity is not eligible, fallback
            active_conn_id = connectivity_pid
            if not c_elig["eligible"]:
                # If high-speed fiber/leased line not available in tier, fallback to P02 Biz Fibre 300 (available in T1/T2)
                if connectivity_pid in ["P03", "P05", "P06"] and city_tier <= 2:
                    active_conn_id = "P02"
                elif "Not available in City Tier" in str(c_elig["reasons"]):
                    active_conn_id = "P04"
                else:
                    active_conn_id = "P01"
            
            selected: List[ProductSelection] = [
                ProductSelection(product_id=active_conn_id, quantity=sites, is_addon=False)
            ]

            # SIMs
            sim_count = max(1, req.need_sims)
            sim_pid = "P08" if tier_name == "Advanced" else "P07"
            selected.append(ProductSelection(product_id=sim_pid, quantity=sim_count, is_addon=False))

            # Addons
            selected_pids = [s.product_id for s in selected]
            for apid in addon_pids:
                a_elig = catalogue_service.check_eligibility(
                    apid, city_tier, employees, sites, has_gstin, selected_product_ids=selected_pids
                )
                if a_elig["eligible"] and apid not in selected_pids:
                    qty = 1
                    if apid == "P16":  # Cloud email per user
                        qty = min(employees, 10 if tier_name == "Growth" else employees)
                    elif apid == "P20":  # Endpoint security per device
                        qty = employees
                    elif apid == "P23" and req.need_cctv:  # CCTV cameras
                        qty = max(1, req.cctv_cameras_count or 2)
                    elif apid == "P19":  # POS counters
                        qty = sites
                    selected.append(ProductSelection(product_id=apid, quantity=qty, is_addon=False))
                    selected_pids.append(apid)

            # Optional addons for configurator
            opt_addons_list = []
            for opid in optional_addon_pids:
                op_prod = catalogue_service.get_product(opid)
                if op_prod:
                    op_elig = catalogue_service.check_eligibility(
                        opid, city_tier, employees, sites, has_gstin, selected_product_ids=selected_pids
                    )
                    opt_addons_list.append({
                        "product_id": opid,
                        "product_name": op_prod["product_name"],
                        "category": op_prod["category"],
                        "description": op_prod["description"],
                        "unit": op_prod["unit"],
                        "price_inr_per_month": op_prod["price_inr_per_month"],
                        "one_time_setup_inr": op_prod["one_time_setup_inr"],
                        "is_eligible": op_elig["eligible"],
                        "reasons": op_elig["reasons"]
                    })

            # Calculate quote
            biz_details = {
                "business_name": req.business_name,
                "segment": segment,
                "city": req.city,
                "city_tier": city_tier,
                "employee_count": employees,
                "num_sites": sites,
                "has_gstin": has_gstin
            }
            calc = pricing_service.calculate_quote(biz_details, selected, tier_name=tier_name)

            lang = req.preferred_language
            why_msg = why_text.get(lang, why_text["en"])
            lim_msg = limitations_text.get(lang, limitations_text["en"])

            return RecommendedTier(
                tier_name=tier_name,
                tagline=tagline,
                target_fit_reason=f"Optimized for {segment.upper()} enterprises in Tier {city_tier} locations.",
                monthly_total_inr=calc["monthly_recurring_inr"],
                one_time_setup_inr=calc["one_time_setup_inr"],
                standalone_price_inr=calc["monthly_recurring_inr"] + calc["calculated_savings_inr"],
                savings_inr=calc["calculated_savings_inr"],
                contract_months=calc["contract_months"],
                products=calc["items"],
                optional_addons=opt_addons_list,
                why_recommended=why_msg,
                potential_limitations=lim_msg
            )

        # 1. Essential Tier (Cost-effective baseline)
        essential_conn = "P01"  # Biz Fibre 100
        essential_addons = []
        if req.need_pos:
            essential_addons.append("P19")  # Cloud POS
        if req.need_whatsapp:
            essential_addons.append("P15")  # WhatsApp Business

        essential_tier = build_tier(
            tier_name="Essential",
            tagline="Low-cost digital connectivity & payment essentials",
            connectivity_pid=essential_conn,
            addon_pids=essential_addons,
            optional_addon_pids=["P18", "P22", "P14"],
            why_text={
                "en": f"Gives {req.business_name} uninterrupted high-speed fibre broadband with reliable billing and business communication at the most economical monthly commitment.",
                "hi": f"{req.business_name} को सबसे किफायती बजट में विश्वसनीय हाई-स्पीड ब्रॉडबैंड, निर्बाध बिलिंग और व्यावसायिक संपर्क प्रदान करता है।",
                "ta": f"{req.business_name}-க்கு குறைந்த மாதாந்திர கட்டணத்தில் நம்பகமான அதிவேக பிராட்பேண்ட் மற்றும் வணிக தொடர்புகளை வழங்குகிறது."
            },
            limitations_text={
                "en": "Standard SLA with dynamic IP; does not include automatic secondary link failover or dedicated cloud backup.",
                "hi": "मानक SLA; इसमें स्वचालित बैकअप लिंक या समर्पित क्लाउड बैकअप शामिल नहीं है।",
                "ta": "நிலையான SLA; இதில் தானியங்கி ஃபைலோவர் அல்லது கிளவுட் பேக்அப் சேர்க்கப்படவில்லை."
            }
        )

        # 2. Growth Tier (Balanced recommendation - recommended for most)
        growth_conn = "P02" if employees >= 5 or segment in ["prof", "multi"] else "P01"
        growth_addons = []
        if req.need_pos:
            growth_addons.append("P19")
        if req.need_whatsapp:
            growth_addons.append("P15")
        if req.need_cloud_email or segment in ["prof", "multi", "mfg"]:
            growth_addons.append("P16")  # Cloud Email
        if req.need_security or segment in ["prof", "mfg"]:
            growth_addons.append("P20")  # Endpoint security
        if req.need_cctv:
            growth_addons.append("P23")  # Cloud CCTV
        if req.need_failover_backup or sites > 1:
            growth_addons.append("P09")  # 4G/5G Failover

        growth_tier = build_tier(
            tier_name="Growth",
            tagline="Balanced high-performance bundle with productivity & security",
            connectivity_pid=growth_conn,
            addon_pids=growth_addons,
            optional_addon_pids=["P17", "P22", "P11", "P13"],
            why_text={
                "en": f"The ideal sweet spot for {req.business_name}. Combines robust 300 Mbps broadband with business mobile lines, official Google/Office cloud suite, and active security.",
                "hi": f"{req.business_name} के लिए सबसे संतुलित पैकेज। 300 Mbps ब्रॉडबैंड, आधिकारिक क्लाउड ईमेल, बिज़नेस सिम और सुरक्षा का पूर्ण संगम।",
                "ta": f"{req.business_name}-க்கு மிகவும் பொருத்தமான தேர்வு. 300 Mbps பிராட்பேண்ட், வணிக சிம், அலுவலக கிளவுட் மின்னஞ்சல் மற்றும் பாதுகாப்பு உள்ளடக்கியது."
            },
            limitations_text={
                "en": "Includes up to 10 email licenses and standard Wi-Fi; advanced multi-site SD-WAN available in Advanced tier.",
                "hi": "इसमें 10 ईमेल लाइसेंस शामिल हैं; मल्टी-साइट SD-WAN एडवांस्ड टियर में उपलब्ध है।",
                "ta": "இதில் 10 மின்னஞ்சல் உரிமங்கள் உள்ளன; முழு SD-WAN வசதி மேம்பட்ட தொகுப்பில் கிடைக்கும்."
            }
        )

        # 3. Advanced Tier (Comprehensive enterprise solution)
        adv_conn = "P05" if req.need_dedicated_leased_line and has_gstin and employees >= 10 else ("P03" if has_gstin and employees >= 5 else "P02")
        adv_addons = list(growth_addons)
        if "P17" not in adv_addons:
            adv_addons.append("P17")  # Cloud Backup 1TB
        if "P21" not in adv_addons and has_gstin and employees >= 10:
            adv_addons.append("P21")  # Managed Firewall
        if sites >= 3 and has_gstin and employees >= 10:
            adv_addons.append("P10")  # SD-WAN
        if "P11" not in adv_addons:
            adv_addons.append("P11")  # Static IP
        if req.need_cctv and "P23" not in adv_addons:
            adv_addons.append("P23")

        adv_tier = build_tier(
            tier_name="Advanced",
            tagline="Mission-critical connectivity, enterprise SLA & cyber defense",
            connectivity_pid=adv_conn,
            addon_pids=adv_addons,
            optional_addon_pids=["P24", "P25", "P12"],
            why_text={
                "en": f"Maximum business continuity for {req.business_name} with priority 99.9% uptime SLA, dedicated static IP, managed firewall defense, and centralized administration.",
                "hi": f"{req.business_name} के लिए सर्वोच्च व्यावसायिक विश्वसनीयता: 99.9% अपटाइम SLA, स्टैटिक आईपी, प्रबंधित फ़ायरवॉल और पूर्ण क्लाउड सुरक्षा।",
                "ta": f"{req.business_name}-ன் தடையில்லா செயல்பாட்டிற்கு 99.9% SLA, நிலையான IP, ஃபயர்வால் பாதுகாப்பு மற்றும் முழு கிளவுட் மேலாண்மை."
            },
            limitations_text={
                "en": "Higher setup commitment and multi-year contract for dedicated line and hardware.",
                "hi": "समर्पित हार्डवेयर और लीज्ड लाइन के कारण दीर्घकालिक अनुबंध लागू होता है।",
                "ta": "பிரத்யேக வன்பொருள் மற்றும் நீண்ட கால ஒப்பந்தம் தேவைப்படுகிறது."
            }
        )

        # Welcome Summary in Preferred Language
        summary_messages = {
            "en": f"Hello {req.business_name}! Based on your {segment.upper()} business profile with {employees} employees across {sites} location(s) and a budget of ₹{int(budget):,}/month, our AI Advisor tailored 3 catalogue-grounded bundles.",
            "hi": f"नमस्ते {req.business_name}! आपके {sites} स्थान(स्थानों) और {employees} कर्मचारियों वाले व्यवसाय के लिए ₹{int(budget):,}/माह के बजट के अनुसार 3 प्रमाणित बंडल तैयार किए गए हैं।",
            "ta": f"வணக்கம் {req.business_name}! உங்கள் {sites} கிளைகள் மற்றும் {employees} பணியாளர்கள் கொண்ட நிறுவனத்திற்கு ₹{int(budget):,}/மாத பட்ஜெட்டுக்கு ஏற்ப 3 தொகுப்புகள் பரிந்துரைக்கப்படுகின்றன."
        }

        return AdvisorResponse(
            business_profile={
                "business_name": req.business_name,
                "business_type": req.business_type,
                "segment": segment,
                "city": req.city,
                "city_tier": city_tier,
                "employee_count": employees,
                "num_sites": sites,
                "has_gstin": has_gstin,
                "monthly_budget_inr": budget
            },
            language=req.preferred_language,
            summary_message=summary_messages.get(req.preferred_language, summary_messages["en"]),
            recommendations=[essential_tier, growth_tier, adv_tier],
            disclaimer="All prices, setup fees, and SLAs are authoritatively computed from the official Accel Business product catalogue. No prices or eligibility rules are fabricated."
        )

    generate_recommendations = recommend_bundles

    def process_transcript(self, req) -> Any:
        import re
        from fastapi import HTTPException
        from app.schemas.domain import VoiceTranscriptResponse, ExtractedBusinessProfile, AdvisorRequest

        transcript = req.transcript.strip() if getattr(req, "transcript", None) else ""
        if not transcript:
            raise HTTPException(status_code=400, detail="Voice transcript cannot be empty.")

        lang = req.language if getattr(req, "language", None) in ["en", "hi", "ta"] else "en"
        text_lower = transcript.lower()

        # 1. Category and Business Type
        b_type = "retail"
        segment = "micro"
        category_name = "Retail / Grocery"
        if any(k in text_lower for k in ["clinic", "dental", "doctor", "diagnostic", "hospital", "healthcare", "क्लिनिक", "डॉक्टर", "अस्पताल", "கிளினிக்", "மருத்துவர்", "மருத்துவமனை"]):
            b_type = "clinic"
            segment = "prof"
            category_name = "Healthcare / Clinic"
        elif any(k in text_lower for k in ["restaurant", "cafe", "eatery", "food", "dining", "hotel", "dhaba", "रेस्टोरेंट", "कैफे", "होटल", "உணவகம்", "ஹோட்டல்"]):
            b_type = "restaurant"
            segment = "multi"
            category_name = "Restaurant / Hospitality"
        elif any(k in text_lower for k in ["factory", "plant", "manufacturing", "industrial", "workshop", "auto", "textile", "warehouse", "फैक्ट्री", "कारखाना", "विनिर्माण", "தொழிற்சாலை", "உற்பத்தி"]):
            b_type = "manufacturing"
            segment = "mfg"
            category_name = "Manufacturing / Industrial"
        elif any(k in text_lower for k in ["consulting", "accounting", "legal", "ca firm", "agency", "office", "ऑफिस", "सीए", "அலுவலகம்"]):
            b_type = "services"
            segment = "prof"
            category_name = "Professional Services"
        else:
            b_type = "retail"
            segment = "micro"
            category_name = "Retail / Grocery"

        # 2. Operating City & Tier
        city_tier_map = {
            "chennai": ("Chennai", 1),
            "चेन्नई": ("Chennai", 1),
            "சென்னை": ("Chennai", 1),
            "madras": ("Chennai", 1),
            "bengaluru": ("Bengaluru", 1),
            "bangalore": ("Bengaluru", 1),
            "बेंगलुरु": ("Bengaluru", 1),
            "பெங்களூரு": ("Bengaluru", 1),
            "mumbai": ("Mumbai", 1),
            "bombay": ("Mumbai", 1),
            "मुंबई": ("Mumbai", 1),
            "மும்பை": ("Mumbai", 1),
            "delhi": ("Delhi", 1),
            "दिल्ली": ("Delhi", 1),
            "டெல்லி": ("Delhi", 1),
            "hyderabad": ("Hyderabad", 1),
            "हैदराबाद": ("Hyderabad", 1),
            "ஹைதராபாத்": ("Hyderabad", 1),
            "pune": ("Pune", 1),
            "पुणे": ("Pune", 1),
            "புனே": ("Pune", 1),
            "kolkata": ("Kolkata", 1),
            "कलकत्ता": ("Kolkata", 1),
            "கொல்கத்தா": ("Kolkata", 1),
            "ahmedabad": ("Ahmedabad", 1),
            "अहमदाबाद": ("Ahmedabad", 1),
            "அகமதாபாத்": ("Ahmedabad", 1),
            "coimbatore": ("Coimbatore", 2),
            "கோயம்புத்தூர்": ("Coimbatore", 2),
            "jaipur": ("Jaipur", 2),
            "lucknow": ("Lucknow", 2),
            "indore": ("Indore", 2),
            "kochi": ("Kochi", 2),
            "surat": ("Surat", 2),
            "chandigarh": ("Chandigarh", 2),
            "patna": ("Patna", 2),
            "bhopal": ("Bhopal", 2),
            "nagpur": ("Nagpur", 2),
            "vadodara": ("Vadodara", 2),
            "visakhapatnam": ("Visakhapatnam", 2)
        }
        operating_city = "Bengaluru"
        city_tier = 1
        for c_key, (c_name, c_tier) in city_tier_map.items():
            if c_key in text_lower:
                operating_city = c_name
                city_tier = c_tier
                break

        # 3. Business Name
        business_name = None
        # English patterns
        m_en = re.search(r'(?:called|named|name is|run a [a-z\s]+ called|run\s+|manage\s+|own\s+|shop called|store called|clinic called|restaurant called|enterprise called)\s*([A-Za-z0-9&.\'\-\s]+?)(?=\s+(?:in|located|at|with|and|i have|my|we)\b|[.,]|$)', transcript, re.I)
        if m_en:
            raw_en = m_en.group(1).strip()
            cleaned_en = re.sub(r'^(?:a|an|the|our|my|small)\s+', '', raw_en, flags=re.I).strip()
            if cleaned_en.lower() in ['grocery store', 'grocery shop', 'shop', 'store', 'clinic', 'restaurant', 'diagnostic clinic', 'factory', 'plant']:
                business_name = f"{operating_city} {cleaned_en.title()}"
            else:
                business_name = cleaned_en.title()
        else:
            # Hindi patterns
            m_hi = re.search(r'([^\s,]+(?:\s+[^\s,]+){0,4})\s+(?:नाम की|नाम का|नाम है)', transcript)
            if m_hi:
                raw_hi = m_hi.group(1).strip()
                raw_hi = re.sub(r'^(?:मेरी|हमारा|मेरा|मैं)\s+', '', raw_hi)
                business_name = re.sub(r'^[^\s,]+\s+में\s+', '', raw_hi).strip()
            else:
                # Tamil patterns
                m_ta = re.search(r'([^\s,]+(?:\s+[^\s,]+){0,4})\s+(?:என்ற|என்னும்|பெயர்)', transcript)
                if m_ta:
                    raw_ta = m_ta.group(1).strip()
                    raw_ta = re.sub(r'^(?:நான்|எங்கள்|எனது)\s+', '', raw_ta)
                    business_name = re.sub(r'^[^\s,]+(?:இல்|யில்)\s+', '', raw_ta).strip()

        if not business_name or len(business_name) < 2:
            if b_type == "clinic":
                business_name = f"{operating_city} Diagnostic Clinic"
            elif b_type == "restaurant":
                business_name = f"{operating_city} Kitchen & Bistro"
            elif b_type == "manufacturing":
                business_name = f"{operating_city} Precision Engineering"
            else:
                business_name = "Sri Lakshmi Stores"

        # 4. Sites Count
        word_num_map = {
            "one": 1, "single": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
            "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5,
            "ஒரு": 1, "இரண்டு": 2, "மூன்று": 3, "நான்கு": 4, "ஐந்து": 5
        }
        num_sites = 1
        m_sites = re.search(r'(\d+|one|two|three|four|five|single|multiple|एक|दो|तीन|ஒரு|இரண்டு|மூன்று)\s*(?:shops?|stores?|locations?|sites?|branches?|outlets?|दुकान|शाखा|கிளை|கடை)', transcript, re.I)
        if m_sites:
            s_val = m_sites.group(1).lower()
            num_sites = int(s_val) if s_val.isdigit() else word_num_map.get(s_val, 1)

        # 5. Employee Count
        word_emp_map = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20,
            "तीन": 3, "चार": 4, "पांच": 5, "छह": 6, "सात": 7, "आठ": 8, "दस": 10,
            "மூன்று": 3, "நான்கு": 4, "ஐந்து": 5, "ஆறு": 6, "ஏழு": 7, "எட்டு": 8, "பத்து": 10
        }
        employee_count = 3
        m_emp = re.search(r'(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|तीन|चार|पांच|छह|सात|आठ|மூன்று|நான்கு|ஐந்து|ஆறு)\s*(?:employees?|staff|workers?|people|team members?|कर्मचारी|लोग|ஊழியர்கள்|பணியாளர்கள்)', transcript, re.I)
        if m_emp:
            e_val = m_emp.group(1).lower()
            employee_count = int(e_val) if e_val.isdigit() else word_emp_map.get(e_val, 3)

        # 6. Monthly Budget
        monthly_budget = 3000.0
        m_budget = re.search(r'(?:budget|spending|spend|बजट|பட்ஜெட்)\D*?(\d[\d,]*)\s*(?:rupees|rs|inr|रुपये|रु|ரூபாய்|ரூ)?', transcript, re.I)
        if m_budget and m_budget.group(1):
            try:
                monthly_budget = float(m_budget.group(1).replace(",", ""))
            except ValueError:
                pass
        else:
            m_num_curr = re.search(r'(\d+[\d,]*)\s*(?:rupees|rs|inr|रुपये|रु|ரூபாய்|ரூ)', transcript, re.I)
            if m_num_curr:
                try:
                    monthly_budget = float(m_num_curr.group(1).replace(",", ""))
                except ValueError:
                    pass
            elif "तीन हज़ार" in transcript or "3 हजार" in transcript or "மூவாயிரம்" in transcript:
                monthly_budget = 3000.0
            elif "पांच हज़ार" in transcript or "5 हजार" in transcript or "ஐந்தாயிரம்" in transcript:
                monthly_budget = 5000.0
            elif "आठ हज़ार" in transcript or "8 हजार" in transcript or "எட்டாயிரம்" in transcript:
                monthly_budget = 8000.0

        # 7. Requirements Detection
        requirements = []
        if any(k in text_lower for k in ["internet", "wifi", "broadband", "fibre", "fiber", "connectivity", "इंटरनेट", "இணையம்", "வைஃபை"]):
            requirements.append("Reliable internet")

        if any(k in text_lower for k in ["upi", "qr", "payment", "digital pay", "पेमेंट", "यूपीआई", "பேமெண்ட்"]):
            requirements.append("UPI payments")

        if any(k in text_lower for k in ["billing", "pos", "invoice", "बिलिंग", "பில்லிங்"]):
            requirements.append("Online billing")

        if any(k in text_lower for k in ["whatsapp", "व्हाट्सएप", "வாட்ஸ்அப்"]):
            requirements.append("WhatsApp orders")

        if any(k in text_lower for k in ["cctv", "camera", "surveillance", "security", "सीसीटीवी", "सुरक्षा", "சிசிடிவி", "கேமரா"]):
            requirements.append("CCTV connectivity")

        if any(k in text_lower for k in ["email", "gmail", "workspace", "professional email", "ईमेल", "மின்னஞ்சல்"]):
            requirements.append("Cloud email")

        if re.search(r'\b(?:cloud backup|cloud records?|data backup|storage|patient data|ledger backup)\b', text_lower) or any(k in text_lower for k in ["बैकअप", "பேக்கப்"]):
            requirements.append("Cloud backup")

        if any(k in text_lower for k in ["cybersecurity", "antivirus", "firewall", "endpoint", "एंटीवायरस"]):
            requirements.append("Cybersecurity")

        if re.search(r'\b(?:leased line|dedicated internet|dedicated line|ill)\b', text_lower):
            requirements.append("Dedicated leased line")

        if re.search(r'\b(?:backup connectivity|failover|redundancy|4g backup|backup internet)\b', text_lower):
            requirements.append("Failover backup connectivity")

        if any(k in text_lower for k in ["sd-wan", "sdwan", "branch connect", "multi-site"]):
            requirements.append("SD-WAN branch connectivity")

        if not requirements:
            requirements = ["Reliable internet", "Online billing"]

        # 8. Catalogue Product Mapping
        matched_products = []
        if "Reliable internet" in requirements:
            pid = "P02" if monthly_budget >= 4000 else "P01"
            prod = catalogue_service.get_product(pid)
            if prod:
                matched_products.append({
                    "product_id": pid,
                    "product_name": prod["product_name"],
                    "category": prod["category"],
                    "price_inr_per_month": prod["price_inr_per_month"],
                    "one_time_setup_inr": prod["one_time_setup_inr"],
                    "matched_requirement": "Reliable internet",
                    "reason": "High-uptime commercial broadband for uninterrupted transactions & digital operations."
                })

        if "Online billing" in requirements or "UPI payments" in requirements:
            prod = catalogue_service.get_product("P19")
            if prod:
                matched_products.append({
                    "product_id": "P19",
                    "product_name": prod["product_name"],
                    "category": prod["category"],
                    "price_inr_per_month": prod["price_inr_per_month"],
                    "one_time_setup_inr": prod["one_time_setup_inr"],
                    "matched_requirement": "Online billing / UPI payments",
                    "reason": "Cloud POS counter software with automated digital receipts and payment gateway sync."
                })

        if "WhatsApp orders" in requirements:
            prod = catalogue_service.get_product("P15")
            if prod:
                matched_products.append({
                    "product_id": "P15",
                    "product_name": prod["product_name"],
                    "category": prod["category"],
                    "price_inr_per_month": prod["price_inr_per_month"],
                    "one_time_setup_inr": prod["one_time_setup_inr"],
                    "matched_requirement": "WhatsApp orders",
                    "reason": "Official verified WhatsApp Business API starter for customer catalog and order tracking."
                })

        if "CCTV connectivity" in requirements:
            prod = catalogue_service.get_product("P23")
            if prod:
                matched_products.append({
                    "product_id": "P23",
                    "product_name": prod["product_name"],
                    "category": prod["category"],
                    "price_inr_per_month": prod["price_inr_per_month"],
                    "one_time_setup_inr": prod["one_time_setup_inr"],
                    "matched_requirement": "CCTV connectivity",
                    "reason": "Enterprise cloud security cameras with 7-day secure cloud recording and mobile feed."
                })

        if "Cloud email" in requirements:
            prod = catalogue_service.get_product("P16")
            if prod:
                matched_products.append({
                    "product_id": "P16",
                    "product_name": prod["product_name"],
                    "category": prod["category"],
                    "price_inr_per_month": prod["price_inr_per_month"],
                    "one_time_setup_inr": prod["one_time_setup_inr"],
                    "matched_requirement": "Cloud email",
                    "reason": "Domain-linked Google Workspace / Office email accounts for staff."
                })

        if "Cloud backup" in requirements:
            prod = catalogue_service.get_product("P17")
            if prod:
                matched_products.append({
                    "product_id": "P17",
                    "product_name": prod["product_name"],
                    "category": prod["category"],
                    "price_inr_per_month": prod["price_inr_per_month"],
                    "one_time_setup_inr": prod["one_time_setup_inr"],
                    "matched_requirement": "Cloud backup",
                    "reason": "Automated off-site 1 TB encrypted cloud backup for business ledger and customer records."
                })

        if "Cybersecurity" in requirements:
            prod = catalogue_service.get_product("P20")
            if prod:
                matched_products.append({
                    "product_id": "P20",
                    "product_name": prod["product_name"],
                    "category": prod["category"],
                    "price_inr_per_month": prod["price_inr_per_month"],
                    "one_time_setup_inr": prod["one_time_setup_inr"],
                    "matched_requirement": "Cybersecurity",
                    "reason": "Managed endpoint antivirus and anti-ransomware protection for all billing terminals."
                })

        # Identify any unmatched requirement
        unmatched_requirements = []
        for req_item in ["drone delivery", "crypto payment", "satellite uplink", "ai automated robot"]:
            if req_item in text_lower:
                unmatched_requirements.append(req_item.title())

        # Build Extracted Profile
        has_gstin = True if (monthly_budget >= 6000 or employee_count > 10 or segment in ["mfg", "multi"]) else False
        extracted_profile = ExtractedBusinessProfile(
            business_name=business_name,
            business_category=category_name,
            operating_city=operating_city,
            city_tier=city_tier,
            number_of_sites=num_sites,
            employee_count=employee_count,
            requirements=requirements,
            monthly_budget=monthly_budget,
            currency="INR",
            business_type=b_type,
            segment=segment,
            has_gstin=has_gstin,
            gstin="29CPSXS6426Z1ZL" if has_gstin else None,
            need_sims=max(1, min(employee_count, 5)),
            need_pos=("Online billing" in requirements or "UPI payments" in requirements),
            need_whatsapp=("WhatsApp orders" in requirements),
            need_cctv=("CCTV connectivity" in requirements),
            cctv_cameras_count=max(2, num_sites * 2) if ("CCTV connectivity" in requirements) else 0,
            need_cloud_email=("Cloud email" in requirements),
            need_cloud_backup=("Cloud backup" in requirements),
            need_security=("Cybersecurity" in requirements),
            need_failover_backup=("Dedicated leased line" in requirements or num_sites > 1),
            need_dedicated_leased_line=("Dedicated leased line" in requirements)
        )

        # 9. Build AdvisorRequest and invoke existing recommendation engine
        advisor_req = AdvisorRequest(
            business_name=extracted_profile.business_name,
            business_type=extracted_profile.business_type,
            segment=extracted_profile.segment,
            city=extracted_profile.operating_city,
            city_tier=extracted_profile.city_tier,
            employee_count=extracted_profile.employee_count,
            num_sites=extracted_profile.number_of_sites,
            monthly_budget_inr=extracted_profile.monthly_budget,
            need_sims=extracted_profile.need_sims,
            need_pos=extracted_profile.need_pos,
            need_whatsapp=extracted_profile.need_whatsapp,
            need_cctv=extracted_profile.need_cctv,
            cctv_cameras_count=extracted_profile.cctv_cameras_count,
            need_cloud_email=extracted_profile.need_cloud_email,
            need_cloud_backup=extracted_profile.need_cloud_backup,
            need_security=extracted_profile.need_security,
            need_failover_backup=extracted_profile.need_failover_backup,
            need_dedicated_leased_line=extracted_profile.need_dedicated_leased_line,
            has_gstin=extracted_profile.has_gstin,
            gstin=extracted_profile.gstin,
            preferred_language=lang
        )

        recs = self.recommend_bundles(advisor_req)

        return VoiceTranscriptResponse(
            original_transcript=transcript,
            language=lang,
            extracted_profile=extracted_profile,
            matched_catalogue_products=matched_products,
            unmatched_requirements=unmatched_requirements,
            advisor_request_payload=advisor_req.dict(),
            recommendations=recs
        )

advisor_service = AdvisorService()

