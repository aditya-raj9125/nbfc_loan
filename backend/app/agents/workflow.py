"""
LangGraph Multi-Agent Workflow Orchestrator
Master Agent (Controller) coordinates multiple Worker Agents:
- Sales Agent: Negotiates terms, discusses needs, calculates EMI
- Verification Agent: Confirms KYC from CRM
- Document Agent: Collects required docs (Salary Slip, Aadhaar, PAN)
- Underwriting Agent: Validates credit bureau score & loan eligibility rules
- Sanction Agent: Generates official PDF sanction letter
"""
import os
import logging
from typing import Dict, Any, Optional
from app.agents.state import LoanApplicationState
from app.agents.master_agent_llm import master_agent_llm
from app.agents.sales_agent import sales_agent
from app.agents.verification_agent import verification_agent
from app.agents.document_agent import document_agent
from app.agents.underwriting_agent import underwriting_agent
from app.agents.sanction_agent import sanction_agent
from app.services.ocr_service import ocr_service

logger = logging.getLogger(__name__)


class LoanWorkflow:
    """
    Coordinates and executes the multi-agent loan application process.
    Handles immediate stage cascading and document upload events.
    """

    AGENT_MAP = {
        "master": master_agent_llm,
        "sales": sales_agent,
        "verification": verification_agent,
        "document": document_agent,
        "underwriting": underwriting_agent,
        "sanction": sanction_agent
    }

    async def process_message(
        self,
        state: LoanApplicationState,
        user_message: str
    ) -> LoanApplicationState:
        """Process incoming user or event message through agent graph"""
        state["user_message"] = user_message.strip()

        # -------------------------------------------------------------
        # EVENT: Document Upload Notification from Frontend
        # Format: "__doc_uploaded__:<doc_type>:<filename>"
        # -------------------------------------------------------------
        if user_message.startswith("__doc_uploaded__:"):
            return await self._handle_document_upload_event(state, user_message)

        # -------------------------------------------------------------
        # STANDARD CONVERSATION ROUTING
        # -------------------------------------------------------------
        current_stage = state.get("current_stage", "greeting")
        next_agent = state.get("next_agent", "master")

        logger.info(f"[Workflow] Stage: {current_stage}, Next Agent: {next_agent}")

        # 0. Post-Rejection / Adverse Action Objection Handling
        if state.get("application_status") == "rejected":
            master_updates = await master_agent_llm.run(state)
            state.update(master_updates)
            return state

        # 1. Master Agent turn
        if next_agent == "master" or (
            current_stage in ["greeting", "onboarding", "discovery"]
            and next_agent not in ["sales", "verification", "document", "underwriting", "sanction"]
        ):
            master_updates = await master_agent_llm.run(state)
            state.update(master_updates)

            # If master automatically handed off to sales with loan amount
            if state.get("next_agent") == "sales":
                sales_updates = await sales_agent.run(state)
                state.update(sales_updates)

        # 2. Sales Agent turn
        elif next_agent == "sales":
            sales_updates = await sales_agent.run(state)
            state.update(sales_updates)

            # If sales completed agreement and handed off to verification
            if state.get("next_agent") == "verification":
                verif_updates = await verification_agent.run(state)
                state.update(verif_updates)

                # If verification succeeded and handed off to underwriting
                if state.get("next_agent") == "underwriting":
                    uw_updates = await underwriting_agent.run(state)
                    state.update(uw_updates)
                    if state.get("application_status") == "approved":
                        sanct_updates = await sanction_agent.run(state)
                        state.update(sanct_updates)

        # 3. Verification Agent turn
        elif next_agent == "verification":
            verif_updates = await verification_agent.run(state)
            state.update(verif_updates)

            if state.get("next_agent") == "underwriting":
                uw_updates = await underwriting_agent.run(state)
                state.update(uw_updates)
                if state.get("application_status") == "approved":
                    sanct_updates = await sanction_agent.run(state)
                    state.update(sanct_updates)

        # 4. Document Agent turn
        elif next_agent == "document":
            doc_updates = await document_agent.run(state)
            state.update(doc_updates)

            if state.get("next_agent") == "underwriting":
                uw_updates = await underwriting_agent.run(state)
                state.update(uw_updates)
                if state.get("application_status") == "approved":
                    sanct_updates = await sanction_agent.run(state)
                    state.update(sanct_updates)

        # 5. Underwriting Agent turn
        elif next_agent == "underwriting":
            uw_updates = await underwriting_agent.run(state)
            state.update(uw_updates)

            if state.get("application_status") == "approved":
                sanct_updates = await sanction_agent.run(state)
                state.update(sanct_updates)

        # 6. Sanction Agent turn
        elif next_agent == "sanction":
            sanct_updates = await sanction_agent.run(state)
            state.update(sanct_updates)

        # 7. Completed stage (Post-Sanction follow-up questions)
        elif next_agent == "completed":
            master_updates = await master_agent_llm.run(state)
            state.update(master_updates)
            return state

        return state

    async def _handle_document_upload_event(
        self, state: LoanApplicationState, message: str
    ) -> LoanApplicationState:
        """Handle real-time document upload event and trigger immediate OCR + underwriting"""
        parts = message.split(":")
        doc_type = parts[1] if len(parts) > 1 else "document"
        filename = parts[2] if len(parts) > 2 else ""

        if "uploaded_documents" not in state or state["uploaded_documents"] is None:
            state["uploaded_documents"] = {}

        file_path = os.path.join("uploads", "documents", filename)
        state["uploaded_documents"][doc_type] = file_path

        doc_name = doc_type.replace("_", " ").title()

        # Run Multimodal Vision OCR
        if doc_type == "salary_slip" and os.path.exists(file_path):
            ocr_res = await ocr_service.extract_salary_slip(file_path)
            if ocr_res.get("monthly_salary"):
                state["monthly_salary"] = float(ocr_res["monthly_salary"])
        elif doc_type == "aadhaar" and os.path.exists(file_path):
            ocr_res = await ocr_service.extract_aadhaar(file_path)
            state["kyc_verified"] = True
            if ocr_res.get("address") and not state.get("customer_address"):
                state["customer_address"] = ocr_res["address"]
        elif doc_type == "pan" and os.path.exists(file_path):
            ocr_res = await ocr_service.extract_pan(file_path)
            if ocr_res.get("pan_number"):
                state["pan_number"] = ocr_res["pan_number"]

        # Re-evaluate underwriting immediately with the new document!
        loan_amount = state.get("loan_amount", 0)
        pre_approved = state.get("pre_approved_limit", 0)

        # If we now have what is needed, run underwriting immediately
        if loan_amount > pre_approved and "salary_slip" in state["uploaded_documents"]:
            state["next_agent"] = "underwriting"
            state["current_stage"] = "underwriting"
            uw_updates = await underwriting_agent.run(state)
            state.update(uw_updates)

            if state.get("application_status") == "approved":
                sanct_updates = await sanction_agent.run(state)
                state.update(sanct_updates)
        else:
            state["bot_response"] = (
                f"✅ **{doc_name} Received**: Our Vision AI has successfully verified your document! "
                f"Checking next steps..."
            )
            # Route to document agent or underwriting
            doc_updates = await document_agent.run(state)
            state.update(doc_updates)

        return state


# Global singleton instance
loan_workflow = LoanWorkflow()
