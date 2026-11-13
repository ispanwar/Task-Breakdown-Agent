import streamlit as st
import json
from agent import create_task_breakdown_agent

st.set_page_config(
    page_title="Task Breakdown Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Task Breakdown Agent")
st.markdown("""
This agent helps you break down complex goals into actionable steps,
prioritize them, and identify potential challenges.
""")

# Initialize agent in session state
if "agent" not in st.session_state:
    st.session_state.agent = create_task_breakdown_agent()

# Sidebar for instructions
with st.sidebar:
    st.header("📋 How to use")
    st.markdown("""
    1. **Enter your goal** in the text area
    2. **Click "Break it Down"** to generate a plan
    3. **Ask follow-up questions** to refine the plan
    4. **Reset** to start a new goal

    Examples:
    - "Learn Python for web development"
    - "Launch a personal blog"
    - "Build a machine learning model"
    - "Prepare for a job interview"
    """)

    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.agent["reset"]()
        st.session_state.messages = []
        st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Your Goal")
    user_input = st.text_area(
        "What goal do you want to break down?",
        placeholder="e.g., Learn Python for web development in 3 months",
        height=100,
        key="user_input"
    )

with col2:
    st.subheader("Conversation")
    message_count = len(st.session_state.agent["get_history"]())
    st.metric("Messages", message_count // 2)

# Initialize messages in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create two columns for buttons
col1, col2, col3 = st.columns(3)

with col1:
    submit_button = st.button("✨ Break it Down", use_container_width=True, type="primary")

with col2:
    refine_button = st.button("🎯 Refine", use_container_width=True)

with col3:
    clear_button = st.button("🗑️ Clear History", use_container_width=True)

# Handle button clicks
if clear_button:
    st.session_state.messages = []
    st.rerun()

if submit_button and user_input:
    with st.spinner("🤔 Agent is thinking..."):
        response = st.session_state.agent["chat"](
            f"Please break down this goal into actionable steps: {user_input}"
        )
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

if refine_button and st.session_state.messages:
    refinement_prompt = st.text_input("What would you like to refine or ask about?")
    if refinement_prompt:
        with st.spinner("🤔 Agent is thinking..."):
            response = st.session_state.agent["chat"](refinement_prompt)
            st.session_state.messages.append({
                "role": "user",
                "content": refinement_prompt
            })
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

# Display conversation
st.divider()
st.subheader("💬 Conversation")

if st.session_state.messages:
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

                # Try to parse and display JSON structure nicely
                try:
                    # Extract JSON from the response if it exists
                    content = message["content"]
                    if "{" in content and "}" in content:
                        json_start = content.find("{")
                        json_end = content.rfind("}") + 1
                        json_str = content[json_start:json_end]
                        data = json.loads(json_str)

                        # Display structured plan
                        if "steps" in data:
                            st.markdown("### 📝 Task Plan:")
                            for step in data["steps"]:
                                priority = "🔴" if step.get("priority", 0) >= 4 else "🟡" if step.get("priority", 0) >= 2 else "🟢"
                                effort = step.get("effort", "medium")
                                st.markdown(
                                    f"{priority} **{step['title']}** ({effort} effort)\n"
                                    f"   {step['description']}"
                                )

                        if "tips" in data:
                            st.markdown("### 💡 Pro Tips:")
                            for tip in data["tips"]:
                                st.markdown(f"• {tip}")

                        if "potential_challenges" in data:
                            st.markdown("### ⚠️ Potential Challenges:")
                            for challenge in data["potential_challenges"]:
                                st.markdown(f"• {challenge}")
                except (json.JSONDecodeError, ValueError):
                    pass
else:
    st.info("👈 Enter a goal and click 'Break it Down' to get started!")
