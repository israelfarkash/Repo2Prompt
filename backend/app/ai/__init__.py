"""
AI provider package for the AI Project Reverse Engineer.

Public API:
    - AIProvider: Abstract base class defining the provider interface.
    - GeminiProvider: Google Gemini implementation.
    - get_ai_provider: Factory function to create providers by name.
"""

from .base_provider import AIProvider
from .factory import get_ai_provider
from .gemini_provider import GeminiProvider

__all__ = [
    "AIProvider",
    "GeminiProvider",
    "get_ai_provider",
]
