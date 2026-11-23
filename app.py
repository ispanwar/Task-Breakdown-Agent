import streamlit as st
from agent import create_task_breakdown_agent, AgentAPIError, PLAN_JSON_SCHEMA_DESCRIPTION
from plan_parser import parse_plan_response, PlanParseError

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

# Apply a pending input-clear request before the text_area widget below is
# instantiated (Streamlit forbids writing to a widget's key afterwards).
if st.session_state.get("clear_user_input"):
    st.session_state.user_input = ""
    st.session_state.clear_user_input = False

# Sidebar
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    1. **Enter your goal**
    2. **Click "Generate Plan"**
    3. **Review the plan** that appears
    4. **Refine it** using the input below the plan
    5. **Keep refining** until satisfied
    """)

    if st.button("🔄 Reset Everything", use_container_width=True):
        st.session_state.agent["reset"]()
        st.session_state.plan_data = None
        st.session_state.status = None
        st.session_state.error = None
        st.session_state.clear_user_input = True
        st.rerun()

# Main input section
st.subheader("📝 Your Goal")
user_goal = st.text_area(
    "What do you want to accomplish?",
    placeholder="e.g., Learn React and build a portfolio in 3 months",
    height=80,
    key="user_input"
)

# Button controls
col1, col2 = st.columns(2)
with col1:
    generate_btn = st.button("✨ Generate Plan", use_container_width=True, type="primary")
with col2:
    clear_btn = st.button("🗑️ Clear All", use_container_width=True)

# Handle clear button
if clear_btn:
    st.session_state.plan_data = None
    st.session_state.status = None
    st.session_state.error = None
    st.session_state.clear_user_input = True
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
                    f"Break down this goal step-by-step into actionable tasks. Return ONLY valid JSON (no markdown, no extra text) with this structure: {PLAN_JSON_SCHEMA_DESCRIPTION}\n\nGoal: {user_goal}"
                )
                st.session_state.plan_data = parse_plan_response(response_text)
                st.session_state.status = "complete"

        except AgentAPIError as e:
            st.session_state.error = f"API error: {e}"
            st.session_state.status = "error"
        except PlanParseError as e:
            st.session_state.error = str(e)
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
            try:
                priority = int(step.get("priority", 3))
            except (TypeError, ValueError):
                priority = 3
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

    # Refinement section - always shown after plan is generated
    st.divider()
    st.subheader("🎯 Refine Your Plan")
    st.markdown("Don't like something? Ask for changes below:")

    refine_input = st.text_input(
        "What would you like to adjust or improve?",
        placeholder="e.g., Add more details on step 2, make it harder, add timeline, focus on first step...",
        key="refine_input_main"
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("✅ Apply Refinement", use_container_width=True, type="primary", key="submit_refine"):
            if refine_input.strip():
                try:
                    with st.spinner("🤔 Refining your plan..."):
                        response_text = st.session_state.agent["chat"](
                            f"Based on the previous plan, please refine it with this feedback. Return ONLY valid JSON with same structure: {refine_input}"
                        )
                        st.session_state.plan_data = parse_plan_response(response_text)
                        st.session_state.status = "complete"
                        st.rerun()
                except AgentAPIError as e:
                    st.error(f"❌ API error: {e}")
                except PlanParseError:
                    st.error("❌ Error parsing refined plan. Try rephrasing your request.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please type your refinement request")

elif st.session_state.plan_data is None and st.session_state.status is None:
    st.info("👈 Enter a goal above and click 'Generate Plan' to get started!")
