import json

import pytest

from plan_parser import PlanParseError, extract_json_block, parse_plan_response

FULL_PLAN = {
    "goal": "Learn Python",
    "steps": [
        {"title": "Install Python", "description": "Get it set up", "priority": 5, "effort": "small"}
    ],
    "estimated_time": "2 weeks",
    "tips": ["Practice daily"],
    "potential_challenges": ["Time management"],
}


def test_plain_json_no_fences():
    text = json.dumps({"goal": "x"})
    assert parse_plan_response(text) == {"goal": "x"}


def test_json_fences_with_language_tag():
    text = f"```json\n{json.dumps({'goal': 'x'})}\n```"
    assert parse_plan_response(text) == {"goal": "x"}


def test_json_fences_without_language_tag():
    text = f"```\n{json.dumps({'goal': 'x'})}\n```"
    assert parse_plan_response(text) == {"goal": "x"}


def test_json_with_surrounding_prose():
    text = f"Here's your plan:\n{json.dumps({'goal': 'x'})}\nHope this helps!"
    assert parse_plan_response(text) == {"goal": "x"}


def test_nested_braces_extracted_fully():
    text = json.dumps(FULL_PLAN)
    assert parse_plan_response(text) == FULL_PLAN


def test_no_json_present_raises():
    with pytest.raises(PlanParseError):
        extract_json_block("just plain text, no JSON here")


def test_malformed_json_raises_with_cause_chained():
    text = '{"goal": "x",}'  # trailing comma - invalid JSON
    with pytest.raises(PlanParseError) as exc_info:
        parse_plan_response(text)
    assert isinstance(exc_info.value.__cause__, json.JSONDecodeError)


def test_empty_string_raises():
    with pytest.raises(PlanParseError):
        extract_json_block("")


def test_whitespace_only_raises():
    with pytest.raises(PlanParseError):
        extract_json_block("   \n\t  ")


def test_full_schema_shape_parses_correctly():
    text = f"```json\n{json.dumps(FULL_PLAN)}\n```"
    result = parse_plan_response(text)
    assert result == FULL_PLAN
    assert set(result.keys()) == {
        "goal", "steps", "estimated_time", "tips", "potential_challenges"
    }
