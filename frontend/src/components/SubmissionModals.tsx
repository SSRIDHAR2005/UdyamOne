import React from 'react';
import { X, Layers, FileText, Shield, Video, CheckCircle2, ChevronRight, ChevronLeft } from 'lucide-react';

interface ModalProps {
  type: 'architecture' | 'business_case' | 'privacy' | 'script' | null;
  onClose: () => void;
}

export const SubmissionModals: React.FC<ModalProps> = ({ type, onClose }) => {
  const [currentSlide, setCurrentSlide] = React.useState(1);

  if (!type) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden border border-slate-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-900 text-white">
          <div className="flex items-center gap-2">
            {type === 'architecture' && <Layers className="w-5 h-5 text-red-400" />}
            {type === 'business_case' && <FileText className="w-5 h-5 text-amber-400" />}
            {type === 'privacy' && <Shield className="w-5 h-5 text-emerald-400" />}
            {type === 'script' && <Video className="w-5 h-5 text-sky-400" />}
            <span className="font-bold text-sm">
              {type === 'architecture' && 'Deliverable 2: Solution Architecture Blueprint'}
              {type === 'business_case' && 'Deliverable 3: Business Case (10-Slide Pitch Presentation)'}
              {type === 'privacy' && 'Deliverable 4: One-Page Privacy & Security Note (DPDP Act, 2023)'}
              {type === 'script' && 'Deliverable 1: Three-Minute Video Pitch & Demo Script'}
            </span>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Area */}
        <div className="p-6 sm:p-8 overflow-y-auto flex-1 text-slate-800 text-xs leading-relaxed space-y-6">
          {type === 'architecture' && (
            <div className="space-y-6">
              <div className="bg-red-50 p-4 rounded-xl border border-red-200 text-xs text-red-900">
                <strong>Architectural Vision:</strong> UdyamOne is a production-grade decoupled system. The React 18+ client handles mobile-first conversational discovery and rich self-service configurators, while the Python FastAPI backend serves as the single source of truth for catalogue rules, dependency trees, DPDP consent tracking, and OCR validation.
              </div>

              {/* Architecture Diagram Representation */}
              <div className="p-5 rounded-2xl bg-slate-900 text-white font-mono text-[11px] space-y-4 overflow-x-auto shadow-inner">
                <div className="border border-slate-700 rounded-xl p-3 bg-slate-800/80">
                  <span className="text-red-400 font-bold block mb-1">1. CLIENT LAYER (React 18 + Vite + TypeScript + Tailwind)</span>
                  <p className="text-slate-300">├── MSME Business Portal: AI Advisor (Multilingual EN/HI/TA), Bundle Configurator, Smart KYC, Tracker</p>
                  <p className="text-slate-300">└── Partner Operations Portal: Lead Funnel Management, ML Risk Prioritization, Recovery Link Generator</p>
                </div>

                <div className="flex justify-center text-slate-400">▼ REST API / HTTPS JSON (OpenAPI v3) ▼</div>

                <div className="border border-slate-700 rounded-xl p-3 bg-slate-800/80">
                  <span className="text-emerald-400 font-bold block mb-1">2. FASTAPI BACKEND GATEWAY & CORE ENGINES</span>
                  <p className="text-slate-300">├── Catalogue Engine: product_catalogue.csv (25 SKUs, dependency validator requires_one_of, tier eligibility)</p>
                  <p className="text-slate-300">├── Pricing & Quote Service: Real-time recalculation (Σ products), 18% GST calculation, quote expiry persistence</p>
                  <p className="text-slate-300">├── Advisor Engine: Hybrid rules + catalogue constraint solver (Essential, Growth, Advanced tiers)</p>
                  <p className="text-slate-300">├── Smart Digital KYC Engine: Mock GSTIN (3,534 records), Mock Udyam (2,723 records), Windows Media OCR & regex</p>
                  <p className="text-slate-300">└── Predictive Lead Intelligence: Scikit-learn Random Forest model (trained strictly on pre-conversion signals)</p>
                </div>

                <div className="flex justify-center text-slate-400">▼ Local Cache & Registry Backing ▼</div>

                <div className="border border-slate-700 rounded-xl p-3 bg-slate-800/80">
                  <span className="text-sky-400 font-bold block mb-1">3. DATA LAYER (SQLite / PostgreSQL Compatible + Ground Truth CSVs)</span>
                  <p className="text-slate-300">├── mock_gstin_registry.csv (3,534 Active, Cancelled, Suspended records)</p>
                  <p className="text-slate-300">├── mock_udyam_registry.csv (2,723 MSME classifications)</p>
                  <p className="text-slate-300">├── smb_leads.csv (5,000 leads, funnel benchmarks & drop reasons)</p>
                  <p className="text-slate-300">└── kyc_documents/ (47 specimen images, K01-K12 planted test cases)</p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl border border-slate-200 bg-slate-50">
                  <h4 className="font-bold text-slate-900 text-xs mb-1">Security & DPDP Governance</h4>
                  <p className="text-slate-600">Granular purpose-specific consent recorded with timestamp and versioning. No Aadhaar biometric storage; simulated third-party mock registries.</p>
                </div>
                <div className="p-4 rounded-xl border border-slate-200 bg-slate-50">
                  <h4 className="font-bold text-slate-900 text-xs mb-1">Resilience & Performance</h4>
                  <p className="text-slate-600">Sub-50ms API response time with zero external network blocking. Authoritative fallback recommendation engine functions seamlessly offline.</p>
                </div>
              </div>
            </div>
          )}

          {type === 'business_case' && (
            <div className="space-y-6">
              {/* Carousel Slide Controller */}
              <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                <span className="font-bold text-xs uppercase text-red-600">
                  Slide {currentSlide} of 10
                </span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setCurrentSlide(Math.max(1, currentSlide - 1))}
                    disabled={currentSlide === 1}
                    className="p-1 rounded bg-slate-100 hover:bg-slate-200 disabled:opacity-40 cursor-pointer"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setCurrentSlide(Math.min(10, currentSlide + 1))}
                    disabled={currentSlide === 10}
                    className="p-1 rounded bg-slate-100 hover:bg-slate-200 disabled:opacity-40 cursor-pointer"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* 10-Slide Deck */}
              {currentSlide === 1 && (
                <div className="space-y-3 p-4 bg-slate-50 rounded-2xl border border-slate-200">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Slide 1: Executive Summary</span>
                  <h3 className="text-xl font-black text-slate-900">UdyamOne: Unlocking India's 6 Crore+ MSME Market</h3>
                  <p className="text-slate-600 text-xs leading-relaxed">
                    Accel Business serves large enterprises with high touch, but small businesses need one seamless digital journey. Today, SMB acquisition yields only <strong>7.36% activation</strong> (368 out of 5,000 leads) at an unsustainably high blended CAC of <strong>₹15,000</strong>. UdyamOne delivers <strong>One Conversation. One Smart Bundle. One Connected Business</strong>, compressing onboarding from 17.6 days down to 4.5 days.
                  </p>
                </div>
              )}

              {currentSlide === 2 && (
                <div className="space-y-3 p-4 bg-slate-50 rounded-2xl border border-slate-200">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Slide 2: Funnel Diagnosis</span>
                  <h3 className="text-xl font-black text-slate-900">The Core Bottleneck: Needs Assessed to Quote Accepted</h3>
                  <p className="text-slate-600 text-xs leading-relaxed">
                    In the historical baseline, <strong>1,113 leads drop out (56% drop)</strong> immediately after needs assessment. The root causes are systemic: quotes take 3–5 days to arrive, arrive with technical product codes owners cannot understand, and bundle prices are perceived as opaque without modular customization.
                  </p>
                </div>
              )}

              {currentSlide === 3 && (
                <div className="space-y-3 p-4 bg-slate-50 rounded-2xl border border-slate-200">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Slide 3: Priority MSME Segments</span>
                  <h3 className="text-xl font-black text-slate-900">Target Strategy Across 4 Distinct MSME Tiers</h3>
                  <ul className="space-y-2 text-xs text-slate-700">
                    <li>• <strong>Micro Retail (55% Base):</strong> Kirana/Salons. Very high price sensitivity. Bundle: Biz Fibre 100 + Cloud POS + WhatsApp API (₹2,597/mo).</li>
                    <li>• <strong>Professional Offices (25% Base):</strong> Clinics, CA firms. Medium price sensitivity. High margin. Bundle: Biz Fibre 300 + Cloud Email + Endpoint Security (₹4,500/mo).</li>
                    <li>• <strong>Multi-Site Retail (15% Base):</strong> Restaurant chains. Bundle: SD-WAN + 4G Failover + Central CCTV (₹12,000/mo).</li>
                    <li>• <strong>Small Manufacturers (5% Base):</strong> Auto parts units. Bundle: Dedicated Leased Line 20 Mbps + Machine IoT sensors (₹35,000/mo).</li>
                  </ul>
                </div>
              )}

              {currentSlide === 4 && (
                <div className="space-y-3 p-4 bg-slate-50 rounded-2xl border border-slate-200">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Slide 4: The Digital Solution</span>
                  <h3 className="text-xl font-black text-slate-900">Self-Service Customer Journey in 4 Frictionless Steps</h3>
                  <p className="text-slate-600 text-xs leading-relaxed">
                    1. <strong>AI Advisor:</strong> Progressive questioning in English, Hindi, or Tamil yields 3 comparison tiers (Essential, Growth, Advanced).<br/>
                    2. <strong>Smart Quote:</strong> Real-time transparent configurator with instant downloadable PDF quote.<br/>
                    3. <strong>Instant Digital KYC:</strong> DPDP Act consent + automated registry verification + OCR anomaly checks.<br/>
                    4. <strong>Proactive Tracker:</strong> Live 7-stage installation roadmap with technician direct contact.
                  </p>
                </div>
              )}

              {currentSlide === 5 && (
                <div className="space-y-3 p-4 bg-slate-50 rounded-2xl border border-slate-200">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Slide 5: Catalogue Grounded AI Engine</span>
                  <h3 className="text-xl font-black text-slate-900">Zero Hallucination Architecture</h3>
                  <p className="text-slate-600 text-xs leading-relaxed">
                    Unlike generic chatbots that fabricate nonexistent telecom tariffs, UdyamOne's recommendation engine is hard-grounded in the 25 official catalogue products. Every prerequisite constraint (such as <code>requires_one_of</code> for backup links or <code>requires_gstin</code>) is mathematically verified before quotation.
                  </p>
                </div>
              )}

              {currentSlide === 6 && (
                <div className="space-y-3 p-4 bg-slate-50 rounded-2xl border border-slate-200">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Slide 6: KYC & Regulatory Transformation</span>
                  <h3 className="text-xl font-black text-slate-900">Near-Instant Verification with DPDP Compliance</h3>
                  <p className="text-slate-600 text-xs leading-relaxed">
                    Replaces multi-day physical paperwork visits with sub-second API lookups against mock GSTIN and Udyam registries. Intelligent OCR catches planted discrepancies (expired address proofs, name mismatches, cancelled tax statuses) before dispatching field crews.
                  </p>
                </div>
              )}

              {currentSlide === 7 && (
                <div className="space-y-3 p-4 bg-slate-50 rounded-2xl border border-slate-200">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Slide 7: Value Proposition & Pricing</span>
                  <h3 className="text-xl font-black text-slate-900">Transparent Monthly Billing & Measurable Savings</h3>
                  <p className="text-slate-600 text-xs leading-relaxed">
                    All components are unified under a single monthly recurring invoice with 18% GST itemized. Customers save ₹300–₹1,200/month compared to unbundled ad-hoc purchases, while Accel Business secures 12–24 month contracted tenures with lower churn.
                  </p>
                </div>
              )}

              {currentSlide === 8 && (
                <div className="space-y-3 p-4 bg-slate-50 rounded-2xl border border-slate-200">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Slide 8: Partner Go-to-Market Strategy</span>
                  <h3 className="text-xl font-black text-slate-900">Empowering Local Resellers, Not Competing With Them</h3>
                  <p className="text-slate-600 text-xs leading-relaxed">
                    Channel partners receive the Partner Command Centre with Scikit-learn predictive lead scores. Instead of manually qualifying cold leads, partners receive high-risk abandoned quotes with automated recovery links and commission attribution on all digital activations.
                  </p>
                </div>
              )}

              {currentSlide === 9 && (
                <div className="space-y-3 p-4 bg-slate-50 rounded-2xl border border-slate-200">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Slide 9: Rollout Plan & Success Metrics</span>
                  <h3 className="text-xl font-black text-slate-900">3-Phased City Rollout with Hard KPI Targets</h3>
                  <p className="text-slate-600 text-xs leading-relaxed">
                    • <strong>Phase 1 (Months 1–3):</strong> 5 Tier 1 cities with 250 flagship channel partners.<br/>
                    • <strong>Phase 2 (Months 4–6):</strong> Expansion into 15 Tier 2 cities targeting micro retail and polyclinics.<br/>
                    • <strong>Phase 3 (Months 7–12):</strong> Pan-India rollout with automated WhatsApp onboarding integration.
                  </p>
                </div>
              )}

              {currentSlide === 10 && (
                <div className="space-y-3 p-4 bg-slate-50 rounded-2xl border border-slate-200">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Slide 10: Risks & Mitigations</span>
                  <h3 className="text-xl font-black text-slate-900">Proactive Risk Management</h3>
                  <ul className="space-y-1.5 text-xs text-slate-700">
                    <li>• <strong>Risk: Last-mile fiber delay:</strong> Proactive AirFiber 5G FWA dispatch in &lt;48 hours if civil cabling is stalled.</li>
                    <li>• <strong>Risk: Non-GSTIN micro merchant exclusion:</strong> Dedicated Udyam micro path unlocks 4.8× conversion lift.</li>
                    <li>• <strong>Risk: Channel partner resistance:</strong> Guaranteed partner commission protection on all portal conversions.</li>
                  </ul>
                </div>
              )}
            </div>
          )}

          {type === 'privacy' && (
            <div className="space-y-4 p-6 bg-slate-50 rounded-2xl border border-slate-200 text-xs text-slate-700">
              <div className="border-b border-slate-200 pb-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                    Statutory Privacy Architecture & Design Note
                  </span>
                  <span className="text-[11px] font-mono text-slate-500">Framework: DPDP Act, 2023 · Reference: 2026-07-15</span>
                </div>
                <h3 className="text-base font-extrabold text-slate-900 mt-1">
                  Digital Personal Data Protection (DPDP) Act, 2023 — Privacy Architecture & Security Posture
                </h3>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Platform: Project UdyamOne | Enterprise Brand: Accel Business (Demonstration Prototype)
                </p>
              </div>

              {/* Statutory Timing Context Banner */}
              <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-[11px] text-amber-900 leading-relaxed">
                <strong>Statutory Context & Phased Commencement:</strong> The Digital Personal Data Protection Act, 2023 was enacted by Parliament in August 2023. As of late 2026, provisions of the Act are subject to phased notification and subordinate rule-making by the Central Government under Section 1(2). The controls described below reflect <strong>prototype design controls proactively aligned with the Act's statutory principles and anticipated requirements</strong>, rather than claiming fully operationalized or third-party certified regulatory compliance.
              </div>

              {/* Three Clean Operational Categories */}
              <div className="space-y-3.5">
                {/* 1. Implemented Prototype Controls */}
                <div className="p-3.5 rounded-xl bg-white border border-slate-200 shadow-sm space-y-2">
                  <div className="flex items-center gap-1.5 font-bold text-slate-900 text-xs">
                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                    <span>1. Implemented Prototype Controls (Active in Live Code)</span>
                  </div>
                  <ul className="space-y-1.5 text-[11px] text-slate-600 pl-3.5 list-disc">
                    <li>
                      <strong>Purpose-Specific Granular Consent (Section 6 Principles):</strong> Consent is decoupled into discrete, affirmative opt-in purposes (GSTIN validation, Udyam MSME lookup, telecom KYC compliance). Every consent event captures an explicit timestamp under consent template <code className="bg-slate-100 px-1 py-0.2 rounded font-mono text-slate-800">DPDP-2026-V1.0</code>.
                    </li>
                    <li>
                      <strong>Anticipated Right to Withdraw Consent (Section 6(4) Alignment):</strong> Modeled after Section 6(4) principles (where withdrawal should be as simple as granting consent), the backend provides programmatic consent revocation endpoints (<code className="bg-slate-100 px-1 py-0.2 rounded font-mono text-slate-800">/api/v1/kyc/consent/withdraw</code>) and halts further automated registry lookups upon revocation.
                    </li>
                    <li>
                      <strong>Anticipated Right to Correction & Erasure (Section 12 Alignment):</strong> Designed in accordance with Section 12 principles, allowing business applicants to review, correct inaccurate business profile data, and request erasure of temporary pre-order document uploads.
                    </li>
                    <li>
                      <strong>Data Minimisation & Masking (Section 6(1) Alignment):</strong> Only minimal necessary fields for B2B connectivity are collected. Personal identifiers (e.g. PAN, mobile, signatory IDs) are masked (<code className="bg-slate-100 px-1 py-0.2 rounded font-mono text-slate-800">••••1234</code>) in API responses and frontend displays. Zero biometric data is ingested or stored.
                    </li>
                    <li>
                      <strong>Relational Application Audit Logging:</strong> Every lookup, document extraction, and verification decision produces a structured relational application audit trail recording event timestamp and agent identifier. <em>(Note: Current prototype utilizes application-level relational database logs with SHA-256 digests; production specification mandates hardware-enforced tamper-evident storage described below)</em>.
                    </li>
                  </ul>
                </div>

                {/* 2. Simulated Registry Verification */}
                <div className="p-3.5 rounded-xl bg-white border border-slate-200 shadow-sm space-y-2">
                  <div className="flex items-center gap-1.5 font-bold text-slate-900 text-xs">
                    <span className="w-2 h-2 rounded-full bg-sky-500"></span>
                    <span>2. Simulated Registry Verification & Synthetic Benchmark Data</span>
                  </div>
                  <ul className="space-y-1.5 text-[11px] text-slate-600 pl-3.5 list-disc">
                    <li>
                      <strong>100% Synthetic Ground Truth:</strong> All 3,534 GSTIN records, 2,723 Udyam certificates, and 12 document specimen packs (K01–K12) are synthetic test figures created specifically for the Airtel SYNC hackathon. No real citizen PII is accessed.
                    </li>
                    <li>
                      <strong>Mock Government Gateways:</strong> Lookups query local in-memory/CSV registries. Live government sandbox endpoints (GSTN GSP, Udyam Ministry portal) are not connected in this demonstration prototype.
                    </li>
                  </ul>
                </div>

                {/* 3. Proposed Production Security Controls & Retention Architecture */}
                <div className="p-3.5 rounded-xl bg-white border border-slate-200 shadow-sm space-y-2">
                  <div className="flex items-center gap-1.5 font-bold text-slate-900 text-xs">
                    <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                    <span>3. Proposed Production Controls & Regulatory Retention Limits</span>
                  </div>
                  <ul className="space-y-1.5 text-[11px] text-slate-600 pl-3.5 list-disc">
                    <li>
                      <strong>Proposed Product Policy (Transient / Abandoned Uploads):</strong> A 30-day purge cycle is proposed as an internal product design policy strictly for transient OCR scratch buffers and uncompleted/abandoned onboarding sessions before permanent automated purge.
                    </li>
                    <li>
                      <strong>Telecom Licensing & CAF Retention (Completed Activations):</strong> For activated enterprise connections, Customer Acquisition Forms (CAF), subscriber identity dossiers, and associated verification records are <strong>strictly governed by Department of Telecommunications (DoT) licensing directives and subscriber verification instructions</strong>. Under DoT guidelines, digitized CAF records and subscriber documents must be maintained throughout the active subscription lifecycle and retained following disconnection or migration in accordance with applicable DoT audit rules and legal preservation orders, which supersede internal transient data deletion policies.
                    </li>
                    <li>
                      <strong>Distinction from Network Traffic Metadata:</strong> Distinct from subscriber registration dossiers (CAFs), telecom network traffic metadata—including Call Detail Records (CDR), IP Detail Records (IPDR), and Exchange Detail Records (EDR)—is subject to separate statutory mandates under Unified License amendments (requiring minimum 2-year retention). These communications traffic logs are not collected or managed by the UdyamOne onboarding portal.
                    </li>
                    <li>
                      <strong>Tamper-Evident Immutable WORM Storage:</strong> The production target architecture specifies Hardware Security Module (HSM)-backed Write Once Read Many (WORM) audit logging with cryptographic hash-chaining to ensure tamper evidence.
                    </li>
                    <li>
                      <strong>Zero-Trust IAM & Encryption:</strong> Production roadmap requires OAuth 2.0 / OpenID Connect integrated with enterprise IAM, TLS 1.3 mTLS inter-service encryption, and KMS envelope encryption (AES-256-GCM) for data at rest.
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {type === 'script' && (
            <div className="space-y-5 p-6 bg-slate-50 rounded-2xl border border-slate-200">
              <div className="border-b border-slate-200 pb-3">
                <span className="text-[10px] font-bold uppercase tracking-wider text-sky-700">
                  Pitch & Demonstration Delivery
                </span>
                <h3 className="text-lg font-bold text-slate-900">
                  Three-Minute Live Judging Demonstration Script
                </h3>
              </div>

              <div className="space-y-3 text-xs text-slate-700 font-mono">
                <p>
                  <strong className="text-red-600">[0:00–0:20] The Problem:</strong><br/>
                  "Judges, today 5,000 SMBs show interest in Accel Business, but only 368 get activated. That is a 7.3% conversion rate costing ₹15,000 per customer. The biggest leak is right after needs assessment: quotes take 3–5 days, arrive with confusing product codes, and owners walk away. Meet UdyamOne."
                </p>
                <p>
                  <strong className="text-red-600">[0:20–0:55] AI Advisor (Module 1):</strong><br/>
                  "Watch how a clinic owner in Jaipur discovers connectivity in 30 seconds. In Hindi, English, or Tamil, our AI advisor asks about their site, budget, and patient needs. Grounded strictly in Accel's 25-SKU catalogue, it outputs Essential, Growth, and Advanced bundles with crystal-clear explanations and zero hallucinations."
                </p>
                <p>
                  <strong className="text-red-600">[0:55–1:20] Smart Quote & Configurator (Module 2):</strong><br/>
                  "The owner customizes add-ons like cloud backup and 4G failover. The system automatically enforces technical dependencies and computes the monthly recurring fee, setup charge, and 18% GST with an instant downloadable quotation."
                </p>
                <p>
                  <strong className="text-red-600">[1:20–2:00] Smart Digital KYC (Module 3):</strong><br/>
                  "Under the DPDP Act 2023, the user grants granular consent. Our engine queries 3,500+ mock GSTIN and 2,700+ Udyam records. It executes native OCR on uploaded specimens, instantly flagging expired utility bills and name mismatches with clear corrective guidance."
                </p>
                <p>
                  <strong className="text-red-600">[2:00–2:25] Proactive Order Tracker (Module 4):</strong><br/>
                  "Once booked, the customer follows a 7-stage visual installation timeline, with assigned technician direct contact and proactive alerts—slashing status chasing calls from 3 down to zero."
                </p>
                <p>
                  <strong className="text-red-600">[2:25–3:00] Partner Intelligence & Closing (Modules 5–7):</strong><br/>
                  "Finally, channel partners see abandoned quotes scored by our Scikit-learn predictive model. High-propensity leads get automated recovery links. UdyamOne is engineered to compress onboarding from 17.6 days baseline down to 4.5 days target, reduce CAC by 68% to ₹4,800, and unlock India's 6 crore MSMEs."
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-slate-900 text-white font-semibold text-xs hover:bg-slate-800 transition-colors cursor-pointer"
          >
            Close Window
          </button>
        </div>
      </div>
    </div>
  );
};

