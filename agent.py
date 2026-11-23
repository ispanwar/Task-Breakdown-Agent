from typing import Any, Callable

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq()

PLAN_JSON_SCHEMA_DESCRIPTION = (
    '{"goal": "", "steps": [{"title": "", "description": "", '
    '"priority": 1, "effort": "small/medium/large", "dependencies": []}], '
    '"estimated_time": "", "tips": [], "potential_challenges": []} '
    '(priority is an integer from 1 to 5, not a string)'
)


class AgentAPIError(Exception):
    """Raised when the underlying Groq API call fails (network, auth, rate limit, etc.)."""


def create_task_breakdown_agent() -> dict[str, Callable[..., Any]]:
    """Create an agent that breaks down goals into executable tasks using Groq."""

    system_prompt = f"""You are an expert task breakdown agent. Your job is to help users accomplish their goals by:
1. Breaking down complex goals into clear, actionable steps
2. Prioritizing tasks based on dependencies and importance
3. Estimating effort levels (small, medium, large)
4. Identifying potential blockers or challenges
5. Suggesting resources or tools when relevant

When a user gives you a goal, respond with a structured JSON plan matching this shape:
{PLAN_JSON_SCHEMA_DESCRIPTION}

Always think step by step about what's needed to accomplish the goal."""

    conversation_history: list[dict[str, str]] = []

    def chat(user_message: str) -> str:
        """Send a message to the agent and get response."""
        messages = (
            [{"role": "system", "content": system_prompt}]
            + conversation_history
            + [{"role": "user", "content": user_message}]
        )

        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                max_tokens=2048,
                messages=messages,
            )
        except Exception as e:
            raise AgentAPIError(f"Groq API request failed: {e}") from e

        assistant_message = response.choices[0].message.content
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": assistant_message})

        return assistant_message

    def reset() -> None:
        """Reset conversation history."""
        conversation_history.clear()

    return {
        "chat": chat,
        "reset": reset,
        "get_history": lambda: conversation_history,
    }
