"""Configuration for the Veritas Verification Layer."""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Council members - using the latest models
COUNCIL_MODELS = [
    "google/gemini-3.7-flash",
    "openai/gpt-5.6-sol",
    "anthropic/claude-sonnet-5",
    "x-ai/grok-4.6",
]

# Chairman model - synthesizes final verified response
CHAIRMAN_MODEL = "google/gemini-3.7-flash"

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Data directory for conversation storage
DATA_DIR = "data/conversations"

# Demo mode toggle (disabled for real API calls)
USE_DEMO_MODE = os.getenv("USE_DEMO_MODE", "false").lower() == "true"
