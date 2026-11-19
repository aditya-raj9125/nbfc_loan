"""
LLM Factory - Multimodal AI Provider (Google Gemini & Groq)
Primary: Google Gemini (Gemini 1.5 Flash / Pro) with native Multimodal Vision
Secondary: Groq Cloud API
"""
import logging
import os
from typing import Any
from app.config import get_settings

logger = logging.getLogger(__name__)


def _get_gemini_api_key(settings) -> str:
    """Retrieve Gemini API key from settings or environment variables"""
    return (
        getattr(settings, "GEMINI_API_KEY", "")
        or os.environ.get("GEMINI_API_KEY", "")
        or os.environ.get("GOOGLE_API_KEY", "")
    ).strip()


def get_conversational_llm() -> Any:
    """High-temperature LLM for natural, empathetic conversation (master, sales)."""
    settings = get_settings()
    gemini_key = _get_gemini_api_key(settings)

    if gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            model_name = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")
            logger.info(f"[LLMFactory] Using Google Gemini ({model_name}) for Conversational LLM")
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=gemini_key,
                temperature=0.7,
                max_output_tokens=1024,
                timeout=10.0,
                max_retries=1,
            )
        except Exception as e:
            logger.warning(f"[LLMFactory] Failed to initialize Gemini, checking Groq: {e}")

    # Fallback to Groq
    from langchain_groq import ChatGroq
    model_name = getattr(settings, "GROQ_MODEL", "llama-3.3-70b-versatile")
    logger.info(f"[LLMFactory] Using Groq ({model_name}) for Conversational LLM")
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=model_name,
        temperature=0.7,
        max_tokens=1024,
        request_timeout=10.0,
        max_retries=1,
    )


def get_analytical_llm() -> Any:
    """Low-temperature LLM for structured decisions (verification, underwriting, sanction)."""
    settings = get_settings()
    gemini_key = _get_gemini_api_key(settings)

    if gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            model_name = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=gemini_key,
                temperature=0.2,
                max_output_tokens=1024,
                timeout=10.0,
                max_retries=1,
            )
        except Exception as e:
            logger.warning(f"[LLMFactory] Failed to initialize Gemini for analytical: {e}")

    from langchain_groq import ChatGroq
    model_name = getattr(settings, "GROQ_MODEL", "llama-3.3-70b-versatile")
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=model_name,
        temperature=0.2,
        max_tokens=1024,
        request_timeout=10.0,
        max_retries=1,
    )


def get_vision_llm() -> Any:
    """Vision-capable LLM for document OCR — natively reads images and PDFs directly."""
    settings = get_settings()
    gemini_key = _get_gemini_api_key(settings)

    if gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            model_name = getattr(settings, "GEMINI_VISION_MODEL", "gemini-2.5-flash")
            logger.info(f"[LLMFactory] Using Google Gemini Multimodal Vision ({model_name})")
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=gemini_key,
                temperature=0.1,
                max_output_tokens=1024,
                timeout=15.0,
                max_retries=1,
            )
        except Exception as e:
            logger.warning(f"[LLMFactory] Failed to initialize Gemini Vision: {e}")

    from langchain_groq import ChatGroq
    model_name = getattr(settings, "GROQ_VISION_MODEL", "llama-3.2-11b-vision-preview")
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=model_name,
        temperature=0.1,
        max_tokens=1024,
        request_timeout=15.0,
        max_retries=1,
    )
