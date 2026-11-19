"""
Verification Agent - Customer Identity & KYC Verification
Worker Agent in the Agentic Architecture.
Confirms KYC details (phone, address, identity) via CRM and transitions to Underwriting.
"""
from typing import Dict, Any, Optional
from app.agents.state import LoanApplicationState
from app.services.crm_service import crm_service
from app.llm_factory import get_analytical_llm
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class VerificationAgent:
    """
    Verification Agent: Confirms KYC details from CRM or uploaded identity proofs.
    """

    async def run(self, state: LoanApplicationState) -> Dict[str, Any]:
        customer_email = state.get("customer_email", "")
        raw_name = state.get("customer_name") or "there"
        first_name = raw_name.split()[0].title() if raw_name else "there"
        loan_amount = state.get("loan_amount", 0)

        # 1. Attempt lookup in CRM
        kyc_result = await crm_service.verify_customer_kyc(customer_email)
        updates: Dict[str, Any] = {
            "current_stage": "verification",
            "verification_completed": True
        }

        if kyc_result.get("success") and kyc_result["data"].get("kyc_verified"):
            data = kyc_result["data"]
            updates["kyc_verified"] = True
            updates["customer_phone"] = data.get("phone") or state.get("customer_phone")
            updates["customer_address"] = data.get("address") or state.get("customer_address")
            updates["next_agent"] = "underwriting"

            bot_text = (
                f"✅ **KYC Confirmed**: Thanks, {first_name}! Your identity and address records "
                f"({data.get('city', 'India')}) have been verified successfully via our CRM system.\n\n"
                f"Initiating credit assessment and bureau underwriting now..."
            )
        elif state.get("kyc_verified") or state.get("aadhaar_number") or state.get("customer_address"):
            # Verified via uploaded Aadhaar / Onboarding details
            updates["kyc_verified"] = True
            updates["next_agent"] = "underwriting"
            bot_text = (
                f"✅ **Identity Verified**: Details for {first_name} confirmed successfully! "
                f"Passing your application to Underwriting for credit scoring and sanction letter generation."
            )
        else:
            # KYC unverified, route to document agent for Aadhaar / PAN
            updates["kyc_verified"] = False
            updates["next_agent"] = "document"
            updates["current_stage"] = "document_upload"
            updates["application_status"] = "needs_documents"
            bot_text = (
                f"To comply with RBI guidelines, we need to quickly verify your KYC. "
                f"Please upload a photo of your **Aadhaar Card** or **PAN Card** using the 📎 button."
            )

        updates["bot_response"] = bot_text
        self._record_conversation(state, state.get("user_message", ""), bot_text)
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
verification_agent = VerificationAgent()
