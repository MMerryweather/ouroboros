"""LLM provider adapters for Ouroboros.

This module provides unified access to LLM providers through the LLMAdapter
protocol. AnthropicAdapter supports direct Claude API calls. LiteLLMAdapter
supports multi-provider routing. CodexAdapter provides Codex-native auth and
error semantics over LiteLLM.
"""

from ouroboros.providers.anthropic_adapter import AnthropicAdapter
from ouroboros.providers.base import (
    CompletionConfig,
    CompletionResponse,
    LLMAdapter,
    Message,
    MessageRole,
    UsageInfo,
)
from ouroboros.providers.codex_adapter import CodexAdapter
from ouroboros.providers.litellm_adapter import LiteLLMAdapter

__all__ = [
    # Protocol
    "LLMAdapter",
    # Models
    "Message",
    "MessageRole",
    "CompletionConfig",
    "CompletionResponse",
    "UsageInfo",
    # Implementations (AnthropicAdapter is the recommended default)
    "AnthropicAdapter",
    "LiteLLMAdapter",
    "CodexAdapter",
]
