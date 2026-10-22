
"""Integration test for a running local Ollama model."""

import pytest

from src.local_llm import OllamaPolicy
from src.tools import parse_request


@pytest.mark.integration
def test_ollama_returns_a_valid_tool_request():
    policy = OllamaPolicy(model="qwen2.5:0.5b")

    result = policy.next_request(
        observation=None,
        trace=(),
        remaining_actions=20,
    )

    assert parse_request(result).tool == result["tool"]
