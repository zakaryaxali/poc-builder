"""Claude API client with retry logic and streaming support."""

import os
import time
from typing import Any

from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError


class ClaudeClient:
    """Wrapper for Claude API with retry logic and error handling."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-20250514",
        max_retries: int = 3,
        timeout: float = 60.0,
    ):
        """Initialize Claude client.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model to use for generation
            max_retries: Maximum number of retry attempts for failed requests
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        self.client = Anthropic(api_key=self.api_key, timeout=timeout)

        # Token usage tracking
        self.input_tokens = 0
        self.output_tokens = 0

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """Generate text using Claude with automatic retry logic.

        Args:
            prompt: User prompt/message
            system: System prompt for context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)

        Returns:
            Generated text response

        Raises:
            APIError: If the request fails after all retries
        """
        messages = [{"role": "user", "content": prompt}]

        for attempt in range(self.max_retries):
            try:
                kwargs: dict[str, Any] = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }

                if system:
                    kwargs["system"] = system

                response = self.client.messages.create(**kwargs)

                # Track token usage
                if hasattr(response, 'usage'):
                    self.input_tokens += response.usage.input_tokens
                    self.output_tokens += response.usage.output_tokens

                # Extract text from response
                if response.content and len(response.content) > 0:
                    return response.content[0].text

                return ""

            except RateLimitError as e:
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    print(f"Rate limited. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise APIError(f"Rate limit exceeded after {self.max_retries} attempts") from e

            except APIConnectionError as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Connection error. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise APIError(f"Connection failed after {self.max_retries} attempts") from e

            except APIError as e:
                if attempt < self.max_retries - 1:
                    print(f"API error: {e}. Retrying...")
                    time.sleep(1)
                else:
                    raise

        raise APIError("Failed to generate response after all retries")

    def generate_structured(
        self,
        prompt: str,
        system: str | None = None,
        schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate structured JSON output.

        Args:
            prompt: User prompt requesting JSON output
            system: System prompt
            schema: Optional JSON schema for validation

        Returns:
            Parsed JSON response as dictionary
        """
        # Add JSON instruction to prompt
        json_prompt = f"{prompt}\n\nRespond with valid JSON only, no other text."

        response = self.generate(prompt=json_prompt, system=system, temperature=0.3)

        # Extract JSON from response (handle code blocks)
        import json
        import re

        # Try to find JSON in code blocks first
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Otherwise try to parse the whole response
            json_str = response.strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response}") from e

    def get_token_usage(self) -> dict[str, int]:
        """Get total token usage since client initialization or last reset.

        Returns:
            Dictionary with input_tokens, output_tokens, and total_tokens
        """
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
        }

    def reset_token_usage(self) -> None:
        """Reset token usage counters to zero."""
        self.input_tokens = 0
        self.output_tokens = 0
