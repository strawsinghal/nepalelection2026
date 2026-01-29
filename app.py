import streamlit as st
import datetime
import time
from google import genai
from google.genai import types

# 1. Setup Models
DEEP_MODEL = "gemini-3-pro-preview" 
FAST_MODEL = "gemini-3-flash-preview"

# Initialize Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Nepal 2026 Intel", layout="wide")

# --- SESSION STATE INITIALIZATION (Crucial for UI Stability) ---
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "report_type" not in st.session_state:
    st.session_state.report_type = None

# --- CACHING LOGIC ---

@st.cache_data(ttl="1h", show_spinner=False)
def get_fast_intel(constituency_name):
    prompt = f"""
    Provide a structured 3-bullet summary for {constituency_name} (Nepal 2026 Election).
    Format:
    * **Winner Projection:** [Name/Party]
    * **Key Rival:** [Name/Party]
    * **X-Factor:** [Gen Z/Rebel/Alliance]
    """
    response = client.models.generate_content(
        model=FAST_MODEL,
        contents=prompt
    )
    return response.text

@st.cache_data(ttl="1d", show_spinner=False)
def get_daily_deep_intel(constituency_name):
    """
    Runs DEEP research using Gemini 3 Pro. Cached for 24 hours.
    """
    prompt = f"""
    Perform a professional political deep dive for {constituency_name}, Nepal (March 5, 2026 Election).
    1. Identify major candidates using Jan 20, 2026 nomination data.
    2. Analyze the 'Gen Z' and 'Balen-Rabi Alliance' impact.
    3. Predict the winner probability based on ground sentiment.
    """
    response = client.models.generate_content(
        model=DEEP_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    return {
        "text": response.text,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

# --- UI HEADER ---
ticker_html = """
<div style="background-color: #1E1E1E; color: #00FF94; padding: 8px; border-radius: 5px; margin-bottom: 15px; font-family: monospace;">
    <marquee>🚨 LIVE: 150,000 police deployed • 🗳️ 3,406 Candidates Finalized • ❄️ Logistics: Snow Alerts in Karnali • 🥊 Jhapa-5: Balen vs Oli Heat Map High</marquee>
</div>
"""
st.markdown(ticker_html, unsafe_allow_html=True)
st.title("🇳🇵 Nepal Election 2026: War Room")

# --- DATA DICTIONARY ---
constituency_data = {
    "Koshi (28)": ["Jhapa 5", "Jhapa 3", "Morang 6", "Sunsari 1", "Ilam 2"],
    "Madhesh (32)": ["Sarlahi 4", "Rautahat 1", "Dhanusha 3", "Saptari 2"],
    "Bagmati (33)": ["Kathmandu 4", "Chitwan 2", "Chitwan 3", "Lalitpur 3"],
    "Gandaki (18)": ["Gorkha 2", "Kaski 2", "Tanahun 1"],
    "Lumbini (26)": ["Rupandehi 2", "Dang 2", "Banke 2"],
    "Karnali (12)": ["Surkhet 2", "Jumla 1"],
    "Sudurpashchim (16)": ["Kailali 5", "Dadeldhura 1"]
}

col_nav, col_main = st.columns([1, 3], gap="medium")

with col_nav:
    st.subheader("📍 Select Zone")
    prov = st.selectbox("Province", list(constituency_data.keys()))
    seat = st.selectbox("Constituency", constituency_data[prov])
    
    st.markdown("---")
    
    # IMPROVED BATCH UPDATE (Uses Progress Bar & Toast)
    if st.button("🔄 Sync Daily Cache"):
        seats = constituency_data[prov]
        bar = st.progress(0)
        st.toast(f"Starting sync for {len(seats)} seats in {prov}...")
        
        for i, s in enumerate(seats):
            # Calls the cache function silently
            get_daily_deep_intel(s)
            bar.progress((i + 1) / len(seats))
            time.sleep(0.1) # UI breathing room
            
        st.toast("✅ Daily Intelligence Sync Complete!", icon="🎉")
        time.sleep(1)
        st.rerun()

with col_main:
    # ACTION BUTTON
    if st.button(f"🚀 Analyze {seat}", type="primary", use_container_width=True):
        
        # 1. FAST PHASE
        with st.status("📡 Establishing Satellite Link...", expanded=True) as status:
            st.write("Fetching instant flash intelligence...")
            fast_data = get_fast_intel(seat)
            st.session_state.current_report = {"fast": fast_data, "deep": None}
            st.session_state.report_type = "fast"
            status.update(label="⚡ Flash Data Received!", state="complete", expanded=False)
            
        # 2. DEEP PHASE (Background Check)
        # We check if deep data is cached. If not, we run it.
        # This keeps the user on the "Fast" tab until they want Deep.
        deep_data = get_daily_deep_intel(seat)
        st.session_state.current_report["deep"] = deep_data
        st.session_state.report_type = "deep"
        st.toast(f"🧠 Deep Research for {seat} is ready!", icon="✅")


    # DISPLAY LOGIC (Using Tabs for Friendly UI)
    if st.session_state.current_report:
        
        st.divider()
        st.subheader(f"📊 Intelligence Report: {seat}")
        
        # TABS: The Friendly Way to handle "Fast vs Deep"
        tab_fast, tab_deep = st.tabs(["⚡ Fast Pulse", "🧠 Deep Strategy"])
        
        with tab_fast:
            if st.session_state.current_report["fast"]:
                st.info("Instant Snapshot (Gemini 3 Flash)")
                st.markdown(st.session_state.current_report["fast"])
            
        with tab_deep:
            deep_content = st.session_state.current_report["deep"]
            if deep_content:
                st.success(f"Verified Deep Research (Gemini 3 Pro) • {deep_content['timestamp']}")
                st.markdown(deep_content["text"])
            else:
                st.warning("Deep research is compiling... check back in 10 seconds.")
                
    else:
        # EMPTY STATE
        st.info("👈 Select a constituency and click 'Analyze' to begin.")
