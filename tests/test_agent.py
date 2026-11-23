from unittest.mock import MagicMock, patch

import pytest

from agent import AgentAPIError, create_task_breakdown_agent


def make_mock_response(content: str) -> MagicMock:
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content=content))]
    return response


def test_agent_dict_has_expected_keys():
    agent = create_task_breakdown_agent()
    assert set(agent.keys()) == {"chat", "reset", "get_history"}


@patch("agent.client.chat.completions.create")
def test_chat_sends_system_and_user_message_on_first_call(mock_create):
    mock_create.return_value = make_mock_response("hello")
    agent = create_task_breakdown_agent()

    agent["chat"]("break down my goal")

    sent_messages = mock_create.call_args.kwargs["messages"]
    assert sent_messages[0]["role"] == "system"
    assert sent_messages[-1] == {"role": "user", "content": "break down my goal"}


@patch("agent.client.chat.completions.create")
def test_chat_returns_assistant_content(mock_create):
    mock_create.return_value = make_mock_response("the plan")
    agent = create_task_breakdown_agent()

    result = agent["chat"]("goal")

    assert result == "the plan"


@patch("agent.client.chat.completions.create")
def test_history_accumulates_across_calls(mock_create):
    mock_create.side_effect = [make_mock_response("first"), make_mock_response("second")]
    agent = create_task_breakdown_agent()

    agent["chat"]("goal one")
    agent["chat"]("goal two")

    second_call_messages = mock_create.call_args.kwargs["messages"]
    assert {"role": "user", "content": "goal one"} in second_call_messages
    assert {"role": "assistant", "content": "first"} in second_call_messages
    assert second_call_messages[-1] == {"role": "user", "content": "goal two"}


@patch("agent.client.chat.completions.create")
def test_reset_clears_history(mock_create):
    mock_create.return_value = make_mock_response("reply")
    agent = create_task_breakdown_agent()

    agent["chat"]("goal")
    agent["reset"]()

    assert agent["get_history"]() == []


@patch("agent.client.chat.completions.create")
def test_get_history_matches_sent_and_received_turns(mock_create):
    mock_create.return_value = make_mock_response("reply")
    agent = create_task_breakdown_agent()

    agent["chat"]("goal")

    assert agent["get_history"]() == [
        {"role": "user", "content": "goal"},
        {"role": "assistant", "content": "reply"},
    ]


@patch("agent.client.chat.completions.create")
def test_api_failure_raises_agent_api_error_with_cause(mock_create):
    original_error = Exception("connection refused")
    mock_create.side_effect = original_error
    agent = create_task_breakdown_agent()

    with pytest.raises(AgentAPIError) as exc_info:
        agent["chat"]("goal")

    assert exc_info.value.__cause__ is original_error


@patch("agent.client.chat.completions.create")
def test_failed_call_leaves_no_dangling_user_message(mock_create):
    mock_create.side_effect = Exception("boom")
    agent = create_task_breakdown_agent()

    with pytest.raises(AgentAPIError):
        agent["chat"]("goal")

    assert agent["get_history"]() == []
