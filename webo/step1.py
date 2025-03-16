import json
import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
import time
from PIL import Image
import io
import base64
import tempfile

# LangChain LLM imports
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# browser-use imports
from browser_use import Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Browser Automation Assistant",
    page_icon="🌐",
    layout="wide",
)

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = ""
if "plan" not in st.session_state:
    st.session_state.plan = None
if "task" not in st.session_state:
    st.session_state.task = ""
if "execution_state" not in st.session_state:
    st.session_state.execution_state = (
        "idle"  # Can be 'idle', 'planning', 'executing', 'error', 'complete'
    )
if "screenshots" not in st.session_state:
    st.session_state.screenshots = []
if "error_message" not in st.session_state:
    st.session_state.error_message = None
if "error_analysis" not in st.session_state:
    st.session_state.error_analysis = None


# Helper functions
def clean_response(text: str) -> str:
    """Remove markdown code fences (e.g., ```json) so that JSON can be parsed."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return text


def get_llm():
    """Initialize the LLM based on selected model"""
    if st.session_state.model_choice == "Gemini":
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.3)


# System prompts
system_prompt = SystemMessage(
    content="""
You are an assistant that refines user task instructions for browser automation.
When given a user's task along with additional context or modifications, determine whether there is enough 
information to generate a detailed, step-by-step plan.
Important:
- Do not ask for the current date or year; assume they are known.
- If the user provides modifications, update the plan accordingly.
Respond in valid JSON:
If complete, respond with:
  { "complete": true, "plan": "Detailed step-by-step plan..." }
If more info is needed, respond with:
  { "complete": false, "missing": ["Missing detail 1", "Missing detail 2"] }
Respond in valid JSON only.
"""
)

error_analysis_prompt = SystemMessage(
    content="""
You are an assistant that analyzes error messages from a browser automation agent.
Given an error message, provide a brief description of the problem and ask a clarifying question 
that will help resolve the issue.
Respond in valid JSON format with two keys:
{
  "problem": "A brief description of the error in one sentence.",
  "question": "A clarifying question asking what additional detail is needed."
}
Respond in valid JSON only.
"""
)


# LLM interaction functions
def query_agent(task: str, history: str) -> dict:
    with st.spinner("Analyzing your task..."):
        llm = get_llm()
        prompt_text = history + "\nUser Task: " + task
        messages = [system_prompt, HumanMessage(content=prompt_text)]
        response = llm.invoke(messages)
        cleaned = clean_response(response.content)
        try:
            return json.loads(cleaned)
        except Exception as e:
            st.error(f"Error parsing agent response: {e}")
            st.code(cleaned, language="json")
            return None


def analyze_error(error_msg: str) -> dict:
    with st.spinner("Analyzing error..."):
        llm = get_llm()
        messages = [error_analysis_prompt, HumanMessage(content="Error: " + error_msg)]
        response = llm.invoke(messages)
        cleaned = clean_response(response.content)
        try:
            return json.loads(cleaned)
        except Exception as e:
            st.error(f"Error parsing error analysis: {e}")
            return {
                "problem": "Unknown error",
                "question": "What additional information do you want to provide?",
            }


# Custom screenshot callback for Browser-use
class ScreenshotController(Controller):
    def __init__(self):
        super().__init__()

    def on_screenshot(self, screenshot_data):
        """Save screenshot to session state when browser takes screenshot"""
        try:
            # Add screenshot to session state for display
            st.session_state.screenshots.append(screenshot_data)
            # Force a rerun to update the UI
            st.rerun()
        except Exception as e:
            st.error(f"Error saving screenshot: {e}")


# Planning and execution functions
async def generate_plan():
    st.session_state.execution_state = "planning"
    result = query_agent(st.session_state.task, st.session_state.conversation_history)

    if result and result.get("complete"):
        st.session_state.plan = result.get("plan")
        st.session_state.execution_state = "plan_ready"
    else:
        missing = result.get("missing", []) if result else []
        if missing:
            st.session_state.missing_details = missing
        else:
            st.session_state.missing_details = ["The task needs more details."]
        st.session_state.execution_state = "need_details"


async def execute_plan():
    st.session_state.execution_state = "executing"
    st.session_state.screenshots = []

    # Clear any previous error state
    st.session_state.error_message = None
    st.session_state.error_analysis = None

    controller = ScreenshotController()

    # Create browser config
    browser_config = BrowserConfig(
        headless=False,  # Set to True for production
    )
    browser = Browser(config=browser_config)

    llm = get_llm()

    # Create the browser-use agent with the accepted plan
    browser_agent = Agent(
        task=st.session_state.plan,
        llm=llm,
        controller=controller,
        browser=browser,
    )

    try:
        # Run the agent
        await browser_agent.run(max_steps=100)

        # Try to create history GIF if available
        try:
            gif_path = tempfile.mktemp(suffix=".gif")
            browser_agent.create_history_gif(output_path=gif_path)
            st.session_state.history_gif = gif_path
        except Exception as e:
            st.session_state.history_gif = None

        st.session_state.execution_state = "complete"
    except Exception as e:
        error_str = str(e)
        st.session_state.error_message = error_str
        st.session_state.error_analysis = analyze_error(error_str)
        st.session_state.execution_state = "error"


def handle_additional_details(details):
    st.session_state.conversation_history += "Additional: " + details + "\n"
    asyncio.run(generate_plan())


def handle_plan_modification(modification):
    st.session_state.conversation_history += "Modification: " + modification + "\n"
    asyncio.run(generate_plan())


def handle_error_feedback(feedback):
    controller = ScreenshotController()
    controller.update_context("error_feedback", feedback)
    asyncio.run(execute_plan())


def reset_state():
    st.session_state.conversation_history = ""
    st.session_state.plan = None
    st.session_state.task = ""
    st.session_state.execution_state = "idle"
    st.session_state.screenshots = []
    st.session_state.error_message = None
    st.session_state.error_analysis = None


# UI Components
def render_sidebar():
    with st.sidebar:
        st.title("Configuration")

        # Model selection
        if "model_choice" not in st.session_state:
            st.session_state.model_choice = "Gemini"

        model_choice = st.radio(
            "Choose LLM Model:",
            ["Gemini", "OpenAI"],
            index=0 if st.session_state.model_choice == "Gemini" else 1,
        )
        st.session_state.model_choice = model_choice

        # Reset button
        if st.button("Reset Session", type="primary"):
            reset_state()
            st.rerun()

        # About section
        st.divider()
        st.markdown("### About")
        st.markdown("""
        This app uses Browser-use to automate web tasks with LLM guidance.
        
        1. Enter a task description
        2. Refine the plan as needed
        3. Execute and watch the AI navigate
        """)


def render_task_input():
    st.title("Browser Automation Assistant 🌐")

    with st.container():
        task = st.text_area(
            "What task would you like the browser to perform?",
            value=st.session_state.task,
            height=100,
            placeholder="Example: Go to weather.com and check the 5-day forecast for San Francisco",
        )

        if task != st.session_state.task:
            st.session_state.task = task

        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Submit", type="primary", disabled=not task):
                st.session_state.conversation_history = "User: " + task + "\n"
                asyncio.run(generate_plan())


def render_planning_interface():
    if st.session_state.execution_state == "planning":
        st.info("Analyzing your task and generating a plan...")

    elif st.session_state.execution_state == "need_details":
        st.warning("The task needs more information:")
        for detail in st.session_state.missing_details:
            st.markdown(f"- {detail}")

        additional_details = st.text_area(
            "Please provide additional details:", height=100
        )

        if st.button("Submit Details", type="primary"):
            handle_additional_details(additional_details)

    elif st.session_state.execution_state == "plan_ready":
        st.success("Plan generated successfully!")

        with st.expander("Review the step-by-step plan", expanded=True):
            st.markdown(st.session_state.plan)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Execute Plan", type="primary"):
                asyncio.run(execute_plan())

        with col2:
            modification = st.text_area(
                "Suggest modifications to the plan (optional):", height=100
            )
            if st.button("Submit Modifications"):
                handle_plan_modification(modification)


def render_execution_interface():
    if st.session_state.execution_state == "executing":
        st.info("Executing the plan... Please wait.")

        # Show loading spinner
        with st.spinner("Browser automation in progress..."):
            # This is just for visual effect in the UI since the actual execution happens in the background
            time.sleep(0.1)

    elif st.session_state.execution_state == "error":
        st.error(f"Error encountered: {st.session_state.error_message}")

        if st.session_state.error_analysis:
            st.warning(
                f"Problem: {st.session_state.error_analysis.get('problem', 'Unknown error')}"
            )

            feedback = st.text_area(
                st.session_state.error_analysis.get(
                    "question", "Please provide additional information:"
                ),
                height=100,
            )

            if st.button("Resume Execution", type="primary"):
                handle_error_feedback(feedback)

    elif st.session_state.execution_state == "complete":
        st.success("Task completed successfully!")

        if st.button("Start New Task", type="primary"):
            reset_state()
            st.rerun()


def render_screenshot_gallery():
    if st.session_state.screenshots:
        st.subheader("Browser Screenshots")

        # Create columns for the gallery
        cols = st.columns(3)

        # Display screenshots in columns
        for i, screenshot_data in enumerate(st.session_state.screenshots):
            with cols[i % 3]:
                try:
                    # Convert base64 to image
                    if isinstance(screenshot_data, str) and screenshot_data.startswith(
                        "data:image"
                    ):
                        # Extract base64 part
                        img_data = screenshot_data.split(",")[1]
                        img = Image.open(io.BytesIO(base64.b64decode(img_data)))
                        st.image(img, caption=f"Step {i + 1}", use_column_width=True)
                    elif isinstance(screenshot_data, bytes):
                        img = Image.open(io.BytesIO(screenshot_data))
                        st.image(img, caption=f"Step {i + 1}", use_column_width=True)
                    else:
                        st.warning(f"Screenshot {i + 1}: Invalid format")
                except Exception as e:
                    st.error(f"Error displaying screenshot {i + 1}: {e}")

        # Display history GIF if available
        if "history_gif" in st.session_state and st.session_state.history_gif:
            st.subheader("Execution Summary")
            try:
                with open(st.session_state.history_gif, "rb") as f:
                    st.image(f.read(), caption="Execution History")
            except Exception as e:
                st.error(f"Error displaying history GIF: {e}")


# Main app
def main():
    render_sidebar()
    render_task_input()

    # Show appropriate interface based on current state
    if st.session_state.execution_state in ["planning", "need_details", "plan_ready"]:
        render_planning_interface()
    elif st.session_state.execution_state in ["executing", "error", "complete"]:
        render_execution_interface()

    # Always show screenshots if available
    render_screenshot_gallery()


if __name__ == "__main__":
    main()
