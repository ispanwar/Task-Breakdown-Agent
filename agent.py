import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq()

def create_task_breakdown_agent():
    """Create an agent that breaks down goals into executable tasks using Groq."""

    system_prompt = """You are an expert task breakdown agent. Your job is to help users accomplish their goals by:
1. Breaking down complex goals into clear, actionable steps
2. Prioritizing tasks based on dependencies and importance
3. Estimating effort levels (small, medium, large)
4. Identifying potential blockers or challenges
5. Suggesting resources or tools when relevant

When a user gives you a goal, respond with a structured JSON plan that includes:
- goal: the original goal
- steps: array of tasks with {title, description, priority (1-5, 5 is highest), effort (small/medium/large), dependencies}
- estimated_time: total estimated time
- tips: array of pro tips to complete this goal
- potential_challenges: array of obstacles to watch out for

Always think step by step about what's needed to accomplish the goal."""

    conversation_history = []

    def chat(user_message):
        """Send a message to the agent and get response."""
        conversation_history.append({
            "role": "user",
            "content": user_message
        })

        messages = [
            {"role": "system", "content": system_prompt}
        ] + conversation_history

        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            max_tokens=2048,
            messages=messages
        )

        assistant_message = response.choices[0].message.content
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def reset():
        """Reset conversation history."""
        conversation_history.clear()

    return {
        "chat": chat,
        "reset": reset,
        "get_history": lambda: conversation_history
    }
