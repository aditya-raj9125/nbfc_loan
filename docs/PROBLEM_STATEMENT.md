# EY Techathon 6.0 — Problem Statement

## About the Business
A large-scale Non-Banking Financial Company (NBFC) with a presence across India offers personal loans, home loans, auto loans, and more. To increase revenue from existing customers, the NBFC aims to sell personal loans to prospects and existing customers through an intuitive, web-based conversational chatbot interface.

The chatbot serves as a **Digital Sales Assistant**, where a **Master Agent (Agentic AI Controller)** coordinates multiple **Worker AI Agents** to handle the end-to-end loan sales process — from conversation and KYC verification to credit evaluation, underwriting decisioning, and generating an official sanction letter.

---

## Core Problem Statement
The NBFC wants to improve its sales conversion rate for personal loans by adopting an AI-driven conversational approach. The solution must simulate a human-like consultative sales journey, where the Master Agent handles customer engagement, qualifies customer needs, handles objections, and collaborates with specialized Worker AI agents to execute all steps before closing the chat.

---

## Key Goal & Deliverables
Design and build an **Agentic AI Solution** where the Master Agent:
1. **Engages Customers**: Welcomes borrowers landing on the web chatbot via marketing channels (ads, email campaigns, pre-approved prompts).
2. **Consultative Discovery**: Identifies loan requirements, desired amount, tenure, and purpose while persuasive in proposing personalized loan offers.
3. **Multi-Agent Orchestration**: Coordinates specialized Worker AI agents:
   - **Sales Agent**: Negotiates loan terms, EMI structures, and interest rates.
   - **Verification Agent**: Verifies KYC details (phone, address) via the CRM server.
   - **Document Agent**: Manages document collection (Salary Slips, Aadhaar, PAN) via Multimodal Vision AI.
   - **Underwriting Agent**: Fetches credit bureau scores and enforces credit eligibility rules.
   - **Sanction Letter Agent**: Issues an official PDF Sanction Letter.

---

## Evaluation Criteria

| Evaluation Dimension | Weight | Description |
| :--- | :---: | :--- |
| **Technical Design** | **40%** | Agentic AI orchestration (LangGraph / Multi-Agent Graph), modular code, architectural integrity, and clean separation of concerns. |
| **Realism of Data & Workflow** | **25%** | Fidelity of synthetic customer datasets, mock CRM / Credit Bureau APIs, Multimodal document processing, and real-world NBFC lending policies. |
| **Conversation Flow** | **25%** | Natural, human-like sales dialogue, context retention across multi-turn exchanges, and non-linear exception handling. |
| **Demo Quality & Presentation** | **10%** | Seamless end-to-end walkthrough from first contact to sanction letter download. |
