"""
Master Test Runner for NBFC Conversational Loan Platform
Runs the complete test suite:
1. test_financial_math.py (Reducing-balance EMI, Dynamic Rates, Tenures)
2. test_document_vision.py (PDF Parsing, PyMuPDF, Vision Extraction Fallback)
3. test_agent_orchestration.py (All 10 Problem Statement Scenarios & Underwriting Rules)
"""
import sys
import os
import time

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import pytest


def main():
    print("\n" + "=" * 70)
    print("   🏦 NBFC LOAN PLATFORM — COMPREHENSIVE TEST SUITE")
    print("   EY Techathon 6.0: Agentic AI Orchestration & Policy Validation")
    print("=" * 70 + "\n")

    start_time = time.time()

    # Run pytest with verbose reporting
    test_args = [
        os.path.join(backend_dir, "tests"),
        "-v",
        "-s",
        "--tb=short"
    ]

    exit_code = pytest.main(test_args)
    duration = time.time() - start_time

    print("\n" + "=" * 70)
    if exit_code == 0:
        print(f"   ✅ ALL TESTS PASSED SUCCESSFULLY! (Completed in {duration:.2f}s)")
        print("   All underwriting policies, agent handoffs, and calculations validated.")
    else:
        print(f"   ❌ SOME TESTS FAILED (Exit code: {exit_code}) in {duration:.2f}s")
    print("=" * 70 + "\n")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
