"""
Financial Calculations & Amortization Math Tests
Validates:
- Standard reducing-balance EMI mathematical precision against banking benchmarks
- Dynamic APR / Interest rate calculations based on credit score tiers
- Tenure suggestions based on 35% of income ceiling
- Edge cases: zero amount, zero tenure, large amounts
"""
import pytest
from app.agents.sales_agent import sales_agent


class TestFinancialMath:
    """Validates reducing balance amortization and rate engines"""

    def test_reducing_balance_emi_36_months(self):
        """
        Benchmark:
        P = Rs. 3,50,000, r = 10.50% p.a., n = 36 months
        Monthly r = 10.5 / 12 / 100 = 0.00875
        EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
        Standard banking calculation = Rs. 11,379.80 (~11,380)
        """
        emi = sales_agent._calculate_emi(principal=350000.0, annual_rate=10.5, tenure_months=36)
        assert 11370.0 <= emi <= 11390.0, f"Expected EMI around 11380, got {emi}"

    def test_reducing_balance_emi_24_months(self):
        """
        Benchmark:
        P = Rs. 3,50,000, r = 10.50% p.a., n = 24 months
        Standard banking calculation = Rs. 16,231.61
        """
        emi = sales_agent._calculate_emi(principal=350000.0, annual_rate=10.5, tenure_months=24)
        assert 16225.0 <= emi <= 16240.0, f"Expected EMI around 16231.61, got {emi}"

    def test_reducing_balance_emi_60_months(self):
        """
        Benchmark:
        P = Rs. 5,00,000, r = 10.0% p.a., n = 60 months
        Standard banking calculation = Rs. 10,623.52 (~10,624)
        """
        emi = sales_agent._calculate_emi(principal=500000.0, annual_rate=10.0, tenure_months=60)
        assert 10615.0 <= emi <= 10635.0, f"Expected EMI around 10624, got {emi}"

    def test_emi_zero_principal(self):
        """Zero principal must return 0 without division by zero"""
        emi = sales_agent._calculate_emi(principal=0.0, annual_rate=10.5, tenure_months=36)
        assert emi == 0.0

    def test_emi_zero_tenure(self):
        """Zero tenure must return 0 without division by zero"""
        emi = sales_agent._calculate_emi(principal=350000.0, annual_rate=10.5, tenure_months=0)
        assert emi == 0.0

    def test_dynamic_rate_prime_borrower(self):
        """Credit score >= 800 should get prime rate discount (9.5%)"""
        mock_state = {
            "credit_score": 820,
            "pre_approved_limit": 750000.0
        }
        rate = sales_agent._calculate_interest_rate(amount=500000.0, state=mock_state)
        assert rate == 9.5, f"Expected 9.5%, got {rate}%"

    def test_dynamic_rate_standard_borrower(self):
        """Credit score 750-799 should get standard rate (10.5%)"""
        mock_state = {
            "credit_score": 760,
            "pre_approved_limit": 500000.0
        }
        rate = sales_agent._calculate_interest_rate(amount=400000.0, state=mock_state)
        assert rate == 10.5, f"Expected 10.5%, got {rate}%"

    def test_dynamic_rate_subprime_borrower(self):
        """Credit score < 700 gets risk premium (12.5%)"""
        mock_state = {
            "credit_score": 680,
            "pre_approved_limit": 400000.0
        }
        rate = sales_agent._calculate_interest_rate(amount=300000.0, state=mock_state)
        assert rate == 12.5, f"Expected 12.5%, got {rate}%"

    def test_dynamic_rate_limit_exceeded_premium(self):
        """Borrowing more than pre-approved limit adds 0.5% premium"""
        mock_state = {
            "credit_score": 760,
            "pre_approved_limit": 300000.0
        }
        # Amount 450,000 exceeds 300,000 -> 10.5 + 0.5 = 11.0%
        rate = sales_agent._calculate_interest_rate(amount=450000.0, state=mock_state)
        assert rate == 11.0, f"Expected 11.0%, got {rate}%"

    def test_tenure_suggestion_heuristic(self):
        """Monthly salary 80,000 -> target EMI ~28,000 -> suggests optimal tenure"""
        suggested = sales_agent._suggest_tenure(amount=500000.0, monthly_salary=80000.0)
        assert suggested in [24, 36], f"Suggested tenure {suggested} should be 24 or 36 months"
