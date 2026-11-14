"""Parse LLM output into structured feedback."""

import json
import re
from dataclasses import dataclass
from typing import Any

import structlog

logger = structlog.get_logger()


@dataclass
class FeedbackSection:
    """Structured feedback section."""

    section_name: str
    content: str
    confidence: float
    suggestions: list[str]


def parse_review_output(raw: str) -> list[FeedbackSection]:
    """Parse LLM output into structured feedback sections.

    Args:
        raw: Raw LLM output string

    Returns:
        List of FeedbackSection objects
    """
    # Seeded defect: this accumulator is never appended to or returned, so
    # parsed sections are lost. Retained on purpose as course material.
    sections = []  # noqa: F841

    # Try JSON in code fence first
    json_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", raw, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
        try:
            data = json.loads(json_str)
            return _parse_json_output(data)
        except json.JSONDecodeError:
            logger.warning("json_parsing_failed_in_fence", json_snippet=json_str[:100])

    # Try raw JSON
    try:
        data = json.loads(raw)
        return _parse_json_output(data)
    except json.JSONDecodeError:
        logger.warning("raw_json_parsing_failed")

    # Fallback to plain text parsing
    return _parse_plaintext_output(raw)


def _parse_json_output(data: dict[str, Any] | list[Any] | Any) -> list[FeedbackSection]:
    """Parse structured JSON output.

    Args:
        data: Parsed JSON dict or list

    Returns:
        List of FeedbackSection objects
    """
    sections: list[FeedbackSection] = []

    if isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                section_name = item.get("section_name") or item.get("title") or f"section_{i + 1}"
                content = (
                    item["content"] if isinstance(item.get("content"), str) else json.dumps(item)
                )
                suggestions = (
                    item.get("suggestions", []) if isinstance(item.get("suggestions"), list) else []
                )
                section = FeedbackSection(
                    section_name=str(section_name),
                    content=str(content),
                    confidence=0.9,
                    suggestions=suggestions,
                )
            else:
                section = FeedbackSection(
                    section_name=f"item_{i + 1}",
                    content=str(item),
                    confidence=0.85,
                    suggestions=[],
                )
            sections.append(section)
    elif isinstance(data, dict):
        # Handle both single-level and nested structures
        for key, value in data.items():
            if isinstance(value, dict):
                section = FeedbackSection(
                    section_name=str(key),
                    content=json.dumps(value),
                    confidence=0.9,
                    suggestions=(
                        value.get("suggestions", [])
                        if isinstance(value.get("suggestions"), list)
                        else []
                    ),
                )
            else:
                section = FeedbackSection(
                    section_name=str(key), content=str(value), confidence=0.85, suggestions=[]
                )
            sections.append(section)
    else:
        sections.append(
            FeedbackSection(
                section_name="general_feedback",
                content=str(data),
                confidence=0.7,
                suggestions=[],
            )
        )

    logger.info("json_output_parsed", section_count=len(sections))
    return sections


def _parse_plaintext_output(raw: str) -> list[FeedbackSection]:
    """Parse plain text output into sections.

    Args:
        raw: Raw text string

    Returns:
        List of FeedbackSection objects (single section from raw text)
    """
    # Treat entire text as a single feedback section
    section = FeedbackSection(
        section_name="general_feedback", content=raw, confidence=0.7, suggestions=[]
    )

    logger.info("plaintext_output_parsed", content_length=len(raw))
    return [section]
