# Task Breakdown Agent 🤖

A simple AI agent that helps you break down complex goals into actionable, prioritized tasks using Claude and Streamlit.

## Features

- **Goal Analysis**: Input any complex goal
- **Task Breakdown**: Agent creates structured, prioritized task plans
- **Smart Prioritization**: Tasks ranked by importance (1-5 scale)
- **Effort Estimation**: Small/Medium/Large effort levels for each task
- **Challenge Identification**: Highlights potential blockers
- **Pro Tips**: Practical advice for goal completion
- **Conversational Refinement**: Ask follow-up questions to refine the plan

## Project Structure

```
.
├── agent.py          # Agent logic using Claude API
├── app.py            # Streamlit web interface
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd claude_code_02_agent
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create a .env file
   echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
   ```

5. **Run the Streamlit app**
   ```bash
   streamlit run app.py
   ```

## How It Works

### Agent Architecture

The agent uses Claude's extended thinking and conversational capabilities to:

1. **Parse the Goal**: Understands what the user wants to accomplish
2. **Plan**: Breaks down into logical steps with dependencies
3. **Prioritize**: Ranks tasks by importance and urgency
4. **Estimate**: Assigns effort levels and time estimates
5. **Identify Risks**: Highlights potential challenges
6. **Refine**: Responds to follow-up questions for refinement

### Example Usage

**Input:**
> "Learn Python for web development in 3 months"

**Output:**
- Structured task plan with 8-10 steps
- Priority levels (🔴 high, 🟡 medium, 🟢 low)
- Effort estimates
- Pro tips (e.g., "Join a Python community early")
- Challenges (e.g., "Time management with full-time job")

## Learning Goals

This project teaches:
- ✅ Building agents with Claude API
- ✅ Multi-turn conversations with context
- ✅ Structured outputs from LLMs
- ✅ Streamlit for rapid UI prototyping
- ✅ Error handling and edge cases

## Future Enhancements

- [ ] Task progress tracking
- [ ] Export plans to PDF/Markdown
- [ ] Integration with calendar apps
- [ ] Team collaboration features
- [ ] Historical plan comparisons
- [ ] Goal template library

## Requirements

- Python 3.10+
- Anthropic API key
- ~30MB disk space for dependencies

## License

MIT

## Author

Built as a learning project for agent development.
