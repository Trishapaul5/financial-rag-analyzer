"""
Streamlit Frontend for the ENHANCED Financial RAG Analyzer
"""
import streamlit as st
import requests
import uuid

# --- Page Configuration ---
st.set_page_config(
    page_title="Financial News RAG Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Backend API Configuration ---
BACKEND_HOST = "http://backend:8000"
QUERY_URL = f"{BACKEND_HOST}/api/v1/query/stream"
STATS_URL = f"{BACKEND_HOST}/api/v1/db/stats"

# --- Session State Initialization ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "db_stats" not in st.session_state:
    st.session_state.db_stats = {"total_documents": 0, "sources": []}

# --- Sidebar ---
with st.sidebar:
    st.header("📈 FinRAG Analyzer")
    st.subheader("Database Status")
    
    try:
        stats_response = requests.get(STATS_URL)
        if stats_response.status_code == 200:
            st.session_state.db_stats = stats_response.json()
        else:
            st.error("Could not fetch DB stats.")
    except requests.exceptions.ConnectionError:
        st.error("Backend connection failed.")

    st.metric(label="Total Documents Indexed", value=st.session_state.db_stats['total_documents'])
    st.info(f"Sources: {', '.join(st.session_state.db_stats['sources'])}")

    st.divider()
    st.subheader("Query Filters")
    
    selected_sources = st.multiselect(
        "Filter by News Source:",
        options=st.session_state.db_stats['sources'],
        default=st.session_state.db_stats['sources']
    )

# --- Main Page ---
st.header("Chat with Financial News")
st.markdown("Powered by a FastAPI backend, ChromaDB, LangChain, and Ollama.")

# --- Example Questions ---
st.markdown("##### Try an example:")
example_questions = [
    "What are the main investment themes suggested by Motilal Oswal?",
    "Summarize the outlook on the Indian IT services sector.",
    "What is the price band for the Mamaearth IPO?",
]

def ask_example(question):
    st.session_state.run_example = True
    st.session_state.example_question = question

for q in example_questions:
    st.button(q, on_click=ask_example, args=(q,))

# --- Chat History Display ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Main Chat Interaction Logic ---
def run_query(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            payload = {
                "query": prompt,
                "session_id": st.session_state.session_id,
                "sources": selected_sources
            }
            response_container = st.empty()
            full_response = ""
            with requests.post(QUERY_URL, json=payload, stream=True) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                    full_response += chunk
                    response_container.markdown(full_response + "▌")
            
            response_container.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except requests.exceptions.RequestException as e:
            st.error(f"Connection to backend failed: {e}")
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})

# Handle user input from chat box
if prompt := st.chat_input("Ask a question..."):
    run_query(prompt)

# Handle user input from example buttons
if st.session_state.get("run_example"):
    question = st.session_state.example_question
    st.session_state.run_example = False
    run_query(question)
    st.rerun()
