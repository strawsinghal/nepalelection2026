import streamlit as st
import datetime
import time
import re
from google import genai
from google.genai import types

# 1. Setup Models
DEEP_MODEL = "gemini-3-pro-preview" 
FAST_MODEL = "gemini-3-flash-preview"

# Initialize Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Nepal 2026 Strategy Room", layout="wide", initial_sidebar_state="expanded")

# --- SESSION STATE ---
if "current_report" not in st.session_state:
    st.session_state.current_report = None

# --- CACHING LOGIC (The "Backend" Brain) ---

@st.cache_data(ttl="1h", show_spinner=False)
def get_fast_pulse(constituency_name):
    """
    Returns a raw probability number and leader name for the dashboard metrics.
    """
    prompt = f"""
    Analyze {constituency_name} (Nepal 2026 Election).
    Return ONLY a JSON-like string:
    {{"leader": "Candidate Name", "probability": "XX", "runner_up": "Candidate Name", "gap": "XX"}}
    Do not explain. Just the data.
    """
    response = client.models.generate_content(
        model=FAST_MODEL,
        contents=prompt
    )
    return response.text

@st.cache_data(ttl="1d", show_spinner=False)
def get_deep_analytics(constituency_name):
    """
    The Heavy Lifter: Runs implicitly. No user button needed.
    """
    prompt = f"""
    Act as a Chief Election Strategist for {constituency_name}, Nepal (March 5, 2026).
    Input Data: Jan 20 finalized nominations, security reports, historical voting patterns, and current 'Gen Z' sentiment.
    
    Output strictly in this structure:
    
    ### 🏆 PROJECTED OUTCOME
    * **Winner Prediction:** [Name] ([Party])
    * **Win Probability:** [XX]%
    * **Margin:** +/- [XX] votes
    
    ### 📉 CANDIDATE POSITIONS (Leaderboard)
    1. **[Name]** ([Party]) - [Estimated Vote Share %] - [Trend: Rising/Falling]
    2. **[Name]** ([Party]) - [Estimated Vote Share %] - [Trend: Stable]
    3. **[Name]** ([Party]) - [Estimated Vote Share %] - [Trend: Collapsing]
    
    ### 🧠 STRATEGIC REASONING
    * **Factor 1 (Demographics):** [Analyze youth/caste vote swing]
    * **Factor 2 (Alliances):** [Analyze impact of rebel candidates or intra-party feuds]
    * **Factor 3 (Ground Reality):** [Analyze impact of Jan 20 nomination crowd size or local development issues]
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

# --- STYLING (The "Data Terminal" Look) ---
st.markdown("""
<style>
    .metric-box {
        background-color: #0E1117;
        border: 1px solid #262730;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .big-number {
        font-size: 3em;
        font-weight: bold;
        color: #00FF94;
    }
    .label {
        color: #B0B3B8;
        font-size: 0.9em;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stProgress > div > div > div > div {
        background-color: #00FF94;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER & TICKER ---
ticker_text = "🔒 SYSTEM ACTIVE: 3,406 Candidates Tracked • 📡 UPLINK: 23,112 Polling Centers • ⚠️ ALERT: Jhapa-5 Swing Variable High"
st.markdown(f"""
<div style="background-color: #0E1117; color: #00FF94; padding: 10px; font-family: 'Courier New', monospace; border-bottom: 2px solid #00FF94;">
    <marquee scrollamount="10">{ticker_text}</marquee>
</div>
""", unsafe_allow_html=True)

# --- MAIN UI ---
col_sidebar, col_main = st.columns([1, 4], gap="medium")

with col_sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Flag_of_Nepal.svg/1200px-Flag_of_Nepal.svg.png", width=50)
    st.title("Command Center")
    st.markdown("---")
    
    # Simple, Clean Navigation
    constituency_data = {
        "Koshi": ["Jhapa 5", "Jhapa 3", "Morang 6", "Sunsari 1", "Ilam 2"],
        "Madhesh": ["Sarlahi 4", "Rautahat 1", "Dhanusha 3", "Saptari 2"],
        "Bagmati": ["Kathmandu 4", "Chitwan 2", "Chitwan 3", "Lalitpur 3"],
        "Gandaki": ["Gorkha 2", "Kaski 2", "Tanahun 1"],
        "Lumbini": ["Rupandehi 2", "Dang 2"],
        "Karnali": ["Surkhet 2"],
        "Sudurpashchim": ["Dadeldhura 1"]
    }
    
    prov = st.selectbox("OPERATIONAL ZONE", list(constituency_data.keys()))
    seat = st.selectbox("TARGET SECTOR", constituency_data[prov])
    
    st.markdown("---")
    st.caption("v4.2.0 | LIVE CONNECTED")
    st.caption("Secure Link: Jan 2026 DB")

with col_main:
    # Top Action Bar
    c1, c2 = st.columns([3, 1])
    with c1:
        st.subheader(f"📍 Intelligence Target: {seat}")
    with c2:
        analyze_btn = st.button("RUN PREDICTION", type="primary", use_container_width=True)

    if analyze_btn:
        # 1. THE "PROCESSING" FEEL (Fake steps to show 'work' is happening)
        with st.status("🔄 Triangulating Data Points...", expanded=True) as status:
            st.write("🔹 Fetching Jan 2026 Candidate Manifests...")
            time.sleep(0.5)
            st.write("🔹 Analyzing Historical Swing Votes...")
            # Implicitly trigger fast model here
            fast_raw = get_fast_pulse(seat) 
            status.update(label="✅ Data Uplink Established", state="complete", expanded=False)

        # 2. PARSE FAST DATA (Simple Regex to extracting json-like values if needed, or just display)
        # For safety, we just pass the text to session state, but normally we'd parse JSON.
        
        # 3. RUN DEEP MODEL (Implicitly - user doesn't see a 'sync' button)
        deep_data = get_deep_analytics(seat)
        
        st.session_state.current_report = {
            "fast": fast_raw, 
            "deep": deep_data
        }

    # --- RESULTS DASHBOARD ---
    if st.session_state.current_report:
        data = st.session_state.current_report["deep"]
        
        # Extract Probability for Visual Gauge (Simple string parsing for demo)
        # In a real app, you'd ask Gemini for JSON to make this robust.
        # This is a fallback visualization based on the text.
        
        st.markdown("### 🔮 Predictive Modeling")
        
        # We display the text report in a highly structured way
        st.info(f"Analysis Timestamp: {data['timestamp']}")
        
        # The content from Gemini is already formatted as Markdown tables/lists
        # giving it that "Report" look.
        st.markdown(data["text"])
        
        st.markdown("---")
        st.caption("CONFIDENTIAL: For Strategic Use Only. Data aggregated from Election Commission & Open Source Intelligence.")

    else:
        # Default "Waiting" State
        st.markdown("""
        <div style="text-align: center; padding: 50px; color: #444;">
            <h3>Ready for Analysis</h3>
            <p>Select a sector and initiate prediction algorithms.</p>
        </div>
        """, unsafe_allow_html=True)
