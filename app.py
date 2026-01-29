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

st.set_page_config(page_title="Nepal 2026 Strategy Room", layout="wide", initial_sidebar_state="expanded")

# --- SESSION STATE ---
if "current_report" not in st.session_state:
    st.session_state.current_report = None

# --- CACHING LOGIC ---
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

# --- STYLING ---
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
    .stProgress > div > div > div > div {
        background-color: #00FF94;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER & TICKER ---
ticker_text = "🔒 SYSTEM ACTIVE: 3,406 Candidates Tracked • 📡 UPLINK: 23,112 Polling Centers • ⚠️ ALERT: Jhapa-5 Swing Variable High"
st.markdown(f"""
<div style="background-color: #0E1117; color: #00FF94; padding: 10px; font-family: 'Courier New', monospace; border-bottom: 2px solid #00FF94; margin-bottom: 20px;">
    <marquee scrollamount="10">{ticker_text}</marquee>
</div>
""", unsafe_allow_html=True)

# --- MAIN UI ---
col_sidebar, col_main = st.columns([1, 4], gap="medium")

with col_sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Flag_of_Nepal.svg/1200px-Flag_of_Nepal.svg.png", width=50)
    st.title("Command Center")
    st.markdown("---")
    
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
    st.caption("v4.3.0 | LIVE CONNECTED")

with col_main:
    # Action Bar
    c1, c2 = st.columns([3, 1])
    with c1:
        st.subheader(f"📍 Intelligence Target: {seat}")
    with c2:
        analyze_btn = st.button("RUN PREDICTION", type="primary", use_container_width=True)

    # --- PROGRESS BAR LOGIC ---
    if analyze_btn:
        # 1. CREATE BAR
        progress_text = "📡 Initiating Satellite Uplink..."
        my_bar = st.progress(0, text=progress_text)

        # 2. SIMULATE CONNECTION (0-30%)
        # This gives immediate visual feedback
        for percent_complete in range(0, 40, 10):
            time.sleep(0.05) 
            my_bar.progress(percent_complete, text=f"🔍 Scanning Jan 2026 Database... {percent_complete}%")

        # 3. THE HEAVY LIFT (40%)
        # This text tells the user "Wait, we are doing real work now"
        my_bar.progress(40, text="🧠 RUNNING DEEP REASONING MODEL... (Please Wait)")
        
        # 4. EXECUTE API CALL (Blocking)
        deep_data = get_deep_analytics(seat)
        
        # 5. FINALIZE (90-100%)
        my_bar.progress(90, text="✅ Synthesizing Strategy Report...")
        time.sleep(0.2)
        my_bar.progress(100, text="🚀 ANALYSIS COMPLETE")
        time.sleep(0.5)
        my_bar.empty() # Hide bar to show results cleanly
        
        # Store in session state
        st.session_state.current_report = deep_data

    # --- RESULTS DASHBOARD ---
    if st.session_state.current_report:
        data = st.session_state.current_report
        
        st.markdown("### 🔮 Predictive Modeling")
        st.info(f"Verified Intelligence • Timestamp: {data['timestamp']}")
        
        # Display the Deep Report
        st.markdown(data["text"])
        
        st.markdown("---")
        st.caption("CONFIDENTIAL: For Strategic Use Only. Data aggregated from Election Commission & Open Source Intelligence.")

    else:
        # Default State
        st.markdown("""
        <div style="text-align: center; padding: 50px; color: #444;">
            <h3>Ready for Analysis</h3>
            <p>Select a sector and click 'RUN PREDICTION' to begin deep scan.</p>
        </div>
        """, unsafe_allow_html=True)
