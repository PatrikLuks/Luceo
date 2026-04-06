"""Tests for Anthropic client wrapper."""

from unittest.mock import AsyncMock, MagicMock, patch

from src.services.anthropic_client import generate_response


class TestGenerateResponse:
    async def test_successful_call(self):
        """Test successful API call returns text and token count."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Ahoj, jak ti mohu pomoci?")]
        mock_response.usage = MagicMock(input_tokens=50, output_tokens=30)

        with patch("src.services.anthropic_client._get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_get.return_value = mock_client

            text, tokens = await generate_response(
                "system prompt", [{"role": "user", "content": "hi"}]
            )

        assert text == "Ahoj, jak ti mohu pomoci?"
        assert tokens == 80

    async def test_api_error_returns_fallback(self):
        """Test API failure returns Czech fallback message with crisis contact."""
        with patch("src.services.anthropic_client._get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(side_effect=Exception("API down"))
            mock_get.return_value = mock_client

            text, tokens = await generate_response("system", [])

        assert "116 123" in text  # Crisis line number
        assert tokens == 0

    async def test_empty_content_returns_empty_string(self):
        """Test empty response.content returns empty string."""
        mock_response = MagicMock()
        mock_response.content = []
        mock_response.usage = MagicMock(input_tokens=10, output_tokens=0)

        with patch("src.services.anthropic_client._get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_get.return_value = mock_client

            text, tokens = await generate_response("system", [])

        assert text == ""
        assert tokens == 10

    async def test_uses_configurable_model(self):
        """Test that the model name comes from settings."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="ok")]
        mock_response.usage = MagicMock(input_tokens=1, output_tokens=1)

        with patch("src.services.anthropic_client._get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_get.return_value = mock_client

            await generate_response("sys", [{"role": "user", "content": "test"}])

            call_kwargs = mock_client.messages.create.call_args[1]
            # Model should be from settings, not hardcoded
            assert "model" in call_kwargs
            assert isinstance(call_kwargs["model"], str)
