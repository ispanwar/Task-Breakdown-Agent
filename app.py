import streamlit as st
import json
import re
from agent import create_task_breakdown_agent

st.set_page_config(
    page_title="Task Breakdown Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Task Breakdown Agent")
st.markdown("Break down your goals into actionable steps with AI assistance")

# Initialize session state
if "agent" not in st.session_state:
    st.session_state.agent = create_task_breakdown_agent()
    st.session_state.plan_data = None
    st.session_state.status = None
    st.session_state.error = None

# Sidebar
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    1. Enter your goal
    2. Click "Generate Plan"
    3. Review the breakdown
    4. Use "Refine" for adjustments
    5. Click "Reset" to start over
    """)

    if st.button("🔄 Reset Everything", use_container_width=True):
        st.session_state.agent["reset"]()
        st.session_state.plan_data = None
        st.session_state.status = None
        st.session_state.error = None
        st.rerun()

# Main input section
st.subheader("📝 Your Goal")
user_goal = st.text_area(
    "What do you want to accomplish?",
    placeholder="e.g., Learn React and build a portfolio in 3 months",
    height=80,
    key="goal_input"
)

# Button controls
col1, col2, col3 = st.columns(3)
with col1:
    generate_btn = st.button("✨ Generate Plan", use_container_width=True, type="primary")
with col2:
    refine_btn = st.button("🎯 Refine", use_container_width=True, disabled=st.session_state.plan_data is None)
with col3:
    clear_btn = st.button("🗑️ Clear", use_container_width=True)

# Handle clear button
if clear_btn:
    st.session_state.plan_data = None
    st.session_state.status = None
    st.session_state.error = None
    st.rerun()

# Handle generate plan
if generate_btn:
    if not user_goal.strip():
        st.error("❌ Please enter a goal first!")
    else:
        st.session_state.status = "loading"
        st.session_state.error = None

        try:
            with st.spinner("🤔 AI is analyzing your goal..."):
                response_text = st.session_state.agent["chat"](
                    f"Break down this goal step-by-step into actionable tasks. Return ONLY valid JSON (no markdown, no extra text) with this structure: {{\"goal\": \"\", \"steps\": [{{\"title\": \"\", \"description\": \"\", \"priority\": 1-5, \"effort\": \"small/medium/large\"}}], \"estimated_time\": \"\", \"tips\": [], \"potential_challenges\": []}}\n\nGoal: {user_goal}"
                )

                # Clean and parse JSON
                plan_json = response_text.strip()

                # Remove markdown code blocks if present
                plan_json = re.sub(r'```json\s*', '', plan_json)
                plan_json = re.sub(r'```\s*', '', plan_json)

                # Extract JSON object
                json_match = re.search(r'\{[\s\S]*\}', plan_json)
                if json_match:
                    json_str = json_match.group(0)
                    st.session_state.plan_data = json.loads(json_str)
                    st.session_state.status = "complete"
                else:
                    st.session_state.error = "Could not extract JSON from response"
                    st.session_state.status = "error"

        except json.JSONDecodeError as e:
            st.session_state.error = f"Invalid JSON in response. Try again or rephrase your goal."
            st.session_state.status = "error"
        except Exception as e:
            st.session_state.error = f"Error: {str(e)}"
            st.session_state.status = "error"

# Display status and plan
if st.session_state.status == "loading":
    st.warning("⏳ Generating plan... Please wait")

elif st.session_state.status == "error":
    st.error(f"❌ {st.session_state.error}")

elif st.session_state.status == "complete" and st.session_state.plan_data:
    st.success("✅ Plan generated successfully!")
    st.divider()

    plan = st.session_state.plan_data

    # Display goal
    if "goal" in plan:
        st.markdown(f"**Goal:** {plan['goal']}")

    # Display estimated time
    if "estimated_time" in plan:
        st.markdown(f"**⏱️ Estimated Time:** {plan['estimated_time']}")

    st.divider()

    # Display steps
    if "steps" in plan:
        st.subheader("📋 Steps to Complete")
        for i, step in enumerate(plan["steps"], 1):
            # Priority indicator
            priority = step.get("priority", 3)
            if priority >= 4:
                priority_icon = "🔴"
            elif priority >= 2:
                priority_icon = "🟡"
            else:
                priority_icon = "🟢"

            effort = step.get("effort", "medium").upper()

            with st.container(border=True):
                st.markdown(f"### {i}. {priority_icon} {step['title']}")
                st.markdown(step['description'])
                st.markdown(f"*Effort: {effort}*")

    # Display tips
    if "tips" in plan:
        st.subheader("💡 Pro Tips")
        for tip in plan["tips"]:
            st.markdown(f"✓ {tip}")

    # Display challenges
    if "potential_challenges" in plan:
        st.subheader("⚠️ Potential Challenges")
        for challenge in plan["potential_challenges"]:
            st.markdown(f"• {challenge}")

    # Refine section
    st.divider()
    if refine_btn:
        st.subheader("🎯 Refine Your Plan")

        refine_input = st.text_input(
            "What would you like to adjust or ask?",
            placeholder="e.g., Add more details on step 2, make it harder, add timeline...",
            key="refine_input"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Submit Refinement", use_container_width=True, type="primary"):
                if refine_input.strip():
                    try:
                        with st.spinner("🤔 Refining your plan..."):
                            response_text = st.session_state.agent["chat"](
                                f"Based on the previous plan, please refine it with this feedback. Return ONLY valid JSON with same structure: {refine_input}"
                            )

                            # Clean and parse JSON
                            plan_json = response_text.strip()
                            plan_json = re.sub(r'```json\s*', '', plan_json)
                            plan_json = re.sub(r'```\s*', '', plan_json)

                            json_match = re.search(r'\{[\s\S]*\}', plan_json)
                            if json_match:
                                json_str = json_match.group(0)
                                st.session_state.plan_data = json.loads(json_str)
                                st.session_state.status = "complete"
                                st.rerun()
                            else:
                                st.error("❌ Could not parse refined plan. Try again.")
                    except json.JSONDecodeError:
                        st.error("❌ Error parsing refined plan. Try rephrasing your request.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter your refinement request")

        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.rerun()

elif st.session_state.plan_data is None and st.session_state.status is None:
    st.info("👈 Enter a goal and click 'Generate Plan' to get started!")
