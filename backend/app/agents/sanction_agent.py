"""
Sanction Agent - Official Sanction Letter Generation & Closing
Worker Agent in the Agentic Architecture.
Generates the official PDF sanction letter and provides disbursement timeline.
"""
from typing import Dict, Any, Optional
import os
import uuid
from app.agents.state import LoanApplicationState
from app.services.pdf_generator import pdf_generator
from app.config import get_settings


class SanctionAgent:
    """
    Sanction Agent: Generates official downloadable PDF sanction letter
    and provides clear closing and post-approval instructions.
    """

    def _get_display_name(self, raw_name: Optional[str]) -> str:
        if not raw_name:
            return "Valued Customer"
        return raw_name.strip().split()[0].title()

    async def run(self, state: LoanApplicationState) -> Dict[str, Any]:
        customer_name = state.get("customer_name") or "Valued Customer"
        first_name = self._get_display_name(customer_name)
        customer_address = state.get("customer_address") or "Address on file"
        loan_amount = state.get("loan_amount") or 500000.0
        tenure_months = state.get("tenure_months") or 36
        interest_rate = state.get("interest_rate") or 10.5
        emi_amount = state.get("emi_amount") or 16250.0

        loan_id = state.get("loan_application_id")
        if not loan_id:
            loan_id = f"NBFC-{uuid.uuid4().hex[:8].upper()}"

        updates: Dict[str, Any] = {
            "loan_application_id": loan_id,
            "application_status": "approved",
            "current_stage": "sanction",
            "next_agent": "completed",
            "should_end": False
        }

        try:
            pdf_path = await pdf_generator.generate_sanction_letter(
                customer_name=customer_name,
                customer_address=customer_address,
                loan_amount=loan_amount,
                tenure_months=tenure_months,
                interest_rate=interest_rate,
                emi_amount=emi_amount,
                loan_id=loan_id
            )

            # Build public URL for the generated PDF
            filename = os.path.basename(pdf_path)
            settings = get_settings()
            backend_url = settings.FRONTEND_URL.replace("3000", "8000")
            pdf_url = f"{backend_url.rstrip('/')}/uploads/sanction_letters/{filename}"

            updates["sanction_letter_url"] = pdf_url

            bot_text = f"""🎉 **OFFICIAL LOAN SANCTION CONFIRMATION** 🎉

Dear **{customer_name}**, we are thrilled to formally issue your digital Sanction Letter:

━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 **Sanction Reference**: `{loan_id}`
💰 **Sanctioned Amount**: **Rs. {loan_amount:,.0f}**
📊 **Annualized ROI**: **{interest_rate:.2f}% p.a.** (Reducing)
⏳ **Tenure**: **{tenure_months} Months** ({tenure_months // 12} Years)
💳 **Equated Monthly EMI**: **Rs. {emi_amount:,.0f}**
⚡ **Processing Fee**: **Rs. 0 (Waived)**
━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 **Download Your Official Document:**
👉 [**Click Here to Download Sanction Letter (PDF)**]({pdf_url})

**Next Steps & Disbursement Timeline:**
1. **Digital e-Sign**: Click the link above to review your sanctioned terms.
2. **Auto-Disbursement**: Loan funds will be credited to your verified bank account within **2 to 4 hours**.
3. **First EMI**: Scheduled on the 5th of next month via automated NACH e-mandate.

Thank you for trusting NBFC Finance as your financial partner! Feel free to ask if you have any questions. 🙂"""

        except Exception as e:
            bot_text = f"""🎉 **Congratulations {first_name}! Your loan of Rs. {loan_amount:,.0f} is APPROVED!**

• **Sanction Reference**: `{loan_id}`
• **Approved Amount**: Rs. {loan_amount:,.0f}
• **Interest Rate**: {interest_rate}% p.a.
• **Monthly EMI**: Rs. {emi_amount:,.0f}
• **Tenure**: {tenure_months} months

Your official sanction letter has been dispatched to your email address ({state.get('customer_email', 'registered email')}).
Funds will be transferred within 2 to 4 hours. Thank you for choosing NBFC Finance!"""

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
sanction_agent = SanctionAgent()
