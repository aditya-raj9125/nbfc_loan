"""
Sales Agent - Loan Terms Structuring, Negotiation & Persuasion
Worker Agent in the Agentic Architecture.
Calculates EMI, presents personalized options, handles objections, and routes to Verification/Document.
"""
from typing import Dict, Any, Optional, List
import re
from app.agents.state import LoanApplicationState
from app.llm_factory import get_conversational_llm
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class SalesAgent:
    """
    Sales Agent: Negotiates loan terms, discusses customer needs, amount,
    tenure, and interest rates, and persuades customer to proceed.
    """

    def _get_display_name(self, raw_name: Optional[str]) -> str:
        if not raw_name:
            return "there"
        greetings = ["hi", "hello", "hey", "friend", "guest"]
        first_name = raw_name.strip().split()[0].title()
        if first_name.lower() in greetings:
            return "there"
        return first_name

    def _calculate_interest_rate(self, amount: float, state: LoanApplicationState) -> float:
        """Dynamic interest rate based on credit score & loan amount"""
        base_rate = 11.0
        score = state.get("credit_score") or 750
        pre_approved = state.get("pre_approved_limit") or 500000

        if score >= 800:
            base_rate -= 1.5  # 9.5%
        elif score >= 750:
            base_rate -= 0.5  # 10.5%
        elif score < 700:
            base_rate += 1.5  # 12.5%

        # Small premium if amount exceeds pre-approved limit
        if amount > pre_approved:
            base_rate += 0.5

        return round(base_rate, 2)

    def _calculate_emi(self, principal: float, annual_rate: float, tenure_months: int) -> float:
        """Standard reducing balance EMI formula"""
        if principal <= 0 or tenure_months <= 0:
            return 0.0
        monthly_r = (annual_rate / 12.0) / 100.0
        numerator = principal * monthly_r * ((1.0 + monthly_r) ** tenure_months)
        denominator = ((1.0 + monthly_r) ** tenure_months) - 1.0
        if denominator == 0:
            return round(principal / tenure_months, 2)
        return round(numerator / denominator, 2)

    def _suggest_tenure(self, amount: float, monthly_salary: float) -> int:
        """Suggest optimal tenure so EMI stays comfortable (30-35% of monthly income)"""
        salary = monthly_salary if monthly_salary and monthly_salary > 0 else 70000.0
        target_emi = salary * 0.35

        # Heuristic search through standard tenures: 12, 24, 36, 48, 60
        standard_tenures = [12, 24, 36, 48, 60]
        best_tenure = 36
        min_diff = float("inf")

        for t in standard_tenures:
            emi = self._calculate_emi(amount, 10.5, t)
            diff = abs(emi - target_emi)
            if diff < min_diff:
                min_diff = diff
                best_tenure = t

        return best_tenure

    async def run(self, state: LoanApplicationState) -> Dict[str, Any]:
        """Execute Sales negotiation turn"""
        user_message = state.get("user_message", "").strip()
        customer_name = self._get_display_name(state.get("customer_name"))
        pre_approved = state.get("pre_approved_limit") or 500000.0
        monthly_salary = state.get("monthly_salary") or 75000.0

        # Check for newly updated amount or tenure in message
        extracted_amount = self._extract_amount(user_message)
        extracted_tenure = self._extract_tenure(user_message)

        loan_amount = extracted_amount or state.get("loan_amount") or pre_approved
        tenure = extracted_tenure or state.get("tenure_months") or self._suggest_tenure(loan_amount, monthly_salary)
        interest_rate = self._calculate_interest_rate(loan_amount, state)
        emi = self._calculate_emi(loan_amount, interest_rate, tenure)

        updates: Dict[str, Any] = {
            "loan_amount": loan_amount,
            "tenure_months": tenure,
            "interest_rate": interest_rate,
            "emi_amount": emi,
            "emi_presented": True,
            "offer_presented": True
        }

        # Analyze intent for acceptance vs negotiation
        msg_lower = user_message.lower()
        is_agreement = any(
            phrase in msg_lower
            for phrase in [
                "yes", "ok", "okay", "sure", "proceed", "agree", "let's do it",
                "go ahead", "sounds good", "perfect", "deal", "accept", "apply", "continue"
            ]
        )

        emi_was_shown = state.get("emi_presented", False)

        # If user accepts terms after seeing the EMI, hand off to Verification or Document
        if is_agreement and emi_was_shown and not extracted_amount and not extracted_tenure:
            if loan_amount <= pre_approved:
                updates["next_agent"] = "verification"
                updates["current_stage"] = "verification"
                updates["application_status"] = "pending"
                bot_text = (
                    f"Excellent choice, {customer_name}! Your loan terms of Rs. {loan_amount:,.0f} "
                    f"at {interest_rate}% for {tenure} months (EMI: Rs. {emi:,.0f}/mo) are locked in. "
                    f"Let me instantly confirm your KYC status with our CRM so we can issue your sanction letter."
                )
            elif loan_amount <= pre_approved * 2:
                updates["next_agent"] = "document"
                updates["current_stage"] = "document_upload"
                updates["application_status"] = "needs_documents"
                bot_text = (
                    f"Wonderful, {customer_name}! Since Rs. {loan_amount:,.0f} exceeds your instant pre-approved "
                    f"limit of Rs. {pre_approved:,.0f}, our underwriting policy requires a quick salary slip to verify income. "
                    f"Could you please upload your latest salary slip using the 📎 button?"
                )
            else:
                updates["next_agent"] = "sales"
                updates["current_stage"] = "sales"
                updates["application_status"] = "needs_negotiation"
                bot_text = (
                    f"{customer_name}, as discussed, Rs. {loan_amount:,.0f} exceeds our single-applicant credit ceiling of Rs. {pre_approved * 2:,.0f}. "
                    f"We can immediately approve Rs. {pre_approved:,.0f} today with zero extra paperwork. Would you like to proceed with that?"
                )

            updates["bot_response"] = bot_text
            self._record_conversation(state, user_message, bot_text)
            return updates

        # Otherwise, synthesize an intelligent, persuasive sales offer via LLM
        years = tenure // 12
        tenure_desc = f"{years} year{'s' if years > 1 else ''}" if tenure % 12 == 0 else f"{tenure} months"

        scenario_category = (
            "INSTANT_PRE_APPROVED"
            if loan_amount <= pre_approved
            else ("NEEDS_SALARY_SLIP" if loan_amount <= pre_approved * 2 else "EXCEEDS_MAX_CAP")
        )

        system_prompt = f"""You are Shruti, the senior loan specialist at NBFC Finance.
You are negotiating loan terms with {customer_name}.

FINANCIAL PARAMETERS:
- Requested Loan: Rs. {loan_amount:,.0f}
- Pre-approved Benchmark: Rs. {pre_approved:,.0f}
- Proposed Tenure: {tenure_desc} ({tenure} months)
- Interest Rate: {interest_rate}% per annum
- Monthly EMI: Rs. {emi:,.0f}
- Scenario: {scenario_category}

ROLE & PERSUASION GOAL:
1. Present the loan offer with crystal clarity: Amount, Tenure, Rate, and exact Monthly EMI (in Rs.).
2. Highlight why this is an attractive deal: zero prepayment charges after 6 months, instant processing, minimal friction.
3. If {scenario_category} == 'INSTANT_PRE_APPROVED': Emphasize that approval will be instant upon brief KYC verification.
4. If {scenario_category} == 'NEEDS_SALARY_SLIP': Explain clearly that because it's up to 2x pre-approved, submitting one salary slip will enable immediate credit sanction.
5. If {scenario_category} == 'EXCEEDS_MAX_CAP': Gently suggest capping at Rs. {pre_approved:,.0f} for instant disbursement today.
6. End with a friendly, direct call to action asking if this EMI works for them. Keep length to 3-5 concise sentences."""

        messages: List[Any] = [SystemMessage(content=system_prompt)]
        context_history = state.get("conversation_context", [])
        for turn in context_history[-6:]:
            if turn.get("role") in ["user", "customer"]:
                messages.append(HumanMessage(content=turn.get("content", "")))
            else:
                messages.append(AIMessage(content=turn.get("content", "")))
        messages.append(HumanMessage(content=user_message))

        llm = get_conversational_llm()
        try:
            resp = await llm.ainvoke(messages)
            bot_text = str(resp.content).strip()
        except Exception as e:
            bot_text = (
                f"Here is your customized offer for Rs. {loan_amount:,.0f}:\n\n"
                f"• **Tenure**: {tenure_desc}\n"
                f"• **Interest Rate**: {interest_rate}% p.a.\n"
                f"• **Monthly EMI**: Rs. {emi:,.0f}\n\n"
                f"Does this monthly installment look comfortable for you?"
            )

        updates["bot_response"] = bot_text
        updates["current_stage"] = "sales"
        updates["next_agent"] = "sales"

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

    def _extract_amount(self, text: str) -> Optional[float]:
        msg = text.lower().strip()
        lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakhs?|lacs?|l\b)", msg)
        if lakh_match:
            return float(lakh_match.group(1)) * 100000
        k_match = re.search(r"(\d+(?:\.\d+)?)\s*k\b", msg)
        if k_match:
            return float(k_match.group(1)) * 1000
        rupee_match = re.search(r"(?:rs\.?|inr|₹)\s*([\d,]+(?:\.\d+)?)", msg)
        if rupee_match:
            try:
                return float(rupee_match.group(1).replace(",", ""))
            except ValueError:
                pass
        plain_match = re.search(r"\b(\d{5,7})\b", msg)
        if plain_match:
            return float(plain_match.group(1))
        return None

    def _extract_tenure(self, text: str) -> Optional[int]:
        msg = text.lower().strip()
        yr_match = re.search(r"(\d+)\s*(?:years?|yrs?)", msg)
        if yr_match:
            return int(yr_match.group(1)) * 12
        mo_match = re.search(r"(\d+)\s*(?:months?|mos?)", msg)
        if mo_match:
            return int(mo_match.group(1))
        return None


# Global singleton instance
sales_agent = SalesAgent()
