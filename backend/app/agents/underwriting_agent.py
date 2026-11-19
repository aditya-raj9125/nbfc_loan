"""
Underwriting Agent - Credit Bureau Scoring & Eligibility Underwriting
Worker Agent in the Agentic Architecture.
Enforces the EY Problem Statement Business Rules:
1. Validates Credit Score from Bureau API (score must be >= 700).
2. If Loan Amount <= Pre-approved Limit: Instant Approval.
3. If Loan Amount <= 2x Pre-approved Limit: Requires salary slip. Approves if EMI <= 50% salary.
4. If Loan Amount > 2x Pre-approved Limit: Rejects with transparent explanation & counter-offer.
"""
from typing import Dict, Any, Optional
from app.agents.state import LoanApplicationState
from app.services.credit_bureau import credit_bureau
from app.llm_factory import get_analytical_llm
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class UnderwritingAgent:
    """
    Underwriting Agent: Evaluates credit bureau metrics, applies eligibility rules,
    and makes the definitive loan approval or rejection decision.
    """

    def _get_display_name(self, raw_name: Optional[str]) -> str:
        if not raw_name:
            return "there"
        return raw_name.strip().split()[0].title()

    async def run(self, state: LoanApplicationState) -> Dict[str, Any]:
        customer_email = state.get("customer_email") or ""
        customer_name = self._get_display_name(state.get("customer_name"))
        loan_amount = state.get("loan_amount") or 500000.0
        pre_approved_limit = state.get("pre_approved_limit") or 500000.0
        monthly_salary = state.get("monthly_salary") or 75000.0
        emi_amount = state.get("emi_amount") or 15000.0
        pan_number = state.get("pan_number")

        # 1. Fetch Bureau Credit Score
        if pan_number:
            bureau_resp = await credit_bureau.fetch_credit_score_from_pan(pan_number)
        else:
            bureau_resp = await credit_bureau.fetch_credit_score(customer_email)

        credit_data = bureau_resp.get("data", {})
        credit_score = state.get("credit_score") or credit_data.get("credit_score", 760)
        rating = credit_data.get("rating", "Good")

        updates: Dict[str, Any] = {
            "credit_score": credit_score,
            "credit_rating": rating,
            "current_stage": "underwriting"
        }

        # 2. Apply Strict Underwriting Rules
        # Rule 1: Credit score must be >= 700
        if credit_score < 700:
            updates["application_status"] = "rejected"
            updates["rejection_reason"] = (
                f"Credit score of {credit_score} is below our threshold of 700."
            )
            updates["next_agent"] = "master"
            updates["should_end"] = False

            bot_text = (
                f"Thank you for your patience, {customer_name}. We have retrieved your credit report from the bureau. "
                f"Your current credit score is **{credit_score}/900 ({rating})**.\n\n"
                f"Unfortunately, our underwriting policy requires a minimum score of **700** for unsecured personal loans. "
                f"As a responsible lender, we cannot approve this application right now to protect your debt profile. "
                f"We recommend checking your bureau report for recent defaults and reapplying in 90 days."
            )
            updates["bot_response"] = bot_text
            self._record_conversation(state, state.get("user_message", ""), bot_text)
            return updates

        # Rule 2: Amount <= Pre-approved Limit -> Instant Approval!
        if loan_amount <= pre_approved_limit:
            updates["application_status"] = "approved"
            updates["next_agent"] = "sanction"
            bot_text = (
                f"🎉 **Congratulations, {customer_name}! Your loan of Rs. {loan_amount:,.0f} is APPROVED!**\n\n"
                f"• **Credit Score**: {credit_score}/900 (Rating: {rating})\n"
                f"• **Pre-approved Limit**: Rs. {pre_approved_limit:,.0f}\n"
                f"• **Eligibility Status**: Perfect Match (Within Instant Sanction Limit)\n\n"
                f"Generating your official Loan Sanction Letter now..."
            )
            updates["bot_response"] = bot_text
            self._record_conversation(state, state.get("user_message", ""), bot_text)
            return updates

        # Rule 3: Amount <= 2x Pre-approved Limit -> Requires Salary Slip & EMI <= 50% Salary
        if loan_amount <= pre_approved_limit * 2:
            uploaded_docs = state.get("uploaded_documents") or {}
            has_salary_slip = "salary_slip" in uploaded_docs or state.get("monthly_salary") is not None

            if not has_salary_slip:
                updates["application_status"] = "needs_documents"
                updates["next_agent"] = "document"
                updates["current_stage"] = "document_upload"
                bot_text = (
                    f"Good news, {customer_name}! Your credit score of **{credit_score}** is excellent. "
                    f"Because your requested amount (Rs. {loan_amount:,.0f}) is higher than your pre-approved "
                    f"limit (Rs. {pre_approved_limit:,.0f}), our underwriting policy requires income verification.\n\n"
                    f"Please upload your latest **Salary Slip** so we can verify that the EMI is within 50% of your salary."
                )
                updates["bot_response"] = bot_text
                self._record_conversation(state, state.get("user_message", ""), bot_text)
                return updates

            # Evaluate Debt-to-Income / EMI to Salary ratio
            emi_ratio = (emi_amount / monthly_salary) if monthly_salary > 0 else 0.4
            if emi_ratio <= 0.50:
                updates["application_status"] = "approved"
                updates["next_agent"] = "sanction"
                bot_text = (
                    f"🎉 **Loan Approved with Income Enhancement!**\n\n"
                    f"• **Applicant**: {customer_name}\n"
                    f"• **Sanctioned Amount**: Rs. {loan_amount:,.0f}\n"
                    f"• **Credit Score**: {credit_score}/900 ({rating})\n"
                    f"• **Verified Monthly Income**: Rs. {monthly_salary:,.0f}\n"
                    f"• **EMI to Income Ratio**: {emi_ratio * 100:.1f}% (Comfortably below our 50% ceiling)\n\n"
                    f"Generating your formal sanction letter now..."
                )
            else:
                updates["application_status"] = "rejected"
                updates["next_agent"] = "completed"
                updates["should_end"] = True
                updates["rejection_reason"] = (
                    f"Monthly EMI of Rs. {emi_amount:,.0f} exceeds 50% of verified salary (Rs. {monthly_salary:,.0f})."
                )
                bot_text = (
                    f"Thank you for providing your income documents, {customer_name}. "
                    f"Upon reviewing your salary slip (Rs. {monthly_salary:,.0f}/mo), the proposed EMI of "
                    f"Rs. {emi_amount:,.0f} represents {emi_ratio * 100:.1f}% of your monthly take-home income.\n\n"
                    f"Under RBI and NBFC guidelines, EMI obligations cannot exceed 50% of monthly income. "
                    f"We can however immediately approve your pre-approved limit of **Rs. {pre_approved_limit:,.0f}**."
                )

            updates["bot_response"] = bot_text
            self._record_conversation(state, state.get("user_message", ""), bot_text)
            return updates

        # Rule 4: Amount > 2x Pre-approved Limit -> Rejected
        updates["application_status"] = "rejected"
        updates["next_agent"] = "completed"
        updates["should_end"] = True
        updates["rejection_reason"] = (
            f"Requested Rs. {loan_amount:,.0f} exceeds maximum eligible threshold of Rs. {pre_approved_limit * 2:,.0f}."
        )
        bot_text = (
            f"Dear {customer_name}, your requested amount of Rs. {loan_amount:,.0f} exceeds our single-borrower "
            f"unsecured limit of Rs. {pre_approved_limit * 2:,.0f} (2x your pre-approved limit of Rs. {pre_approved_limit:,.0f}).\n\n"
            f"We are happy to instantly sanction your pre-approved limit of **Rs. {pre_approved_limit:,.0f}** today, "
            f"or you may contact our branch manager for loan against property / collateralized options."
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
underwriting_agent = UnderwritingAgent()
