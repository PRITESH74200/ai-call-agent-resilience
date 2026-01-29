import streamlit as st
import time
import json
import os
import pandas as pd
from src.app import AICallAgent

st.set_page_config(page_title="AI Agent Resilience Dashboard", layout="wide")

st.title("📞 AI Call Agent Resilience System")
st.markdown("""
This dashboard monitors the **Error Recovery & Resilience System**.
It simulates transient failures and demonstrates how the Circuit Breaker and Retry logic protect the system.
""")

# Load Config
@st.cache_data
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()

# Initialize Session State
if 'agent' not in st.session_state:
    st.session_state.agent = AICallAgent(config)
    st.session_state.agent.start()
    st.session_state.logs = []

# Sidebar Controls
st.sidebar.header("Fault Injection")
eleven_labs_down = st.sidebar.toggle("Simulate ElevenLabs 503", value=False)
st.session_state.agent.eleven_labs.is_down = eleven_labs_down

if st.sidebar.button("Process Call Queue"):
    contacts = ["Alice", "Bob", "Charlie", "David"]
    with st.spinner("Processing calls..."):
        for contact in contacts:
            try:
                st.session_state.agent.process_single_call(contact)
            except Exception as e:
                st.error(f"Error for {contact}: {e}")
            time.sleep(1)

# Dashboard Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("🛠️ Service Status")
    
    # ElevenLabs Status
    el_cb = st.session_state.agent.eleven_labs.circuit_breaker
    st.info(f"**ElevenLabs Service**")
    st.metric("Circuit State", el_cb.state.value)
    st.progress(min(el_cb.failure_count / el_cb.failure_threshold, 1.0), text=f"Failure Count: {el_cb.failure_count}")

    # LLM Status
    llm_cb = st.session_state.agent.llm.circuit_breaker
    st.info(f"**LLM Provider**")
    st.metric("Circuit State", llm_cb.state.value)
    st.progress(min(llm_cb.failure_count / llm_cb.failure_threshold, 1.0), text=f"Failure Count: {llm_cb.failure_count}")

with col2:
    st.subheader("📑 Live Logs (local/Google Sheets Mock)")
    if os.path.exists("app_logs.json"):
        with open("app_logs.json", "r") as f:
            lines = f.readlines()
            log_data = [json.loads(line) for line in lines[-10:]] # Last 10
            df = pd.DataFrame(log_data)
            if not df.empty:
                st.dataframe(df, use_container_width=True)

st.divider()
st.subheader("🔔 Alerts Dispatcher")
# Display mock alerts from the terminal would be hard, so we just show status
if el_cb.state.value == "OPEN":
    st.error("🚨 CRITICAL: ElevenLabs Circuit is OPEN. Calls are failing fast.")
elif el_cb.state.value == "HALF_OPEN":
    st.warning("⚠️ WARNING: ElevenLabs is in HALF_OPEN. Testing recovery...")
else:
    st.success("✅ ElevenLabs is HEALTHY.")
