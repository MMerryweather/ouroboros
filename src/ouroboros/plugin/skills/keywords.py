"""Magic keyword detection for skill routing.

This module provides:
- Command-prefix detection in user messages
- Priority-based matching with deterministic tie-breaking
- Trigger-keyword routing when no prefix route is selected
- Fallback handling for no matches
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Any

import structlog

from ouroboros.plugin.skills.registry import SkillRegistry, get_registry

log = structlog.get_logger()


class MatchType(Enum):
    """Type of keyword match."""

    EXACT_PREFIX = "exact_prefix"  # Exact magic prefix match (highest priority)
    PARTIAL_PREFIX = "partial_prefix"  # Partial prefix match
    TRIGGER_KEYWORD = "trigger_keyword"  # Natural language trigger
    FALLBACK = "fallback"  # No match, use default


@dataclass
class KeywordMatch:
    """Result of keyword detection.

    Attributes:
        skill_name: Name of the matched skill.
        match_type: Type of match that occurred.
        matched_text: The text that matched.
        confidence: Confidence score (0.0 to 1.0).
        metadata: Additional match metadata.
    """

    skill_name: str
    match_type: MatchType
    matched_text: str
    confidence: float
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Validate confidence is in valid range."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


class MagicKeywordDetector:
    """Detects magic keywords and routes to appropriate skills.

    Routing contract:
    1. `ooo <subcommand>` at message start
    2. bare `ooo` -> `welcome`
    3. trigger keywords only when no prefix route exists
    Tie-breaker: longest match first, then lexical skill name.
    """

    # Common magic prefix patterns
    PREFIX_PATTERNS = [
        r"^/?(ouroboros|ooo):(\w+)",  # /ouroboros:run, ooo:interview
        r"^(\w+)\s+(ouroboros|ooo)\s+(\w+)",  # "please ouroboros run"
        r"^(?:/?)?ooo\s+(\w+)",  # "ooo run", "ooo interview" (ooo without colon)
    ]

    def __init__(self, registry: SkillRegistry | None = None) -> None:
        """Initialize the keyword detector.

        Args:
            registry: Optional skill registry. Uses global singleton if not provided.
        """
        self._registry = registry or get_registry()
        self._compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.PREFIX_PATTERNS
        ]

    def detect(self, user_input: str) -> list[KeywordMatch]:
        """Detect magic keywords in user input.

        Args:
            user_input: The user's input text.

        Returns:
            List of keyword matches, sorted by confidence (highest first).
        """
        prefix_matches = self._detect_prefixes(user_input)
        if prefix_matches:
            return self._sort_matches(prefix_matches)

        trigger_matches = self._detect_triggers(user_input)
        return self._sort_matches(trigger_matches)

    def detect_best(self, user_input: str) -> KeywordMatch | None:
        """Detect the single best matching skill.

        Args:
            user_input: The user's input text.

        Returns:
            The best match if found, None otherwise.
        """
        matches = self.detect(user_input)
        return matches[0] if matches else None

    def _detect_prefixes(self, user_input: str) -> list[KeywordMatch]:
        """Detect magic prefix matches in user input.

        Args:
            user_input: The user's input text.

        Returns:
            List of prefix matches.
        """
        matches: list[KeywordMatch] = []
        stripped = user_input.strip()
        lowered = stripped.lower()

        # Contract (1): explicit `ooo <subcommand>` at message start.
        start_match = re.match(r"^ooo\s+([a-z0-9_-]+)\b", lowered)
        if start_match:
            skill_name = start_match.group(1)
            if self._registry.get_skill(skill_name):
                return [
                    KeywordMatch(
                        skill_name=skill_name,
                        match_type=MatchType.EXACT_PREFIX,
                        matched_text=start_match.group(0),
                        confidence=1.0,
                    )
                ]

        # Contract (2): bare `ooo` routes to welcome.
        if lowered == "ooo" and self._registry.get_skill("welcome"):
            return [
                KeywordMatch(
                    skill_name="welcome",
                    match_type=MatchType.EXACT_PREFIX,
                    matched_text=stripped,
                    confidence=1.0,
                )
            ]

        # Backward-compatible prefix patterns (lower precedence than explicit contract path).
        for pattern in self._compiled_patterns:
            for match in pattern.finditer(user_input):
                groups = match.groups()
                skill_name = None
                for group in groups:
                    if group and re.fullmatch(r"[a-zA-Z0-9_-]+", group):
                        candidate = group.lower()
                        if self._registry.get_skill(candidate):
                            skill_name = candidate
                            break

                if skill_name:
                    matches.append(
                        KeywordMatch(
                            skill_name=skill_name,
                            match_type=MatchType.PARTIAL_PREFIX,
                            matched_text=match.group(0),
                            confidence=0.9,
                            metadata={"pattern": pattern.pattern},
                        )
                    )

        return matches

    def _detect_triggers(self, user_input: str) -> list[KeywordMatch]:
        """Detect trigger keyword matches in user input.

        Args:
            user_input: The user's input text.

        Returns:
            List of trigger matches.
        """
        matches: list[KeywordMatch] = []
        input_lower = user_input.lower()

        # Get all skills with trigger keywords
        all_metadata = self._registry.get_all_metadata()

        for skill_name in sorted(all_metadata):
            metadata = all_metadata[skill_name]
            if not metadata.trigger_keywords:
                continue

            for keyword in sorted(metadata.trigger_keywords, key=lambda k: (-len(k), k.lower())):
                keyword_lower = keyword.lower()
                if keyword_lower in input_lower:
                    # Calculate confidence based on match specificity
                    confidence = self._calculate_trigger_confidence(
                        keyword_lower,
                        input_lower,
                    )

                    matches.append(
                        KeywordMatch(
                            skill_name=skill_name,
                            match_type=MatchType.TRIGGER_KEYWORD,
                            matched_text=keyword,
                            confidence=confidence,
                            metadata={"keyword": keyword},
                        )
                    )

        return matches

    def _sort_matches(self, matches: list[KeywordMatch]) -> list[KeywordMatch]:
        """Sort matches by contract priority and deterministic tie-breakers."""
        priority = {
            MatchType.EXACT_PREFIX: 3,
            MatchType.PARTIAL_PREFIX: 2,
            MatchType.TRIGGER_KEYWORD: 1,
            MatchType.FALLBACK: 0,
        }
        return sorted(
            matches,
            key=lambda m: (
                -priority.get(m.match_type, 0),
                -len(m.matched_text),
                m.skill_name,
            ),
        )

    def _calculate_trigger_confidence(
        self,
        keyword: str,
        input_text: str,
    ) -> float:
        """Calculate confidence score for a trigger keyword match.

        Args:
            keyword: The matched keyword.
            input_text: The input text that matched.

        Returns:
            Confidence score between 0.0 and 1.0.
        """
        # Exact match = 1.0
        if keyword == input_text:
            return 1.0

        # Keyword at start = 0.9
        if input_text.startswith(keyword):
            return 0.9

        # Contains keyword with word boundary = 0.8
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, input_text):
            return 0.8

        # Substring match = 0.6
        if keyword in input_text:
            return 0.6

        return 0.5


def detect_magic_keywords(
    user_input: str,
    registry: SkillRegistry | None = None,
) -> list[KeywordMatch]:
    """Convenience function to detect magic keywords.

    Args:
        user_input: The user's input text.
        registry: Optional skill registry.

    Returns:
        List of keyword matches, sorted by confidence.
    """
    detector = MagicKeywordDetector(registry)
    return detector.detect(user_input)


def route_to_skill(
    user_input: str,
    registry: SkillRegistry | None = None,
) -> tuple[str | None, MatchType]:
    """Route user input to the best matching skill.

    Args:
        user_input: The user's input text.
        registry: Optional skill registry.

    Returns:
        Tuple of (skill_name, match_type). Returns (None, MatchType.FALLBACK) if no match.
    """
    detector = MagicKeywordDetector(registry)
    match = detector.detect_best(user_input)

    if match:
        return match.skill_name, match.match_type

    return None, MatchType.FALLBACK


def is_magic_command(user_input: str) -> bool:
    """Check if user input is a magic command.

    Args:
        user_input: The user's input text.

    Returns:
        True if input appears to be a magic command.
    """
    # Quick check for common patterns
    input_lower = user_input.strip().lower()
    magic_indicators = [
        "ooo:",
        "/ouroboros:",
        "ouroboros:",
        "ooo ",  # "ooo run"
    ]

    return any(indicator in input_lower for indicator in magic_indicators)
