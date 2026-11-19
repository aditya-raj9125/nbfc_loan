# System Architecture — NBFC Agentic Loan Platform

## 1. System Overview

The **NBFC Agentic Loan Platform** is designed for high-conversion conversational lending. It pairs an asynchronous web frontend with a reactive Python backend powered by a **Master-Worker Agentic AI Graph**, real-time WebSockets, Groq Llama 3.3 70B Language Models, Groq Llama 3.2 Vision LLMs, and a local embedded SQLite database.

```mermaid
flowchart TD
    subgraph Client["Client Tier (Next.js 14)"]
        UI["Web Portal / Chat Widget\n(Tailwind CSS + Lucide Icons)"]
        Auth["NextAuth.js\n(Persona Credentials & Guest Mode)"]
        WSClient["WebSocket Client\n(Real-Time Bidirectional Sync)"]
        UploadClient["Document Uploader\n(REST Multipart / PDF & Images)"]
    end

    subgraph Gateway["API Gateway Tier (FastAPI)"]
        Router["FastAPI Application Server"]
        WSEndpoint["WebSocket Router\n/ws/chat/{customer_id}"]
        RestDoc["Document Ingestion\n/api/documents/upload"]
        StaticServe["Sanction Letter Server\n/uploads/sanction_letters/"]
    end

    subgraph AgenticCore["Agentic Core (Master-Worker Graph)"]
        State["LoanApplicationState\n(Thread-Safe Conversation Memory)"]
        Master["Master Agent (Shruti)\nContext Manager & Coordinator"]
        
        subgraph Workers["Specialized Worker Agents"]
            Sales["Sales Agent\n(Terms, EMI & Pricing)"]
            Verif["Verification Agent\n(CRM KYC Lookup)"]
            DocAgent["Document Agent\n(Multimodal Vision Ingestion)"]
            UW["Underwriting Agent\n(Credit Bureau & Risk Rules)"]
            Sanction["Sanction Agent\n(ReportLab PDF Generator)"]
        end
    end

    subgraph Services["External & Mock Service Integrations"]
        CRM["Mock CRM Service\n(Customer KYC & Profiles)"]
        Bureau["Mock Credit Bureau\n(CIBIL / Experian Scoring)"]
        GroqLLM["Groq Llama 3.3 70B Versatile\n(Conversational NLP)"]
        GroqVision["Groq Llama 3.2 11B Vision\n(Multimodal OCR Extraction)"]
        DB[(Local SQLite DB\nsqlite:///./nbfc_loan.db)]
    end

    UI --> WSClient
    UI --> UploadClient
    WSClient <-->|ws://localhost:8000/ws/chat/| WSEndpoint
    UploadClient -->|POST /api/documents/upload| RestDoc
    
    WSEndpoint <--> Master
    RestDoc --> Master
    
    Master <--> State
    Master --> Sales
    Master --> Verif
    Master --> DocAgent
    Master --> UW
    Master --> Sanction

    Verif <--> CRM
    UW <--> Bureau
    DocAgent <--> GroqVision
    Master <--> GroqLLM
    Sanction --> StaticServe
    Master --> DB
```

---

## 2. Master-Worker Agent Topology

The conversational architecture avoids static script branching by using a **hierarchical coordinator pattern**. The Master Agent acts as the single point of contact for the borrower, maintaining personality, conversational empathy, and memory while dynamically routing domain-specific subtasks to specialized Worker Agents.

| Agent | Role | Capabilities | Trigger Criteria |
| :--- | :--- | :--- | :--- |
| **Master Agent** *(Shruti)* | Orchestrator & Persona | Empathetic dialogue, intent classification, memory management, worker hand-offs | Active on every turn |
| **Sales Agent** | Loan Advisor | Tenures (12-60m), rates (10.5%-18%), reducing-balance EMI calculations | When user discusses amount, tenure, or repayment |
| **Verification Agent** | Identity & KYC | Real-time CRM record verification (phone, address, pre-approved offers) | When borrower confirms identity or selects loan offer |
| **Document Agent** | Multimodal Auditor | Extracts PAN, Aadhaar, and monthly income from uploaded PDFs/images via Groq Vision | Triggered on document upload (`__doc_uploaded__`) |
| **Underwriting Agent** | Risk Assessor | CIBIL credit check, DTI (Debt-To-Income) evaluation, multi-tier risk policy enforcement | When user requests final sanction or accepts offer |
| **Sanction Agent** | Document Issuer | ReportLab PDF compilation, digital stamping, official download link generation | Upon Underwriting approval |

---

## 3. End-to-End Orchestration Sequence

The following sequence diagram outlines the complete multi-turn lifecycle of a loan application, from initial persona greeting to PDF sanction issuance.

```mermaid
sequenceDiagram
    autonumber
    actor User as Borrower (User)
    participant Front as Frontend (ChatWidget)
    participant WS as FastAPI WebSocket
    participant Master as Master Agent (Shruti)
    participant State as Application State
    participant Worker as Worker Agent Pool
    participant Vision as Groq Vision LLM
    participant DB as SQLite Database

    User->>Front: Selects Demo Persona / Enters Chat
    Front->>WS: Connects WebSocket (/ws/chat/{customer_id})
    WS->>Master: Initialize Conversation
    Master->>Front: Personalized Greeting & Pre-Approved Offer
    
    User->>Front: "I need Rs. 3,50,000 for home renovation"
    Front->>WS: Message payload
    WS->>Master: Process message
    Master->>Worker: Delegate to Sales Agent
    Worker-->>Master: EMI Options (24m: Rs. 16,248 | 36m: Rs. 11,380)
    Master->>Front: Empathic pitch with calculated EMI breakdown

    User->>Front: "36 months looks good, let's proceed"
    Front->>WS: User confirmation
    WS->>Master: Hand-off to Underwriting Agent
    Master->>Worker: Check Pre-Approved Limit & Credit Score
    Worker-->>Master: Amount exceeds pre-approved limit (Rs. 2L). Requires Salary Slip.
    Master->>Front: "Your pre-approved limit is Rs. 2,00,000. Please upload your latest salary slip for Rs. 3.5 Lakhs."

    User->>Front: Uploads salary_slip.pdf
    Front->>WS: REST Upload / Notify ws ("__doc_uploaded__")
    WS->>Worker: Document Agent analyzes via Groq Vision
    Worker->>Vision: Multimodal OCR extraction
    Vision-->>Worker: Net Salary: Rs. 85,000 | Employer: TechCorp
    Worker-->>Master: Salary validated (EMI Rs. 11,380 <= 50% income)
    
    Master->>Worker: Underwriting Agent executes final assessment
    Worker-->>Master: Credit Score 760 >= 700. STATUS: APPROVED.
    Master->>Worker: Sanction Agent compiles PDF
    Worker-->>Master: Sanction Letter Generated (sanction_CUST001_...pdf)
    Master->>DB: Persist Approved Loan Application
    Master->>Front: Official Approval + Clickable PDF Download Link
```

---

## 4. Loan Application State Machine

The state transition flow is strictly enforced by the Master-Worker graph to prevent out-of-order execution (e.g. issuing a sanction before KYC or credit approval).

```mermaid
stateDiagram-v2
    [*] --> GREETING: Session Start
    
    GREETING --> DISCOVERY: User Expresses Intent
    DISCOVERY --> NEGOTIATION: Amount & Purpose Stated
    
    NEGOTIATION --> KYC_VERIFICATION: Terms Accepted
    
    state Underwriting_Flow {
        KYC_VERIFICATION --> CREDIT_EVALUATION: Identity Confirmed
        CREDIT_EVALUATION --> INSTANT_APPROVAL: Loan <= Pre-Approved & Score >= 700
        CREDIT_EVALUATION --> DOC_COLLECTION: Loan > Pre-Approved & Score >= 700
        CREDIT_EVALUATION --> REJECTED: Score < 700
        
        DOC_COLLECTION --> DOC_PROCESSING: Document Uploaded
        DOC_PROCESSING --> SALARY_APPROVED: Validated & EMI <= 50% Income
        DOC_PROCESSING --> SALARY_INSUFFICIENT: EMI > 50% Income
        SALARY_INSUFFICIENT --> NEGOTIATION: Reduce Amount / Extend Tenure
    }
    
    INSTANT_APPROVAL --> SANCTION_GENERATION: Trigger PDF Agent
    SALARY_APPROVED --> SANCTION_GENERATION: Trigger PDF Agent
    
    SANCTION_GENERATION --> COMPLETED: PDF Issued to User
    REJECTED --> COMPLETED: Adverse Action Letter Issued
    
    COMPLETED --> [*]
```

---

## 5. Multimodal Document Extraction Pipeline

The platform leverages Groq's `llama-3.2-11b-vision-preview` model for automated document ingestion without traditional OCR pipeline dependencies (Tesseract or Poppler).

```mermaid
flowchart LR
    Upload["Borrower Upload\n(PDF / PNG / JPEG)"] --> Ingest["Document Router\n(backend/app/api/documents.py)"]
    
    Ingest --> TypeCheck{"File Format?"}
    
    TypeCheck -->|PDF| PyMuPDF["PyMuPDF (fitz)\nRender Page 1 to Pixmap"]
    TypeCheck -->|Image| PIL["Pillow Image Handler"]
    
    PyMuPDF --> Base64["Base64 JPEG Encoder"]
    PIL --> Base64
    
    Base64 --> VisionPrompt["Groq Multimodal Vision API\n(llama-3.2-11b-vision-preview)"]
    
    VisionPrompt --> JSONOutput["Structured JSON Extraction\n- Document Type\n- Monthly Income\n- Employer Name\n- Account / Ref Numbers"]
    
    JSONOutput --> UWState["Update LoanApplicationState\n& Notify Master Agent"]
```

---

## 6. Storage & Database Tier

All persistence operations use a zero-dependency local SQLite database (`sqlite:///./nbfc_loan.db`) managed via SQLAlchemy 2.0 ORM.

```mermaid
erDiagram
    CUSTOMERS ||--o{ LOAN_APPLICATIONS : submits
    CUSTOMERS ||--o{ DOCUMENTS : uploads
    LOAN_APPLICATIONS ||--o{ SANCTION_LETTERS : generates

    CUSTOMERS {
        string id PK "e.g. CUST001"
        string name "Customer Full Name"
        string phone "Phone Number"
        string email "Email Address"
        string city "City of Residence"
        float pre_approved_limit "Pre-approved loan limit"
        int credit_score "Bureau Credit Score"
        string kyc_status "VERIFIED | PENDING"
    }

    LOAN_APPLICATIONS {
        int id PK "Auto-incrementing ID"
        string customer_id FK "References CUSTOMERS.id"
        float loan_amount "Sanctioned / Requested Amount"
        int tenure_months "Repayment period in months"
        float interest_rate "Annual Interest Rate (%)"
        float monthly_emi "Computed Monthly EMI"
        string purpose "Loan Purpose"
        string status "APPROVED | REJECTED | IN_REVIEW"
        datetime created_at "Timestamp of Application"
    }

    DOCUMENTS {
        int id PK "Auto-incrementing ID"
        string customer_id FK "References CUSTOMERS.id"
        string document_type "SALARY_SLIP | PAN | AADHAAR"
        string file_path "Absolute path on local disk"
        string ocr_status "EXTRACTED | FAILED"
        string extracted_data "JSON text of extracted fields"
        datetime uploaded_at "Upload timestamp"
    }

    SANCTION_LETTERS {
        int id PK "Auto-incrementing ID"
        string application_id FK "References LOAN_APPLICATIONS.id"
        string file_path "Local static file path"
        string download_url "Web accessible URL"
        datetime issued_at "Generation timestamp"
    }
```

---

## 7. Security, Privacy, and Standards

1. **Local Isolation**: Customer data, document uploads, and SQLite database records reside exclusively on the host server; no external database services are required.
2. **Credential Privacy**: API keys (Groq, NextAuth secret) are isolated in `.env` and `.env.local` configurations and never exposed to the client bundle.
3. **Audit Trail**: Every worker delegation, document extraction outcome, and underwriting decision is logged in conversation transcripts and synchronized with database state.
