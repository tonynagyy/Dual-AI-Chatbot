import streamlit as st
import uuid
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Model info for display
PROVIDER = os.getenv("PROVIDER", "ollama").upper()
MODEL_NAME = os.getenv("MODEL_NAME", "mistral")

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000/api/chat")

# Page configuration
st.set_page_config(page_title="Inventory Chatbot", page_icon="📦", layout="wide")

st.title("Inventory Chatbot")
st.markdown(f"Analyze inventory using {MODEL_NAME} ({PROVIDER}). Powered by LangGraph.")

# Initialize session state for chat history and session ID
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Sidebar for metrics and info
with st.sidebar:
    st.header("Settings & Info")
    debug_mode = st.toggle("Debug Mode", value=False, help="Show raw API responses for troubleshooting.")
    
    st.info(f"**Session ID:** `{st.session_state.session_id}`")
    st.info(f"**Model:** {MODEL_NAME} ({PROVIDER})")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.markdown("---")
    st.markdown("### Follow-up Scenarios")
    st.markdown("- What is the total value of assets per site?")
    st.markdown("- Show me assets purchased this year.")
    st.markdown("- Who are our top vendors by bill amount?")
    st.markdown("- What are the quarterly billing totals?")
    st.markdown("- List all open purchase orders.")
    st.markdown("- Give me a breakdown of assets by category.")
    st.markdown("- Show customer sales orders from last month.")
    st.markdown("- Hi there!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sql"):
            with st.expander("Generated SQL Query"):
                st.code(message["sql"], language="sql")
        
        # Display debug info if available
        if debug_mode and message.get("debug"):
            with st.expander("Raw Debug Data"):
                st.json(message["debug"])

# Chat input
if prompt := st.chat_input("Ask a question about your inventory..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process with API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                payload = {
                    "session_id": st.session_state.session_id,
                    "message": prompt,
                    "context": {}
                }
                
                response = requests.post(API_URL, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    answer = data.get("natural_language_answer")
                    sql_query = data.get("sql_query")
                    latency = data.get("latency_ms", 0)
                    tokens = data.get("token_usage", {})
                    status = data.get("status")

                    if status == "error":
                        st.error(answer)
                    else:
                        st.markdown(answer)
                    
                    if sql_query:
                        with st.expander("🛠️ Generated SQL Query"):
                            st.code(sql_query, language="sql")
                    
                    # Show metrics
                    cols = st.columns(3)
                    cols[0].metric("Latency", f"{latency}ms")
                    cols[1].metric("Tokens", tokens.get("total_tokens", 0))
                    cols[2].metric("Status", status.upper())

                    # Debug data
                    debug_info = data if debug_mode else None

                    # Add assistant message to history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sql": sql_query,
                        "latency": latency,
                        "tokens": tokens,
                        "debug": debug_info
                    })
                else:
                    st.error(f"API Error (Status {response.status_code}): {response.text}")
                    st.warning("Make sure to run 'python api.py' in a separate terminal!")
                    
            except Exception as e:
                st.error(f"Failed to connect to API: {str(e)}")
                st.warning("Ensure the FastAPI server is running at http://localhost:8000")
