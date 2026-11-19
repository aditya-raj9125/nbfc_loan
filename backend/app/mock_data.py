"""
Synthetic customer data for NBFC Loan Chatbot
10 diverse customer profiles with realistic Indian financial metrics
Includes Offer Mart, CRM KYC data, and Credit Bureau simulation
"""

MOCK_CUSTOMERS = [
    {
        "id": "cust_001",
        "name": "Rahul Sharma",
        "email": "rahul.sharma@email.com",
        "phone": "+91-9876543210",
        "age": 32,
        "city": "Mumbai",
        "address": "123 MG Road, Andheri West, Mumbai 400053",
        "kyc_verified": True,
        "credit_score": 782,
        "pre_approved_limit": 500000,
        "monthly_salary": 85000,
        "current_loans": {"home_loan": 2500000, "auto_loan": 0}
    },
    {
        "id": "cust_002",
        "name": "Priya Patel",
        "email": "priya.patel@email.com",
        "phone": "+91-9876543211",
        "age": 28,
        "city": "Bangalore",
        "address": "456 Indiranagar, Bangalore 560038",
        "kyc_verified": True,
        "credit_score": 820,
        "pre_approved_limit": 750000,
        "monthly_salary": 120000,
        "current_loans": {}
    },
    {
        "id": "cust_003",
        "name": "Amit Kumar",
        "email": "amit.kumar@email.com",
        "phone": "+91-9876543212",
        "age": 35,
        "city": "Delhi",
        "address": "789 Connaught Place, New Delhi 110001",
        "kyc_verified": True,
        "credit_score": 715,
        "pre_approved_limit": 300000,
        "monthly_salary": 65000,
        "current_loans": {"personal_loan": 150000}
    },
    {
        "id": "cust_004",
        "name": "Sneha Reddy",
        "email": "sneha.reddy@email.com",
        "phone": "+91-9876543213",
        "age": 30,
        "city": "Hyderabad",
        "address": "321 Banjara Hills, Hyderabad 500034",
        "kyc_verified": True,
        "credit_score": 750,
        "pre_approved_limit": 600000,
        "monthly_salary": 95000,
        "current_loans": {"auto_loan": 400000}
    },
    {
        "id": "cust_005",
        "name": "Vikram Singh",
        "email": "vikram.singh@email.com",
        "phone": "+91-9876543214",
        "age": 40,
        "city": "Pune",
        "address": "654 Koregaon Park, Pune 411001",
        "kyc_verified": True,
        "credit_score": 680,  # Demonstrates credit score < 700 edge-case rejection
        "pre_approved_limit": 400000,
        "monthly_salary": 75000,
        "current_loans": {"home_loan": 3000000, "personal_loan": 100000}
    },
    {
        "id": "cust_006",
        "name": "Anjali Verma",
        "email": "anjali.verma@email.com",
        "phone": "+91-9876543215",
        "age": 26,
        "city": "Chennai",
        "address": "987 T Nagar, Chennai 600017",
        "kyc_verified": False,  # Needs KYC verification flow
        "credit_score": 730,
        "pre_approved_limit": 250000,
        "monthly_salary": 55000,
        "current_loans": {}
    },
    {
        "id": "cust_007",
        "name": "Rajesh Gupta",
        "email": "rajesh.gupta@email.com",
        "phone": "+91-9876543216",
        "age": 45,
        "city": "Kolkata",
        "address": "147 Park Street, Kolkata 700016",
        "kyc_verified": True,
        "credit_score": 800,
        "pre_approved_limit": 1000000,
        "monthly_salary": 150000,
        "current_loans": {"home_loan": 1500000}
    },
    {
        "id": "cust_008",
        "name": "Meera Nair",
        "email": "meera.nair@email.com",
        "phone": "+91-9876543217",
        "age": 29,
        "city": "Kochi",
        "address": "258 Marine Drive, Kochi 682031",
        "kyc_verified": True,
        "credit_score": 740,
        "pre_approved_limit": 450000,
        "monthly_salary": 80000,
        "current_loans": {"auto_loan": 300000}
    },
    {
        "id": "cust_009",
        "name": "Arjun Malhotra",
        "email": "arjun.malhotra@email.com",
        "phone": "+91-9876543218",
        "age": 33,
        "city": "Chandigarh",
        "address": "369 Sector 17, Chandigarh 160017",
        "kyc_verified": True,
        "credit_score": 660,  # Demonstrates credit score < 700 rejection
        "pre_approved_limit": 350000,
        "monthly_salary": 70000,
        "current_loans": {"personal_loan": 200000}
    },
    {
        "id": "cust_010",
        "name": "Divya Iyer",
        "email": "divya.iyer@email.com",
        "phone": "+91-9876543219",
        "age": 31,
        "city": "Ahmedabad",
        "address": "741 SG Highway, Ahmedabad 380015",
        "kyc_verified": True,
        "credit_score": 790,
        "pre_approved_limit": 700000,
        "monthly_salary": 110000,
        "current_loans": {}
    }
]


# Offer Mart: Pre-approved offers mapped to each customer
OFFER_MART = {
    c["id"]: {
        "offers": [
            {
                "amount": c["pre_approved_limit"],
                "tenure": 36,
                "interest_rate": 10.5 if c["credit_score"] >= 750 else 11.5,
                "processing_fee": 0
            },
            {
                "amount": int(c["pre_approved_limit"] * 0.6),
                "tenure": 24,
                "interest_rate": 10.0 if c["credit_score"] >= 750 else 11.0,
                "processing_fee": 0
            }
        ]
    }
    for c in MOCK_CUSTOMERS
}


def get_customer_by_email(email: str):
    """Get mock customer data by email"""
    if not email:
        return None
    for customer in MOCK_CUSTOMERS:
        if customer["email"].lower() == email.lower():
            return customer
    return None


def get_customer_by_id(customer_id: str):
    """Get mock customer data by ID"""
    for customer in MOCK_CUSTOMERS:
        if customer["id"] == customer_id:
            return customer
    return None


def get_offers_for_customer(customer_id: str):
    """Get pre-approved offers for a customer from Offer Mart"""
    return OFFER_MART.get(customer_id, {"offers": []})
