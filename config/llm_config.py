#!/usr/bin/env python3
"""
LLM Model Configuration - Groq Only
This project uses Groq as the primary LLM provider for data extraction.
API key is loaded from environment variables via .env file.
"""

# Import settings to access API keys from environment variables
from config.settings import settings

# =============================================================================
# PRIMARY MODEL CONFIGURATION
# =============================================================================
PRIMARY_MODEL = "GROQ"  # Only Groq is supported

# =============================================================================
# GROQ CONFIGURATION
# =============================================================================

# Groq Configuration - Fast LLM with excellent performance
# API key is loaded from environment variables via settings (never hardcode here)
GROQ_CONFIG = {
    "name": "GROQ",
    "api_key": settings.GROQ_API_KEY,  # Loaded from .env file via settings
    "model": "llama-3.3-70b-versatile",  # Groq model: llama-3.3-70b-versatile (70B - better quality) or llama-3.1-8b-instant (8B - faster)
    "temperature": 0.3,
    "max_tokens": 8000,
    "top_p": 0.8,
    "streaming": False,
    "timeout": 120  # 70B model may take slightly longer, increased timeout to 120s
}

# =============================================================================
# MODEL PRIORITY AND FALLBACK CONFIGURATION
# =============================================================================

# Only Groq is supported - no fallback models
MODEL_PRIORITY = {
    "GROQ": ["GROQ"]  # Only Groq
}

# Get current model priority (only Groq)
CURRENT_MODEL_PRIORITY = MODEL_PRIORITY.get(PRIMARY_MODEL, ["GROQ"])

# =============================================================================
# VALIDATION
# =============================================================================

VALID_MODELS = ["GROQ"]

if PRIMARY_MODEL not in VALID_MODELS:
    raise ValueError(f"Invalid PRIMARY_MODEL: {PRIMARY_MODEL}. Must be: GROQ")

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_primary_model():
    """Get the current primary model name"""
    return PRIMARY_MODEL

def get_model_config(model_name: str):
    """Get configuration for a specific model"""
    if model_name == "GROQ":
        return GROQ_CONFIG
    return None

def get_current_priority():
    """Get current model priority list"""
    return CURRENT_MODEL_PRIORITY

def is_groq_primary():
    """Check if Groq is the primary model"""
    return PRIMARY_MODEL == "GROQ"
