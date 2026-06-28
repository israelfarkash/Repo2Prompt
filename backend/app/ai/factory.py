"""
AI provider factory.

Central factory function for creating AI provider instances by name.
This allows the rest of the application to remain decoupled from any
specific AI provider implementation.
"""

from .base_provider import AIProvider
from .gemini_provider import GeminiProvider


def get_ai_provider(provider_name: str, api_key: str, model: str) -> AIProvider:
    """
    Create and return an AI provider instance based on the provider name.

    Args:
        provider_name: Identifier for the AI provider (e.g., 'gemini').
                       Case-insensitive.
        api_key: The API key for authenticating with the provider.
        model: The model identifier to use (e.g., 'gemini-2.5-flash').

    Returns:
        An initialized AIProvider instance ready for use.

    Raises:
        ValueError: If the provider_name does not match any known provider.
    """
    normalized = provider_name.strip().lower()

    if normalized == "gemini":
        return GeminiProvider(api_key=api_key, model=model)

    raise ValueError(
        f"Unknown AI provider: '{provider_name}'. "
        f"Supported providers: gemini"
    )
