"""Anthropic Claude API wrapper — thin layer for testability."""

import logging

import anthropic

from src.core.config import settings

logger = logging.getLogger("luceo.anthropic")


async def generate_response(
    system_prompt: str,
    messages: list[dict],
    max_tokens: int = 1024,
) -> tuple[str, int]:
    """Call Claude API and return (response_text, total_token_count).

    Returns a fallback message on API failure — crisis contacts included.
    """
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
        )
        text = response.content[0].text
        tokens = response.usage.input_tokens + response.usage.output_tokens
        return text, tokens

    except anthropic.APIError as e:
        logger.error("Anthropic API error: %s", e)
        return (
            "Omlouvám se, momentálně nemohu odpovědět. Zkus to prosím za chvíli. "
            "Pokud potřebuješ okamžitou pomoc, zavolej na 116 123.",
            0,
        )
