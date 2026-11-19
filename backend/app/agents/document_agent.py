"""
Document Agent - Document Collection & Processing
Worker Agent in the Agentic Architecture.
Guides customers on uploading required documents (Salary Slip, Aadhaar, PAN)
and hands off to Underwriting as soon as documents are present.
"""
from typing import Dict, Any, List, Optional
import os
from app.agents.state import LoanApplicationState
from app.llm_factory import get_conversational_llm
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class DocumentAgent:
    """
    Document Agent: Detects required documents and triggers underwriting upon upload.
    """

    def _get_display_name(self, raw_name: Optional[str]) -> str:
        if not raw_name:
            return "there"
        return raw_name.strip().split()[0].title()

    async def run(self, state: LoanApplicationState) -> Dict[str, Any]:
        user_message = state.get("user_message", "").strip()
        customer_name = self._get_display_name(state.get("customer_name"))
        loan_amount = state.get("loan_amount", 0) or 500000.0
        pre_approved = state.get("pre_approved_limit", 0) or 500000.0
        uploaded = state.get("uploaded_documents") or {}

        # Determine what is required
        required: List[str] = []
        if loan_amount > pre_approved:
            required.append("salary_slip")
        if not state.get("kyc_verified"):
            required.append("aadhaar")

        pending = [doc for doc in required if doc not in uploaded]

        updates: Dict[str, Any] = {
            "required_documents": required,
            "pending_documents": pending,
            "documents_requested": True
        }

        # Check if all required documents are now received
        if not pending or (loan_amount > pre_approved and "salary_slip" in uploaded):
            updates["next_agent"] = "underwriting"
            updates["current_stage"] = "underwriting"
            bot_text = (
                f"✅ All required documents have been received and verified by our Vision AI! "
                f"Proceeding to instant credit underwriting now, {customer_name}..."
            )
        else:
            doc_labels = {
                "salary_slip": "Latest Salary Slip (PDF / Image)",
                "aadhaar": "Aadhaar Card",
                "pan": "PAN Card"
            }
            needed_str = ", ".join(doc_labels.get(d, d) for d in pending)
            updates["next_agent"] = "document"
            updates["current_stage"] = "document_upload"
            bot_text = (
                f"To finalize your loan of Rs. {loan_amount:,.0f}, please upload your **{needed_str}**.\n\n"
                f"📎 Simply tap the **+** or **attachment** icon below to select your file. "
                f"Our Vision AI will read it securely within seconds!"
            )

        updates["bot_response"] = bot_text
        self._record_conversation(state, user_message, bot_text)
        return updates

    def _record_conversation(self, state: LoanApplicationState, user_msg: str, bot_msg: str):
        if "conversation_context" not in state or state["conversation_context"] is None:
            state["conversation_context"] = []
        if user_msg:
            state["conversation_context"].append({"role": "user", "content": user_msg})
        if bot_msg:
            state["conversation_context"].append({"role": "assistant", "content": bot_msg})
        state["conversation_context"] = state["conversation_context"][-16:]


# Global singleton instance
document_agent = DocumentAgent()
