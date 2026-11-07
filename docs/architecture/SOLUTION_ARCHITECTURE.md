# Project UdyamOne — Solution Architecture Blueprint
## Airtel SYNC | YTL Hackathon 2026 | Enterprise Track A

```
======================================================================================================
UDYAMONE ENTERPRISE ARCHITECTURE · ACCEL BUSINESS MSME DIGITAL ONBOARDING PLATFORM
======================================================================================================

                       ┌─────────────────────────────────────────────────────────────┐
                       │                     CLIENT INTERFACES                       │
                       │           (React 18 + Vite + TypeScript + Tailwind)         │
                       └──────────────────────────────┬──────────────────────────────┘
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       │                                                             │
            ┌──────────▼──────────┐                                       ┌──────────▼──────────┐
            │   MSME CUSTOMER     │                                       │   PARTNER COMMAND   │
            │   PORTAL (MOBILE)   │                                       │   PORTAL (DESKTOP)  │
            ├─────────────────────┤                                       ├─────────────────────┤
            │ • AI Advisor (EN/HI/│                                       │ • Lead Management   │
            │   TA) with Audio TTS│                                       │ • ML Propensity Rank│
            │ • Bundle Config     │                                       │ • Abandonment Link  │
            │ • Smart Digital KYC │                                       │ • Field Assignment  │
            │ • Order Tracker     │                                       │ • Executive BI KPIs │
            └──────────┬──────────┘                                       └──────────┬──────────┘
                       │                                                             │
                       └──────────────────────────────┬──────────────────────────────┘
                                                      │  HTTPS / OpenAPI v3 REST API
                                                      │  JSON Payloads / JWT Auth
                       ┌──────────────────────────────▼──────────────────────────────┐
                       │              FASTAPI CORE APPLICATION GATEWAY               │
                       │                  (Python 3.14 + Pydantic v2)                │
                       └──────────────────────────────┬──────────────────────────────┘
                                                      │
         ┌──────────────────┬─────────────────────────┼─────────────────────────┬──────────────────┐
         │                  │                         │                         │                  │
┌────────▼────────┐┌────────▼────────┐       ┌────────▼────────┐       ┌────────▼────────┐┌────────▼────────┐
│ CATALOGUE &     ││ RECOMMENDATION  │       │ SMART DIGITAL   │       │ PROACTIVE ORDER ││ PREDICTIVE LEAD │
│ PRICING ENGINE  ││ ENGINE (HYBRID) │       │ KYC ENGINE      │       │ TRACKER ENGINE  ││ SCORING ENGINE  │
├─────────────────┤├─────────────────┤       ├─────────────────┤       ├─────────────────┤├─────────────────┤
│• 25 Accel SKUs  ││• Progressive Q&A│       │• DPDP Consent   │       │• 7-Stage Live   ││• Scikit-learn   │
│• Dependency     ││• Constraint     │       │  Audit Trail    │       │  Timeline       ││  Random Forest  │
│  Validator      ││  Satisfaction   │       │• Windows OCR    │       │• Feasibility    ││• Zero Data Leak │
│• Rule Enforcement││• 3 Tiers:      │       │  Engine         │       │  Port Check     ││  Guarantee      │
│  (requires_one) ││  Essential,     │       │• Multi-Rule     │       │• Tech Dispatch  ││• Propensity &   │
│• 18% GST Recalc ││  Growth, Adv.   │       │  Anomaly Check  │       │  Coordination   ││  Risk Drivers   │
└────────┬────────┘└────────┬────────┘       └────────┬────────┘       └────────┬────────┘└────────┬────────┘
         │                  │                         │                         │                  │
         └──────────────────┴─────────────────────────┼─────────────────────────┴──────────────────┘
                                                      │
                       ┌──────────────────────────────▼──────────────────────────────┐
                       │                     DATA & REGISTRY LAYER                   │
                       └──────────────────────────────┬──────────────────────────────┘
                                                      │
         ┌──────────────────┬─────────────────────────┼─────────────────────────┬──────────────────┐
         │                  │                         │                         │                  │
┌────────▼────────┐┌────────▼────────┐       ┌────────▼────────┐       ┌────────▼────────┐┌────────▼────────┐
│ PRODUCT         ││ MOCK GSTIN      │       │ MOCK UDYAM      │       │ SMB LEADS DATA  ││ SPECIMEN KYC    │
│ CATALOGUE CSV   ││ REGISTRY CSV    │       │ REGISTRY CSV    │       │ & BI REPOSITORY ││ DOCUMENTS (47)  │
├─────────────────┤├─────────────────┤       ├─────────────────┤       ├─────────────────┤├─────────────────┤
│• 25 SKUs        ││• 3,534 Records  │       │• 2,723 Records  │       │• 5,000 SMB Leads││• K01-K12 Planted│
│• SLA & Pricing  ││• Active/Susp./  │       │• Micro/Small/   │       │• Funnel Benchmrk││  Edge Scenarios │
│• City Tiers     ││  Cancelled      │       │  Medium Class   │       │• 7.36% Baseline ││• Corrupted, Exp.│
└─────────────────┘└─────────────────┘       └─────────────────┘       └─────────────────┘└─────────────────┘
```

---

## 1. COMPONENT SPECIFICATIONS

### A. Customer Frontend Portal
- **Framework:** React 18+, Vite, TypeScript, Tailwind CSS, Lucide React, Recharts.
- **Multilingual Support:** English, Hindi, and Tamil with Web Speech API audio narration.
- **State Management:** Reactive component hooks with auto-recalculation upon parameter alterations.

### B. Core Backend Gateway
- **Framework:** Python FastAPI with Pydantic v2 schemas and SQLAlchemy ORM.
- **Data Integrity:** Strict input validation, zero-leakage ML pipeline, and authoritative deterministic catalogue grounding.
- **Auditability:** Timestamped, versioned DPDP consent logging (`DPDP-2026-V1.0`).

### C. Smart Digital KYC & OCR Engine
- **Mock GSTIN Registry:** 3,534 records covering Active, Suspended, and Cancelled statuses.
- **Mock Udyam Registry:** 2,723 records for instant MSME classification.
- **OCR Engine:** Native Windows Media OCR with fallback parser and specimen extraction caching.
- **Cross-Validation Checks:** Address proof age (<=90 days from `2026-07-15`), business legal name consistency, registration integrity, and document completeness.

### D. Predictive Lead Scoring Engine
- **Algorithm:** Scikit-learn `RandomForestClassifier` with balanced class weighting.
- **Feature Set:** Strict pre-conversion attributes (City Tier, Employees, Sites, Has GSTIN, Has Udyam, Prior Telecom Spend, Channel, Segment).
- **Validation:** 5-fold cross-validation with ROC-AUC = 0.671 and zero data leakage.

