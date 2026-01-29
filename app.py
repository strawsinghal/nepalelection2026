import streamlit as st
import datetime
import time
from google import genai
from google.genai import types

# --- 1. SETUP CLIENT ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("🚨 CRITICAL: GEMINI_API_KEY is missing in Secrets.")
        st.stop()
except Exception as e:
    st.error(f"🚨 Client Init Failed: {str(e)}")
    st.stop()

st.set_page_config(page_title="Nepal 2026 Strategy Room", layout="wide", initial_sidebar_state="expanded")

# --- 2. SMART MODEL SELECTOR (Strictly Your Requested Models) ---
@st.cache_resource
def select_best_model():
    """
    Prioritizes ONLY the high-end models you requested.
    Checks access rights to prevent 404 crashes.
    """
    # The strict list you requested
    priority_models = [
        "gemini-3-pro-preview",   # Tier 1: Deepest Reasoning
        "gemini-3-flash-preview", # Tier 2: High Speed & Intel
        "gemini-2.0-flash",       # Tier 3: Stable 2.0 Fallback
        "gemini-1.5-pro"          # Final Safety Net (just in case)
    ]
    
    try:
        # Get list of models your API Key actually has access to
        my_models = []
        for m in client.models.list():
            if "generateContent" in m.supported_actions:
                # Strip 'models/' prefix for
