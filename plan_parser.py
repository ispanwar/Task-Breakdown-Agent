"""Helpers for extracting and parsing JSON task plans from LLM responses."""

import json
import re


class PlanParseError(Exception):
    """Raised when a model response cannot be parsed into a plan JSON object."""


def extract_json_block(text: str) -> str:
    """Strip markdown code fences and return the first {...} JSON object substring."""
    cleaned = text.strip()
    cleaned = re.sub(r"```json\s*", "", cleaned)
    cleaned = re.sub(r"```\s*", "", cleaned)

    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        raise PlanParseError("Could not extract JSON from response")
    return match.group(0)


def parse_plan_response(text: str) -> dict:
    """Extract and parse a plan JSON object from a raw model response."""
    json_str = extract_json_block(text)
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise PlanParseError(f"Invalid JSON in response: {e}") from e
