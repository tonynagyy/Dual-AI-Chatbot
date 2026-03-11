import time
import uuid
import streamlit as st

# We must set page_config as the first Streamlit command
st.set_page_config(page_title="Football Knowledge Graph", page_icon="⚽", layout="wide")

import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("neo4j").setLevel(logging.WARNING)
logging.getLogger("config").setLevel(logging.WARNING)
logging.getLogger("agent.executor").setLevel(logging.WARNING)
logging.getLogger("agent.classifier").setLevel(logging.WARNING)
logging.getLogger("agent.cypher_generator").setLevel(logging.WARNING)
logging.getLogger("agent.response_engine").setLevel(logging.WARNING)

from agent.classifier import IntentClassifier
from agent.cypher_generator import CypherGenerator
from agent.executor import Neo4jExecutor
from agent.response_engine import ResponseEngine
from config import LLM_PROVIDER, LLM_MODEL

# Map intents to human-readable action labels
INTENT_ACTION_MAP = {
    "add": "Added",
    "update": "Updated",
    "delete": "Deleted",
    "inquire": "Queried",
}

# -------------------------------------------------------------------
# Initialization
# -------------------------------------------------------------------

@st.cache_resource
def get_chatbot_components():
    """
    Initialize and cache the model wrappers and Neo4j connection 
    so they aren't re-created on every Streamlit re-run.
    """
    classifier = IntentClassifier()
    generator = CypherGenerator()
    executor = Neo4jExecutor()
    responder = ResponseEngine()
    return classifier, generator, executor, responder

try:
    classifier, generator, executor, responder = get_chatbot_components()
except Exception as e:
    st.error(f"Failed to initialize chatbot components. Error: {e}")
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# -------------------------------------------------------------------
# UI Layout
# -------------------------------------------------------------------

st.title("⚽ Champions League Graph Bot")
st.markdown(f"Interact with the football knowledge graph using {LLM_MODEL.upper()} ({LLM_PROVIDER.upper()}).")

# Sidebar
with st.sidebar:
    st.header("Settings & Info")
    debug_mode = st.toggle("Debug Mode", value=False, help="Show raw queries and intents for troubleshooting.")
    
    st.info(f"**Session ID:** `{st.session_state.session_id}`")
    st.info(f"**Provider:** {LLM_PROVIDER.upper()}")
    st.info(f"**Model:** {LLM_MODEL}")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.markdown("---")
    st.markdown("### Example Prompts")
    st.markdown("**Inquire:**")
    st.markdown("- Who does Lionel Messi play for?")
    st.markdown("- Who is the manager of Manchester City?")
    st.markdown("**Add:**")
    st.markdown("- Add the fact that Cody Gakpo plays for Liverpool.")
    st.markdown("**Update:**")
    st.markdown("- Update the fact that Kylian Mbappé plays for Real Madrid to Paris Saint-Germain.")
    st.markdown("**Delete:**")
    st.markdown("- Remove the fact that Kevin De Bruyne plays for Manchester City.")
    st.markdown("**Chitchat:**")
    st.markdown("- Hello! How are you doing?")

# -------------------------------------------------------------------
# Chat History
# -------------------------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display debug info if available
        if message.get("debug") and debug_mode:
            debug_info = message["debug"]
            with st.expander("🛠️ Raw Debug Data"):
                st.write(f"**Intent:** {debug_info.get('intent')}")
                st.write(f"**Latency:** {debug_info.get('latency', 0):.2f} ms")
                
                if debug_info.get("cypher"):
                    st.code(debug_info["cypher"], language="cypher")
                if debug_info.get("raw_results") is not None:
                    st.json(debug_info["raw_results"])

# -------------------------------------------------------------------
# Chat Input
# -------------------------------------------------------------------

if prompt := st.chat_input("Ask about Champions League football..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process with the agent
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            start_time = time.time()
            debug_data = {}
            response_text = ""
            
            try:
                # 1. Classify Intent
                intent = classifier.classify(prompt)
                debug_data["intent"] = intent
                
                if intent == "chitchat":
                    # 2. Handle Chitchat without DB
                    response_text = responder.generate_chitchat(prompt)
                else:
                    # 3. Generate Cypher query
                    cypher_query = generator.generate(prompt, intent)
                    debug_data["cypher"] = cypher_query
                    
                    # 4. Execute against Neo4j
                    raw_results = executor.execute_query(cypher_query)
                    debug_data["raw_results"] = raw_results
                    
                    # 5. Convert to natural language
                    action_msg = INTENT_ACTION_MAP.get(intent, "Processed")
                    response_text = responder.generate_response(prompt, raw_results, action_msg, intent)
                    
            except ValueError as e:
                response_text = f"I couldn't generate a valid query for that request. Please try rephrasing.\n\n*Detail: {e}*"
                debug_data["error"] = str(e)
            except Exception as e:
                response_text = f"I'm sorry, I encountered an error: {e}"
                debug_data["error"] = str(e)

            latency = (time.time() - start_time) * 1000
            debug_data["latency"] = latency
            
            # Display response
            st.markdown(response_text)
            
            # Optional Debug Output in current turn
            if debug_mode and debug_data:
                with st.expander("🛠️ Raw Debug Data"):
                    st.write(f"**Intent:** {debug_data.get('intent')}")
                    st.write(f"**Latency:** {debug_data.get('latency', 0):.2f} ms")
                    if debug_data.get("cypher"):
                        st.code(debug_data["cypher"], language="cypher")
                    if debug_data.get("raw_results") is not None:
                        st.json(debug_data["raw_results"])

            # Save the message and state
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "debug": debug_data
            })
