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
    st.session_state.last_response = None
    st.session_state.refine_mode = False

# Sidebar for instructions
with st.sidebar:
    st.header("📋 How to use")
    st.markdown("""
    1. **Enter your goal** in the text area
    2. **Click "Break it Down"** to generate a plan
    3. **Use Refine** to ask follow-up questions
    4. **Reset** to start a new goal

    Examples:
    - "Learn Python for web development"
    - "Launch a personal blog"
    - "Build a machine learning model"
    - "Prepare for a job interview"
    """)

    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.agent["reset"]()
        st.session_state.last_response = None
        st.session_state.refine_mode = False
        st.rerun()

# Main content area
st.subheader("Your Goal")
user_input = st.text_area(
    "What goal do you want to break down?",
    placeholder="e.g., Learn Python for web development in 3 months",
    height=100,
    key="user_input"
)

# Button section
col1, col2, col3 = st.columns(3)

with col1:
    submit_button = st.button("✨ Break it Down", use_container_width=True, type="primary")

with col2:
    refine_button = st.button("🎯 Refine", use_container_width=True, disabled=st.session_state.last_response is None)

with col3:
    clear_button = st.button("🗑️ Clear", use_container_width=True)

# Handle button clicks
if clear_button:
    st.session_state.last_response = None
    st.session_state.refine_mode = False
    st.session_state.user_input = ""
    st.rerun()

if submit_button and user_input:
    with st.spinner("🤔 Agent is thinking..."):
        response = st.session_state.agent["chat"](
            f"Please break down this goal into actionable steps: {user_input}"
        )
        st.session_state.last_response = response
        st.session_state.refine_mode = False

if refine_button:
    st.session_state.refine_mode = True

# Display refine input if in refine mode
if st.session_state.refine_mode:
    st.divider()
    refinement_input = st.text_input(
        "What would you like to refine or ask about?",
        placeholder="e.g., Can you add more details on step 3?"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Submit", use_container_width=True, type="primary"):
            if refinement_input:
                with st.spinner("🤔 Agent is thinking..."):
                    response = st.session_state.agent["chat"](refinement_input)
                    st.session_state.last_response = response
                    st.session_state.refine_mode = False
                    st.rerun()
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.refine_mode = False
            st.rerun()

# Display final response
if st.session_state.last_response:
    st.divider()
    st.subheader("📋 Your Plan")

    response_content = st.session_state.last_response

    # Try to parse and display structured data
    try:
        if "{" in response_content and "}" in response_content:
            json_start = response_content.find("{")
            json_end = response_content.rfind("}") + 1
            json_str = response_content[json_start:json_end]
            data = json.loads(json_str)

            # Display structured plan
            if "steps" in data:
                st.markdown("### 📝 Task Steps:")
                for i, step in enumerate(data["steps"], 1):
                    priority = "🔴" if step.get("priority", 0) >= 4 else "🟡" if step.get("priority", 0) >= 2 else "🟢"
                    effort = step.get("effort", "medium")
                    st.markdown(
                        f"{i}. {priority} **{step['title']}** ({effort})\n"
                        f"   {step['description']}"
                    )

            if "estimated_time" in data:
                st.markdown(f"### ⏱️ Estimated Time: {data['estimated_time']}")

            if "tips" in data:
                st.markdown("### 💡 Pro Tips:")
                for tip in data["tips"]:
                    st.markdown(f"• {tip}")

            if "potential_challenges" in data:
                st.markdown("### ⚠️ Potential Challenges:")
                for challenge in data["potential_challenges"]:
                    st.markdown(f"• {challenge}")
        else:
            st.write(response_content)
    except (json.JSONDecodeError, ValueError):
        st.write(response_content)
else:
    st.info("👈 Enter a goal and click 'Break it Down' to get started!")
