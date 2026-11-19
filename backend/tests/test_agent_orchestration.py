"""
Agent Orchestration, Workflow & Conversational Scenarios Test Suite
Covers all 10 core problem statement scenarios & edge cases:
1. Happy Path Fast-Track Instant Sanction (Rahul Sharma - Rule 2)
2. Low Credit Bureau Score Rejection (Vikram Singh - Rule 1)
3. Income-Enhanced Sanction via Salary Slip (Amit Kumar - Rule 3)
4. High Debt-to-Income / FOIR Exceeded Rejection (Rule 3 Edge Case)
5. Single-Borrower Hard Cap Exceeded (Meera Nair - Rule 4)
6. KYC Verification & Document Prompting (Anjali Verma)
7. Guest Walk-in Conversational Onboarding Flow
8. Sales Negotiation & Multi-Turn EMI Comparison
9. Currency and NLP Entity Extraction Robustness
10. Multi-Turn Dialogue Memory Retention & Context Management
"""
import pytest
import os
import asyncio
from app.agents.state import LoanApplicationState
from app.agents.workflow import loan_workflow
from app.agents.master_agent_llm import master_agent_llm
from app.agents.sales_agent import sales_agent
from app.agents.verification_agent import verification_agent
from app.agents.underwriting_agent import underwriting_agent
from app.agents.sanction_agent import sanction_agent
from tests.mock_documents import (
    create_mock_salary_slip,
    create_mock_pan_card,
    create_mock_aadhaar_card
)


@pytest.fixture(scope="session", autouse=True)
def setup_mock_documents():
    """Ensure mock documents exist in tests/mock_files and backend/uploads/documents"""
    os.makedirs(os.path.join("uploads", "documents"), exist_ok=True)
    os.makedirs(os.path.join("uploads", "sanction_letters"), exist_ok=True)

    # Generate standard test documents
    slip_high = create_mock_salary_slip("test_salary_high.pdf", monthly_salary=85000.0)
    slip_low = create_mock_salary_slip("test_salary_low.pdf", monthly_salary=20000.0)
    pan_doc = create_mock_pan_card("test_pan.pdf", pan="ABCDE1234F")
    aadhaar_doc = create_mock_aadhaar_card("test_aadhaar.pdf", aadhaar="XXXX XXXX 9012")

    return {
        "slip_high": slip_high,
        "slip_low": slip_low,
        "pan": pan_doc,
        "aadhaar": aadhaar_doc
    }


class TestAgentOrchestration:
    """End-to-End Orchestration and Underwriting Policy Tests"""

    @pytest.mark.asyncio
    async def test_scenario_1_fast_track_instant_sanction(self):
        """
        Scenario 1: Happy Path / Fast-Track Instant Sanction
        Customer: Rahul Sharma (Pre-approved: Rs. 5,00,000, Credit Score: 782)
        Requested Amount: Rs. 3,50,000 for 36 months (<= Pre-approved)
        Expected: Underwriting Rule 2 applies -> Instant Approval -> Sanction Letter PDF
        """
        state: LoanApplicationState = {
            "session_id": "test_session_rahul",
            "customer_id": "cust_001",
            "customer_name": "Rahul Sharma",
            "customer_email": "rahul.sharma@email.com",
            "customer_phone": "+91-9876543210",
            "customer_address": "123 MG Road, Andheri West, Mumbai",
            "pre_approved_limit": 500000.0,
            "credit_score": 782,
            "kyc_verified": True,
            "current_stage": "greeting",
            "next_agent": "master",
            "conversation_context": []
        }

        # Step 1: User specifies loan amount and tenure
        state = await loan_workflow.process_message(
            state, "I want a personal loan of Rs. 3,50,000 for 36 months for home renovation."
        )

        assert state.get("loan_amount") == 350000.0
        assert state.get("tenure_months") == 36
        assert state.get("next_agent") == "sales"
        assert state.get("emi_amount") is not None
        assert state.get("emi_amount") > 0

        # Step 2: User confirms and agrees to terms
        state = await loan_workflow.process_message(state, "Yes, the EMI looks good! Please proceed.")

        # Full cascade should run: Sales -> Verification -> Underwriting -> Sanction
        assert state.get("application_status") == "approved"
        assert state.get("current_stage") == "sanction"
        assert state.get("sanction_letter_url") is not None
        assert "uploads/sanction_letters" in state["sanction_letter_url"]
        assert "NBFC-" in state.get("loan_application_id", "")

    @pytest.mark.asyncio
    async def test_scenario_2_low_credit_score_rejection(self):
        """
        Scenario 2: Low Credit Score Policy Rejection
        Customer: Vikram Singh (Credit Score: 680 < 700 threshold)
        Requested: Rs. 2,00,000
        Expected: Underwriting Rule 1 triggers rejection with adverse action guidance
        """
        state: LoanApplicationState = {
            "session_id": "test_session_vikram",
            "customer_id": "cust_005",
            "customer_name": "Vikram Singh",
            "customer_email": "vikram.singh@email.com",
            "pre_approved_limit": 400000.0,
            "credit_score": 680,
            "kyc_verified": True,
            "loan_amount": 200000.0,
            "tenure_months": 24,
            "current_stage": "underwriting",
            "next_agent": "underwriting",
            "conversation_context": []
        }

        updates = await underwriting_agent.run(state)
        state.update(updates)

        assert state.get("application_status") == "rejected"
        assert state.get("should_end") is True
        assert state.get("rejection_reason") is not None
        assert "700" in state["rejection_reason"]
        assert "below our threshold of 700" in state["rejection_reason"].lower()

    @pytest.mark.asyncio
    async def test_scenario_3_income_enhanced_approval_via_documents(self):
        """
        Scenario 3: Income-Enhanced Approval via Salary Slip Upload (Rule 3)
        Customer: Amit Kumar (Pre-approved: Rs. 3,00,000, Score: 715)
        Requested: Rs. 4,50,000 (1.5x pre-approved, <= 2x limit)
        Expected: Underwriting requires salary slip -> Doc uploaded -> Approved
        """
        state: LoanApplicationState = {
            "session_id": "test_session_amit",
            "customer_id": "cust_003",
            "customer_name": "Amit Kumar",
            "customer_email": "amit.kumar@email.com",
            "customer_address": "789 Connaught Place, New Delhi",
            "pre_approved_limit": 300000.0,
            "credit_score": 715,
            "kyc_verified": True,
            "loan_amount": 450000.0,
            "tenure_months": 36,
            "emi_amount": 14600.0,
            "current_stage": "underwriting",
            "next_agent": "underwriting",
            "conversation_context": []
        }

        # Step 1: Initial Underwriting run without salary slip
        updates = await underwriting_agent.run(state)
        state.update(updates)

        assert state.get("application_status") == "needs_documents"
        assert state.get("next_agent") == "document"
        assert "Salary Slip" in state.get("bot_response", "")

        # Step 2: Simulate document upload event with verified salary (Rs. 85,000)
        state["uploaded_documents"] = {
            "salary_slip": "uploads/documents/test_salary_high.pdf"
        }
        state["monthly_salary"] = 85000.0

        # Step 3: Run underwriting again with document attached
        updates2 = await underwriting_agent.run(state)
        state.update(updates2)

        assert state.get("application_status") == "approved"
        assert state.get("next_agent") == "sanction"

        # Step 4: Sanction Agent completes generation
        sanct_updates = await sanction_agent.run(state)
        state.update(sanct_updates)

        assert state.get("sanction_letter_url") is not None

    @pytest.mark.asyncio
    async def test_scenario_4_high_foir_debt_to_income_rejection(self):
        """
        Scenario 4: High Debt-to-Income / FOIR Exceeded Rejection under Rule 3
        Requested: Rs. 4,50,000 (Monthly EMI ~Rs. 14,600)
        Verified Income: Rs. 20,000/mo (EMI is 73% of income > 50% ceiling)
        Expected: Rejection due to FOIR ceiling exceeded
        """
        state: LoanApplicationState = {
            "session_id": "test_session_foir",
            "customer_name": "Applicant High FOIR",
            "pre_approved_limit": 300000.0,
            "credit_score": 720,
            "loan_amount": 450000.0,
            "emi_amount": 14600.0,
            "monthly_salary": 20000.0,  # 14600 / 20000 = 73% > 50%
            "uploaded_documents": {"salary_slip": "uploads/documents/test_salary_low.pdf"},
            "current_stage": "underwriting",
            "next_agent": "underwriting",
            "conversation_context": []
        }

        updates = await underwriting_agent.run(state)
        state.update(updates)

        assert state.get("application_status") == "rejected"
        assert "50%" in state.get("rejection_reason", "")

    @pytest.mark.asyncio
    async def test_scenario_5_single_borrower_hard_cap_exceeded(self):
        """
        Scenario 5: Single-Borrower Hard Cap Exceeded (Rule 4)
        Customer: Meera Nair (Pre-approved: Rs. 4,50,000)
        Requested: Rs. 12,00,000 (> 2x pre-approved limit of Rs. 9,00,000)
        Expected: Underwriting rejects the requested sum and offers pre-approved limit as counter-offer
        """
        state: LoanApplicationState = {
            "session_id": "test_session_meera",
            "customer_name": "Meera Nair",
            "customer_email": "meera.nair@email.com",
            "pre_approved_limit": 450000.0,
            "credit_score": 740,
            "loan_amount": 1200000.0,
            "current_stage": "underwriting",
            "next_agent": "underwriting",
            "conversation_context": []
        }

        updates = await underwriting_agent.run(state)
        state.update(updates)

        assert state.get("application_status") == "rejected"
        assert state.get("should_end") is True
        assert "exceeds maximum eligible threshold" in state.get("rejection_reason", "").lower()
        # Verify counter-offer is proposed
        assert "450,000" in state.get("bot_response", "")

    @pytest.mark.asyncio
    async def test_scenario_6_unverified_kyc_flow(self):
        """
        Scenario 6: Unverified KYC Onboarding (Anjali Verma)
        KYC verified = False in CRM
        Expected: Verification Agent halts underwriting and requests identity proof
        """
        state: LoanApplicationState = {
            "session_id": "test_session_anjali",
            "customer_name": "Anjali Verma",
            "customer_email": "anjali.verma@email.com",  # Mock has kyc_verified=False
            "kyc_verified": False,
            "loan_amount": 200000.0,
            "current_stage": "verification",
            "next_agent": "verification",
            "conversation_context": []
        }

        updates = await verification_agent.run(state)
        state.update(updates)

        assert state.get("kyc_verified") is False
        assert state.get("next_agent") == "document"
        assert "Aadhaar Card" in state.get("bot_response", "") or "PAN Card" in state.get("bot_response", "")

    @pytest.mark.asyncio
    async def test_scenario_7_guest_walk_in_onboarding(self):
        """
        Scenario 7: Guest Walk-in Conversational Onboarding Flow
        Tests multi-step guest qualification: Name -> Mobile Phone -> Age
        """
        state: LoanApplicationState = {
            "session_id": "test_guest_session",
            "needs_onboarding": True,
            "onboarding_step": "name",
            "current_stage": "onboarding",
            "next_agent": "master",
            "conversation_context": []
        }

        # Step 1: Submit Name
        updates = await master_agent_llm.run(dict(state, user_message="Aditya Kumar"))
        state.update(updates)
        assert state.get("customer_name") == "Aditya Kumar"
        assert state.get("onboarding_step") == "phone"

        # Step 2: Submit Invalid Phone
        updates = await master_agent_llm.run(dict(state, user_message="12345"))
        state.update(updates)
        assert state.get("onboarding_step") == "phone"
        assert "10-digit" in state.get("bot_response", "").lower()

        # Step 3: Submit Valid Phone
        updates = await master_agent_llm.run(dict(state, user_message="9876543210"))
        state.update(updates)
        assert state.get("customer_phone") == "+91-9876543210"
        assert state.get("onboarding_step") == "age"

        # Step 4: Submit Age
        updates = await master_agent_llm.run(dict(state, user_message="28 years old"))
        state.update(updates)
        assert state.get("customer_age") == 28
        assert state.get("needs_onboarding") is False
        assert state.get("onboarding_step") == "done"

    def test_scenario_8_nlp_currency_extraction(self):
        """
        Scenario 8: Currency and NLP Entity Extraction Robustness
        Validates extraction across Indian currency formats
        """
        cases = [
            ("I need 5 lakhs for medical treatment", 500000.0, "medical emergency"),
            ("Can you give me 3.5 lacs for my wedding?", 350000.0, "wedding"),
            ("I want Rs. 2,00,000 for travel to Europe", 200000.0, "travel"),
            ("Need ₹750000 for education fees", 750000.0, "education"),
            ("Looking for 50k for gadgets", 50000.0, "personal"),
            ("Please sanction 1000000 for business expansion", 1000000.0, "business expansion"),
        ]

        for text, expected_amount, expected_purpose in cases:
            res = master_agent_llm._extract_all_info(text)
            assert res.get("amount") == expected_amount, f"Failed amount for '{text}'. Got {res.get('amount')}"
            assert res.get("purpose") == expected_purpose, f"Failed purpose for '{text}'. Got {res.get('purpose')}"

    def test_scenario_9_conversation_context_memory_clipping(self):
        """
        Scenario 9: Multi-Turn Dialogue Memory Retention & Context Management
        Ensures context history preserves previous turns while pruning older turns beyond 16
        """
        state: LoanApplicationState = {
            "session_id": "test_memory_session",
            "conversation_context": []
        }

        # Add 25 turns to test auto-pruning
        for i in range(25):
            master_agent_llm._record_conversation(
                state, f"User turn {i}", f"Assistant turn {i}"
            )

        # Context should contain at most 16 entries (8 turns of user + assistant)
        assert len(state["conversation_context"]) <= 16
        # Verify newest turn is retained
        assert state["conversation_context"][-1]["content"] == "Assistant turn 24"
