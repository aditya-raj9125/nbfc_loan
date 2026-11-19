"""
Master Agent - LLM-Powered Conversation Orchestrator
Role: Shruti - Empathetic, smart, persuasive NBFC Loan Advisor.
Coordinates the end-to-end conversation with multi-turn memory.
"""
from typing import Dict, Any, Optional, Tuple, List
import re
from app.agents.state import LoanApplicationState
from app.llm_factory import get_conversational_llm
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class MasterAgentLLM:
    """
    Master Agent: Welcomes customers, understands needs, addresses questions,
    persuades with clear value propositions, and hands off to worker agents.
    """

    def __init__(self):
        self.name = "Shruti"

    def _get_display_name(self, raw_name: Optional[str]) -> str:
        """Get customer first name safely"""
        if not raw_name:
            return "there"
        greetings = ["hi", "hello", "hey", "hii", "hiii", "namaste", "friend", "guest"]
        first_name = raw_name.strip().split()[0].title()
        if first_name.lower() in greetings:
            return "there"
        return first_name

    def _build_messages_with_history(
        self, state: LoanApplicationState, system_prompt: str, current_user_message: str
    ) -> List[Any]:
        """Inject up to 10 previous conversational turns for contextual awareness."""
        messages: List[Any] = [SystemMessage(content=system_prompt)]
        context_history = state.get("conversation_context", [])

        # Add up to last 8 turns of context
        for turn in context_history[-8:]:
            role = turn.get("role", "")
            content = turn.get("content", "")
            if not content:
                continue
            if role in ["user", "customer"]:
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))

        # Add current user message
        if current_user_message:
            messages.append(HumanMessage(content=current_user_message))

        return messages

    async def run(self, state: LoanApplicationState) -> Dict[str, Any]:
        """Main entry point for Master Agent"""
        user_message = state.get("user_message", "").strip()
        current_stage = state.get("current_stage", "greeting")
        customer_name = self._get_display_name(state.get("customer_name"))

        # 0. Adverse action / post-rejection consultative objection handling
        if state.get("application_status") == "rejected":
            return await self._handle_rejection_objection(state, user_message)

        # 1. Check if user is in onboarding (for guests/new visitors)
        if state.get("needs_onboarding", False):
            return await self._handle_onboarding(state, user_message)

        # 2. Extract key parameters from user message
        extracted = self._extract_all_info(user_message)
        updates: Dict[str, Any] = {}

        # 3. If an amount was provided or already present in state, save and move towards sales
        amount = extracted.get("amount") or state.get("loan_amount")
        purpose = extracted.get("purpose") or state.get("loan_purpose")
        tenure = extracted.get("tenure") or state.get("tenure_months")

        if extracted.get("amount"):
            updates["loan_amount"] = extracted["amount"]
            updates["amount_collected"] = True
        if extracted.get("purpose"):
            updates["loan_purpose"] = extracted["purpose"]
        if extracted.get("tenure"):
            updates["tenure_months"] = extracted["tenure"]
            updates["tenure_collected"] = True

        pre_approved = state.get("pre_approved_limit") or 0

        # 4. Generate dynamic, personalized response
        system_prompt = f"""You are Shruti, an intelligent, empathetic digital loan sales advisor at NBFC Finance.
You are chatting with {customer_name}.

CONTEXT:
- Pre-approved Limit: {"Rs. " + f"{pre_approved:,.0f}" if pre_approved > 0 else "Pending profile evaluation"}
- Desired Loan Amount: {"Rs. " + f"{amount:,.0f}" if amount else "Not yet specified"}
- Purpose: {purpose or "General personal need"}
- Current Stage: {current_stage}

GUIDELINES (EY Top-Tier Executive Standards):
1. Sound like a knowledgeable, human financial consultant — warm, confident, and professional.
2. Keep responses concise (2 to 4 sentences). Never dump walls of text.
3. Never ask repetitive questions. If the user already gave an amount or purpose, acknowledge it enthusiastically.
4. If the user mentions their need/purpose (e.g. medical, home renovation, wedding, travel, education), connect it to NBFC Finance's zero-collateral instant loan benefits.
5. If the user has given a loan amount, transition smoothly to calculate their customized EMI terms."""

        llm = get_conversational_llm()
        messages = self._build_messages_with_history(state, system_prompt, user_message)

        try:
            resp = await llm.ainvoke(messages)
            bot_text = str(resp.content).strip()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"[MasterAgent] LLM call failed, using consultative fallback: {e}")
            bot_text = self._intelligent_fallback_response(
                user_message, customer_name, amount, purpose, pre_approved
            )

        updates["bot_response"] = bot_text

        # 5. Routing Decision: If loan amount is known, hand over to Sales Agent
        if amount:
            updates["next_agent"] = "sales"
            updates["current_stage"] = "sales"
        else:
            updates["next_agent"] = "master"
            updates["current_stage"] = "discovery"

        # Update multi-turn dialog memory
        self._record_conversation(state, user_message, bot_text)
        return updates

    def _intelligent_fallback_response(
        self, user_msg: str, name: str, amount: Optional[float], purpose: Optional[str], pre_approved: float
    ) -> str:
        """Consultative financial discovery response when LLM is unavailable or loading"""
        msg = user_msg.lower().strip()

        # 1. Interest rates query
        if any(w in msg for w in ["rate", "interest", "roi", "charge", "fee", "cost", "percentage"]):
            rate_info = "starting at **10.50% p.a.** (reducing balance)"
            if pre_approved > 0:
                return (
                    f"Hi {name}! Our personal loan interest rates are {rate_info} with zero processing fees. "
                    f"Based on your profile, you are already pre-approved for up to **Rs. {pre_approved:,.0f}**. "
                    f"How much funding do you have in mind today?"
                )
            return (
                f"Hi {name}! Our personal loan interest rates start from **10.50% to 14.0% p.a.** (reducing balance), "
                f"with zero processing fees for qualified applicants and flexible 12 to 60-month tenures. "
                f"How much loan amount would you like to explore?"
            )

        # 2. Eligibility query
        if any(w in msg for w in ["eligib", "criteria", "qualif", "check", "am i eligible"]):
            if pre_approved > 0:
                return (
                    f"Great news, {name}! You are already pre-qualified with an instant limit of **Rs. {pre_approved:,.0f}**! "
                    f"No extra verification is needed within this limit. "
                    f"Would you like to apply for the full Rs. {pre_approved:,.0f} or a different amount?"
                )
            return (
                f"Hi {name}! Eligibility requires being an Indian resident aged 21-65 with a minimum CIBIL score of 700 and stable income. "
                f"Could you share how much funding you are looking for so I can assess your terms?"
            )

        # 3. Tenure query
        if any(w in msg for w in ["tenure", "term", "month", "year", "duration", "time", "period"]):
            return (
                f"Hi {name}! We offer flexible repayment tenures from **12 to 60 months** (1 to 5 years). "
                f"You also enjoy zero prepayment penalty after 6 completed EMIs! "
                f"What loan amount and tenure would you prefer?"
            )

        # 4. Document query
        if any(w in msg for w in ["doc", "paper", "aadhaar", "pan", "salary", "slip", "proof"]):
            if pre_approved > 0:
                return (
                    f"Hi {name}! Because you have a pre-approved offer of **Rs. {pre_approved:,.0f}**, "
                    f"you require **zero physical paperwork**! For amounts above your limit, only a recent salary slip is required. "
                    f"How much would you like to borrow?"
                )
            return (
                f"Hi {name}! Our process is 100% digital. All you need is your PAN and Aadhaar, "
                f"and a salary slip if requesting an enhanced amount. What loan amount are you considering?"
            )

        # 5. Amount given
        if amount:
            purp_str = f" for your {purpose}" if purpose else ""
            return f"Got it, {name}! Looking at Rs. {amount:,.0f}{purp_str}. Let me calculate your customized EMI options right away."

        # 6. Greetings or general discovery
        if pre_approved > 0:
            return (
                f"Hi {name}! Welcome to NBFC Finance. As a valued customer, you have a pre-approved limit of up to "
                f"**Rs. {pre_approved:,.0f}** available for immediate disbursal. What loan amount would you like to explore today?"
            )
        return (
            f"Hi {name}! Welcome to NBFC Finance. I'm Shruti, your loan advisor. We offer instant unsecured personal loans "
            f"from Rs. 50,00,000 to Rs. 15,00,000 at competitive rates. How much funding are you looking for?"
        )

    async def _handle_rejection_objection(self, state: LoanApplicationState, user_message: str) -> Dict[str, Any]:
        """Consultative objection handling when an application was previously rejected"""
        import logging
        logger = logging.getLogger(__name__)
        customer_name = self._get_display_name(state.get("customer_name"))
        credit_score = state.get("credit_score") or 680

        system_prompt = f"""You are Shruti, the empathetic and expert loan advisor at NBFC Finance.
Customer {customer_name} has had their unsecured personal loan application declined because their credit score is {credit_score}/900 (minimum required threshold is 700).

The customer is following up with: "{user_message}".

ROLE & CONSULTATIVE GUIDELINES:
1. Be warm, empathetic, and constructive. Acknowledge their situation with dignity.
2. Clearly outline 3 viable alternative financing solutions:
   • Co-Borrower / Co-Applicant: Add an immediate family member (spouse, parent, earning sibling) with a CIBIL score of 720+ for instant joint underwriting.
   • Secured Loan Options: Convert to Loan Against Property (LAP) or loan against FD/mutual funds where credit score restrictions are relaxed.
   • Credit Improvement: Clearing overdue card balances to bring credit utilization under 30% typically improves bureau score by 20-40 points within 60-90 days.
3. If they asked for a lower loan amount: Clarify that the minimum credit score requirement applies across all unsecured amounts under NBFC risk policy, so a co-applicant or secured loan is the quickest path.
4. Keep the response concise, formatted with clear bullet points, and offer to help them set up a co-applicant or secured application."""

        messages = self._build_messages_with_history(state, system_prompt, user_message)
        llm = get_conversational_llm()

        try:
            resp = await llm.ainvoke(messages)
            bot_text = str(resp.content).strip()
        except Exception as e:
            logger.warning(f"[MasterAgent] Adverse action LLM call failed, using fallback: {e}")
            bot_text = self._rejection_objection_fallback(customer_name, credit_score)

        updates: Dict[str, Any] = {
            "bot_response": bot_text,
            "current_stage": "adverse_action_consultation",
            "next_agent": "master",
            "should_end": False
        }
        self._record_conversation(state, user_message, bot_text)
        return updates

    def _rejection_objection_fallback(self, name: str, credit_score: int) -> str:
        return (
            f"I completely understand, {name}, and I'm here to help you explore alternative solutions! "
            f"While our automated underwriting policy requires a minimum credit score of 700 for an unsecured personal loan, "
            f"here are 3 concrete paths we can take right now:\n\n"
            f"1. **Add a Co-Borrower / Co-Applicant**: You can apply jointly with an immediate family member (spouse, parent, or earning sibling) "
            f"who has a credit score of 720+. Their score will qualify the application for immediate approval.\n\n"
            f"2. **Secured Loan Options**: We offer **Loan Against Property (LAP)** and loans backed by fixed deposits/securities with flexible credit score requirements and lower interest rates (starting at 9.25% p.a.).\n\n"
            f"3. **Credit Improvement (90 Days)**: Paying down existing revolving balances to bring utilization under 30% typically boosts your bureau score above 700 within 60 to 90 days.\n\n"
            f"Would you like to explore adding a co-applicant, or would you prefer details on our secured loan options?"
        )

    def _record_conversation(self, state: LoanApplicationState, user_msg: str, bot_msg: str):
        """Append turn to conversation context"""
        if "conversation_context" not in state or state["conversation_context"] is None:
            state["conversation_context"] = []
        if user_msg:
            state["conversation_context"].append({"role": "user", "content": user_msg})
        if bot_msg:
            state["conversation_context"].append({"role": "assistant", "content": bot_msg})
        # Keep last 16 turns to avoid context overflow
        state["conversation_context"] = state["conversation_context"][-16:]

    def _extract_all_info(self, text: str) -> Dict[str, Any]:
        """Robust extraction for Indian currency formats (lakhs, thousands, k, plain digits)"""
        msg = text.lower().strip()
        extracted: Dict[str, Any] = {}

        # 1. Lakhs: e.g. "5 lakhs", "5.5 lacs", "2 lakh", "10l"
        lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakhs?|lacs?|l\b)", msg)
        if lakh_match:
            extracted["amount"] = float(lakh_match.group(1)) * 100000

        # 2. Thousands: e.g. "50k", "500k"
        if "amount" not in extracted:
            k_match = re.search(r"(\d+(?:\.\d+)?)\s*k\b", msg)
            if k_match:
                extracted["amount"] = float(k_match.group(1)) * 1000

        # 3. Numeric string with rupee symbol or comma: e.g. "₹5,00,000", "Rs 500000"
        if "amount" not in extracted:
            rupee_match = re.search(r"(?:rs\.?|inr|₹)\s*([\d,]+(?:\.\d+)?)", msg)
            if rupee_match:
                cleaned = rupee_match.group(1).replace(",", "")
                try:
                    extracted["amount"] = float(cleaned)
                except ValueError:
                    pass

        # 4. Plain 5 to 7 digit numbers: e.g. "300000", "50000"
        if "amount" not in extracted:
            plain_match = re.search(r"\b(\d{5,7})\b", msg)
            if plain_match:
                extracted["amount"] = float(plain_match.group(1))

        # Purpose detection
        purposes = {
            "home renovation": ["home", "renovation", "house", "repair", "interior", "flat", "painting"],
            "wedding": ["wedding", "marriage", "shaadi", "engagement"],
            "medical emergency": ["medical", "hospital", "surgery", "treatment", "health", "emergency"],
            "education": ["education", "study", "college", "tuition", "school", "course", "fees"],
            "travel": ["travel", "vacation", "trip", "holiday", "flight"],
            "business expansion": ["business", "shop", "inventory", "working capital", "startup"],
            "debt consolidation": ["debt", "credit card", "settlement", "clear loan", "repay"],
            "personal": ["personal", "shopping", "gadgets", "laptop", "car", "bike"]
        }
        for purp, keys in purposes.items():
            if any(k in msg for k in keys):
                extracted["purpose"] = purp
                break

        # Tenure extraction: e.g. "2 years", "36 months", "3 yrs"
        yr_match = re.search(r"(\d+)\s*(?:years?|yrs?)", msg)
        if yr_match:
            extracted["tenure"] = int(yr_match.group(1)) * 12
        else:
            mo_match = re.search(r"(\d+)\s*(?:months?|mos?)", msg)
            if mo_match:
                extracted["tenure"] = int(mo_match.group(1))

        return extracted

    async def _handle_onboarding(self, state: LoanApplicationState, message: str) -> Dict[str, Any]:
        """Smooth conversational onboarding for first-time visitors or guest users"""
        step = state.get("onboarding_step", "name")
        updates: Dict[str, Any] = {}
        clean_msg = message.strip()

        if step == "name":
            # Avoid accepting generic greetings as names
            if clean_msg.lower() in ["hi", "hello", "hey", "namaste", "good morning", "yo"]:
                bot_resp = "Hello! Welcome to NBFC Finance. I'm Shruti, your loan advisor. What should I call you?"
                updates["onboarding_step"] = "name"
                updates["needs_onboarding"] = True
            else:
                extracted_name = re.sub(
                    r"^(?:my\s+name\s+is|i\s+am|i'm|this\s+is|call\s+me)\s+",
                    "",
                    clean_msg,
                    flags=re.IGNORECASE
                ).strip()
                name = extracted_name.title() if extracted_name else clean_msg.title()
                updates["customer_name"] = name
                first_name = name.split()[0]
                bot_resp = f"Pleasure to meet you, {first_name}! Could you share your 10-digit mobile number so I can check your pre-approved offers?"
                updates["onboarding_step"] = "phone"
                updates["needs_onboarding"] = True

        elif step == "phone":
            phone_clean = re.sub(r"[^\d]", "", clean_msg)
            if len(phone_clean) >= 10 and phone_clean[-10:][0] in "6789":
                phone = phone_clean[-10:]
                updates["customer_phone"] = f"+91-{phone}"
                bot_resp = f"Got it! And what is your age?"
                updates["onboarding_step"] = "age"
                updates["needs_onboarding"] = True
            else:
                bot_resp = "Please enter a valid 10-digit Indian mobile number (e.g. 9876543210)."
                updates["onboarding_step"] = "phone"
                updates["needs_onboarding"] = True

        elif step == "age":
            age_match = re.search(r"\b(\d{2})\b", clean_msg)
            if age_match and 18 <= int(age_match.group(1)) <= 75:
                age = int(age_match.group(1))
                updates["customer_age"] = age
                updates["needs_onboarding"] = False
                updates["onboarding_step"] = "done"
                updates["current_stage"] = "greeting"
                name = self._get_display_name(state.get("customer_name"))
                bot_resp = f"Thank you, {name}! You're all set. Based on initial eligibility, you can access pre-approved personal loans up to Rs. 5,00,000 at competitive rates. How much would you like to apply for?"
            else:
                bot_resp = "Please share your age (must be between 18 and 75 for eligibility)."
                updates["onboarding_step"] = "age"
                updates["needs_onboarding"] = True

        else:
            updates["needs_onboarding"] = False
            updates["current_stage"] = "greeting"
            name = self._get_display_name(state.get("customer_name"))
            bot_resp = f"Welcome back, {name}! How can I help you with your loan requirements today?"

        updates["bot_response"] = bot_resp
        updates["next_agent"] = "master"
        self._record_conversation(state, message, bot_resp)
        return updates


# Global singleton instance
master_agent_llm = MasterAgentLLM()
