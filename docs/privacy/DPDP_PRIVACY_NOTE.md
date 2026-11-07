# One-Page Privacy, Legal & Security Design Note
## Architecture Aligned with the Digital Personal Data Protection (DPDP) Act, 2023 & DoT Licensing Framework
### Project UdyamOne · Accel Business / Airtel SYNC 2026

```
======================================================================================================
DATA GOVERNANCE, STATUTORY TIMING & PRIVACY ARCHITECTURE SPECIFICATION
======================================================================================================
```

### 1. Statutory Context & Phased Commencement
- **Enactment vs Commencement:** The Digital Personal Data Protection Act, 2023 was enacted by Parliament in August 2023. As of late 2026, provisions of the Act are subject to phased notification and subordinate rule-making by the Central Government under Section 1(2), alongside the operational establishment of the Data Protection Board of India (DPBI).
- **Prototype Status:** The privacy controls implemented in Project UdyamOne represent **prototype design controls proactively engineered to align with the Act's statutory principles and anticipated subordinate rules**, rather than claiming fully operationalized or third-party certified regulatory compliance.

### 2. Purpose-Specific Granular Consent & Withdrawal (Section 6 & Section 6(4))
- **Granular Notice & Opt-In (Section 6):** Prior to initiating business identification or registry lookups, UdyamOne presents an unbundled, affirmative consent dialogue in simple language (English, Hindi, Tamil). Consent is collected independently for three distinct activities:
  1. *GSTIN verification* with the mock GSTN portal.
  2. *Udyam enterprise validation* with the mock Ministry of MSME registry.
  3. *Telecom regulatory subscriber onboarding* under Department of Telecommunications (DoT) verification directives.
- **Timestamping & Template Versioning:** Every consent grant captures `consent_timestamp`, `applicant_name`, IP address, and template version (`DPDP-2026-V1.0`).
- **Anticipated Right to Withdraw Consent (Section 6(4) Alignment):** Modeled after Section 6(4) principles (where withdrawal must be as accessible as giving consent), the backend provides programmatic revocation endpoints (`POST /api/v1/kyc/consent/withdraw`). Once revoked, further automated registry lookups and credit checks are immediately aborted.

### 3. Data Minimisation, Masking & Individual Rights (Section 6(1) & Section 12)
- **Data Minimisation (Section 6(1)):** Only strictly necessary attributes required for enterprise B2B service qualification are gathered. No biometric data (iris scans, fingerprints) is ingested or stored.
- **Identifier Masking:** Sensitive registration IDs and contact numbers are masked in API outputs, telemetry, and partner-facing screens (e.g., `37IHK****1ZS`, `+91 98765 ***10`).
- **Anticipated Right to Correction & Erasure (Section 12 Alignment):** Applicants can review extracted OCR profile data, correct discrepancies prior to quote acceptance, and request erasure of uncompleted pre-order document uploads.

### 4. Data Retention Architecture: Product Policy vs DoT Licensing Obligations
- **Proposed Product Policy (Transient / Abandoned Uploads):** A **30-day automated purge cycle** is proposed as an internal product design policy strictly for transient OCR document scratch buffers and uncompleted/abandoned onboarding sessions.
- **Telecom Licensing & Subscriber Record Retention (Completed Activations):** For activated enterprise subscriptions, Customer Acquisition Forms (CAF), subscriber identity dossiers, and associated verification records are **strictly governed by Department of Telecommunications (DoT) licensing directives and subscriber verification instructions**. Under DoT guidelines, digitized CAF records and subscriber identity documents must be maintained throughout the active subscription lifecycle and retained following disconnection or migration in accordance with applicable DoT audit rules and legal preservation orders, which supersede internal transient data deletion policies.
- **Distinction from Network Traffic Metadata:** Distinct from subscriber registration dossiers (CAFs), telecom network traffic metadata—including Call Detail Records (CDR), IP Detail Records (IPDR), and Exchange Detail Records (EDR)—is subject to separate statutory mandates under Unified License amendments (requiring minimum 2-year retention). These communications traffic logs are not collected or managed by the UdyamOne onboarding portal.

### 5. Verification Gateways & Synthetic Hackathon Isolation
- **100% Synthetic Ground Truth:** Lookups query local mock datasets (`mock_gstin_registry.csv` with 3,534 records, `mock_udyam_registry.csv` with 2,723 records, and 12 document specimen packs K01–K12). Zero real citizen PII is accessed or transmitted.
- **Explicit Telemetry Metadata:** All mock API responses carry explicit `mock_verification: true` metadata so simulated validations are never conflated with live government portal responses.

### 6. Storage Security Posture: Prototype vs Production Roadmap
- **Prototype Implementation:** Relational SQLite/PostgreSQL audit logging with SHA-256 cryptographic digests, local file storage under isolated scratch paths, TLS 1.3 transport encryption, and role-based access control (RBAC).
- **Production Target Architecture:**
  1. *Hardware Security Module (HSM)-backed Write Once Read Many (WORM)* audit logging with cryptographic hash-chaining to ensure tamper evidence.
  2. *Zero-Trust Enterprise IAM* with OAuth 2.0 / OpenID Connect integrated into Accel Business SSO.
  3. *KMS Envelope Encryption (AES-256-GCM)* for customer data at rest with automatic key rotation.
  4. *Integration with Government Gateways:* Live DigiLocker / Aadhaar XML e-KYC integration via licensed Authentication User Agency (AUA) / KYC User Agency (KUA) rails.

### 7. Summary Statement
*Project UdyamOne demonstrates proactive architectural alignment with the principles of the DPDP Act, 2023, while strictly respecting the overarching subscriber recordkeeping obligations mandated by the Department of Telecommunications (DoT) under Indian telecom licensing rules. It utilizes synthetic test data in an isolated sandbox environment.*
