"""
LangGraph State Definition
Defines the state structure for the loan application workflow
"""
from typing import TypedDict, List, Optional, Literal, Dict, Any
from langchain_core.messages import BaseMessage


class LoanApplicationState(TypedDict, total=False):
    """Comprehensive state for the NBFC loan application conversation"""
    
    # Conversation Core
    messages: List[BaseMessage]
    user_message: str
    bot_response: str
    conversation_context: List[Dict[str, str]]  # Full multi-turn dialog memory: [{"role": "user"/"assistant", "content": "..."}]
    
    # Customer Info
    customer_id: Optional[str]
    customer_email: Optional[str]
    customer_name: Optional[str]
    customer_phone: Optional[str]
    customer_age: Optional[int]
    customer_address: Optional[str]
    is_guest: bool
    is_mock_user: bool
    
    # Onboarding Control
    needs_onboarding: bool
    onboarding_step: Optional[str]  # "name", "phone", "age", "done"
    
    # Loan Parameters & Offer
    loan_amount: Optional[float]
    loan_purpose: Optional[str]
    tenure_months: Optional[int]
    interest_rate: Optional[float]
    emi_amount: Optional[float]
    emi_presented: bool
    amount_collected: bool
    tenure_collected: bool
    offer_presented: bool
    
    # Financial & Verification Metrics
    kyc_verified: bool
    verification_completed: bool
    credit_score: Optional[int]
    credit_rating: Optional[str]
    pre_approved_limit: Optional[float]
    monthly_salary: Optional[float]
    current_loans: Optional[Dict[str, float]]
    
    # Document Verification
    aadhaar_number: Optional[str]
    pan_number: Optional[str]
    awaiting_pan: bool
    uploaded_documents: Dict[str, str]  # e.g. {"aadhaar": "path/file.pdf", "salary_slip": "path/slip.png"}
    required_documents: List[str]
    pending_documents: List[str]
    documents_requested: bool
    
    # Workflow Stage & Status
    current_stage: str
    application_status: str
    next_agent: Optional[str]
    should_end: bool
    
    # Decisions & Sanction
    rejection_reason: Optional[str]
    sanction_letter_url: Optional[str]
    user_intent: Optional[str]
    
    # DB Linkage
    loan_application_id: Optional[str]
    conversation_id: Optional[str]
