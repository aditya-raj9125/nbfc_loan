"""
LLM Factory - Provides Groq LLMs for all agents
Conversational (temp 0.7) for master/sales, analytical (temp 0.3) for verification/underwriting/sanction,
and vision (temp 0.1) for document OCR (Aadhaar, PAN, Salary Slip).
"""
import logging
from langchain_groq import ChatGroq
from app.config import get_settings

logger = logging.getLogger(__name__)


def get_conversational_llm() -> ChatGroq:
    """High-temperature LLM for natural, empathetic conversation (master, sales, document agents)."""
    settings = get_settings()
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=0.7,
        max_tokens=1024,
    )


def get_analytical_llm() -> ChatGroq:
    """Low-temperature LLM for structured decisions (verification, underwriting, sanction)."""
    settings = get_settings()
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=0.2,
        max_tokens=1024,
    )


def get_vision_llm() -> ChatGroq:
    """Vision-capable LLM for document OCR — reads images and PDFs directly."""
    settings = get_settings()
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_VISION_MODEL,
        temperature=0.1,
        max_tokens=1024,
    )


# Module-level instances with fallback
try:
    conversational_llm = get_conversational_llm()
    analytical_llm = get_analytical_llm()
    vision_llm = get_vision_llm()
    logger.info("LLM instances initialized successfully.")
except Exception as e:
    logger.warning("LLM initialization warning: %s", e)
    conversational_llm = None
    analytical_llm = None
    vision_llm = None
