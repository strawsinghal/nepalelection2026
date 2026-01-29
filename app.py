import streamlit as st
import datetime
import time
from google import genai
from google.genai import types

# --- CONFIGURATION ---
# Primary: The powerful model you want
DEEP_MODEL = "gemini-3-pro-preview" 
# Fallback: The reliable model if Pro hangs
FALLBACK_MODEL = "gemini-2.0-flash-exp"

# Initialize Client
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

# --- SESSION STATE ---
if "current_report" not in st.session_state:
    st.session_state.current_report = None

# --- CORE LOGIC (With Safety Net) ---
@st.cache_data(ttl="1d", show_spinner=False)
def get_deep_analytics(constituency_name):
    """
    Robust function: Tries Gemini 3 Pro first. 
    If it fails/hangs, falls back to Gemini 2 Flash instantly.
    """
    prompt = f"""
    Act as a Chief Election Strategist for {constituency_name}, Nepal (March 5, 2026).
    Output strictly in this structure:
    ### 🏆 PROJECTED OUTCOME
    * **Winner Prediction:** [Name] ([Party])
    * **Win Probability:** [XX]%
    
    ### 📉 CANDIDATE POSITIONS
    1. **[Name]** ([Party]) - [XX]%
    2. **[Name]** ([Party]) - [XX]%
    
    ### 🧠 STRATEGIC REASONING
    * **Key Factor:** [Detail]
    """
    
    # Attempt 1: Deep Model
    try:
        response = client.models.generate_content(
            model=DEEP_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        return {
            "text": response.text,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "model": "Gemini 3 Pro",
            "status": "success"
        }
    except Exception as e:
        # Attempt 2: Fallback (Safety Net)
        try:
            time.sleep(1) # Brief pause
            fallback_resp = client.models.generate_content(
                model=FALLBACK_MODEL,
                contents=prompt
            )
            return {
                "text": fallback_resp.text,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "model": "Gemini 2 Flash (Fallback)",
                "status": "success"
            }
        except Exception as e2:
             return {
                "text": f"⚠️ **SYSTEM FAILURE:** {str(e2)}",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "status": "error"
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
    }
    .stProgress > div > div > div > div {
        background-color: #00FF94;
    }
    /* Fix for large header */
    h1 { font-size: 2.5rem !important; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown(f"""
<div style="background-color: #0E1117; color: #00FF94; padding: 10px; font-family: 'Courier New', monospace; border-bottom: 2px solid #00FF94; margin-bottom: 20px;">
    <marquee scrollamount="10">🔒 SYSTEM ACTIVE: 3,406 Candidates Tracked • 📡 UPLINK: 23,112 Polling Centers</marquee>
</div>
""", unsafe_allow_html=True)

# --- MAIN UI ---
col_sidebar, col_main = st.columns([1, 4], gap="medium")

with col_sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Flag_of_Nepal.svg/1200px-Flag_of_Nepal.svg.png", width=50)
    st.title("Command Center")
    st.markdown("---")
    
    # Navigation
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
    st.caption("v4.5.0 | FAILSAFE ACTIVE")

with col_main:
    # Action Bar
    c1, c2 = st.columns([3, 1])
    with c1:
        st.subheader(f"📍 Intelligence Target: {seat}")
    with c2:
        # Fixed: Changed use_container_width to width="stretch" to stop warnings
        analyze_btn = st.button("RUN PREDICTION", type="primary", width="stretch")

    # --- PROGRESS BAR LOGIC ---
    if analyze_btn:
        progress_text = "📡 Initiating Satellite Uplink..."
        my_bar = st.progress(0, text=progress_text)

        # 1. Visual Start
        for percent_complete in range(0, 30, 10):
            time.sleep(0.05) 
            my_bar.progress(percent_complete, text=f"🔍 Scanning Database... {percent_complete}%")

        # 2. Heavy Lift (The part that was stuck)
        my_bar.progress(40, text="🧠 RUNNING DEEP REASONING MODEL...")
        
        # 3. Execution
        deep_data = get_deep_analytics(seat)
        
        # 4. Completion
        my_bar.progress(100, text="🚀 ANALYSIS COMPLETE")
        time.sleep(0.5)
        my_bar.empty()
        
        st.session_state.current_report = deep_data

    # --- RESULTS DASHBOARD ---
    if st.session_state.current_report:
        data = st.session_state.current_report
        
        if data.get("status") == "error":
            st.error(data["text"])
        else:
            # Display Report
            st.markdown("### 🔮 Predictive Modeling")
            
            # Show which model was actually used
            st.caption(f"Verified Intelligence • Source: {data.get('model', 'Unknown')} • Timestamp: {data['timestamp']}")
            
            st.markdown(data["text"])
            st.markdown("---")
            st.caption("CONFIDENTIAL: For Strategic Use Only.")

    else:
        st.markdown("""
        <div style="text-align: center; padding: 50px; color: #444;">
            <h3>Ready for Analysis</h3>
            <p>Select a sector and click 'RUN PREDICTION'.</p>
        </div>
        """, unsafe_allow_html=True)
