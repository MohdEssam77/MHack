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

# LangChain imports
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Browser automation
from browser_use import Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig

# Load environment
load_dotenv()

# Configure page
st.set_page_config(
    page_title="AI Web Operator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for OpenAI-like theme
st.markdown("""
<style>
    .stApp {
        background-color: #343541;
        color: #ececf1;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #40414f !important;
        color: #ececf1 !important;
        border-radius: 5px;
        padding: 1rem;
    }
    .stButton button {
        background-color: #10a37f !important;
        color: white !important;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .plan-box {
        background-color: #40414f;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = ""
if "plan" not in st.session_state:
    st.session_state.plan = None
if "execution_state" not in st.session_state:
    st.session_state.execution_state = "ready"

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.3)

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

def clean_response(text: str) -> str:
    return text.strip().removeprefix("```json").removesuffix("```")

async def interactive_plan_refinement():
    col1, col2 = st.columns([3,1])
    with col1:
        st.header("AI Web Operator")
        user_input = st.text_area("Enter your task instruction:", height=150)

        if st.button("Generate Plan"):
            st.session_state.conversation_history = f"User: {user_input}"
            st.session_state.execution_state = "planning"

    if st.session_state.execution_state == "planning":
        with st.spinner("Analyzing your task..."):
            messages = [system_prompt, HumanMessage(content=st.session_state.conversation_history)]
            response = llm.invoke(messages)
            cleaned = clean_response(response.content)
            
            try:
                result = json.loads(cleaned)
                if result.get("complete"):
                    st.session_state.plan = result["plan"]
                    st.session_state.execution_state = "plan_ready"
                else:
                    missing = result.get("missing", [])
                    st.session_state.missing_details = missing if missing else ["The task needs more details."]
                    st.session_state.execution_state = "needs_details"
            except Exception as e:
                st.error(f"Error parsing response: {e}")
                st.session_state.execution_state = "error"

    if st.session_state.execution_state == "needs_details":
        st.warning("The task needs more information:")
        for detail in st.session_state.missing_details:
            st.markdown(f"- {detail}")
            
        with st.form("additional_details"):
            details = st.text_area("Please provide additional details:", height=100)
            if st.form_submit_button("Submit Details", type="primary"):
                st.session_state.conversation_history += f"\nAdditional: {details}"
                st.session_state.execution_state = "planning"
                st.rerun()

    if st.session_state.plan and st.session_state.execution_state == "plan_ready":
        st.markdown("""
        <div class="plan-box">
            <h3>Execution Plan</h3>
            <pre>{plan}</pre>
        </div>
        """.format(plan=st.session_state.plan), unsafe_allow_html=True)

        if st.button("Confirm and Run"):
            st.session_state.execution_state = "executing"
            await execute_plan(st.session_state.plan)

async def execute_plan(plan: str):
    controller = Controller()
    browser_agent = Agent(
        task=plan,
        llm=llm,
        controller=controller,
    )

    try:
        await browser_agent.run(max_steps=100)
        st.success("✅ Task completed successfully!")
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        st.session_state.execution_state = "error"

if __name__ == "__main__":
    asyncio.run(interactive_plan_refinement())