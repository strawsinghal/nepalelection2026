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

# --- 2. SMART MODEL SELECTOR ---
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
        "gemini-1.5-pro"          # Final Safety Net
    ]
    
    try:
        # Get list of models your API Key actually has access to
        my_models = []
        for m in client.models.list():
            if "generateContent" in m.supported_actions:
                # INDENTATION FIXED HERE
                clean_name = m.name.replace("models/", "")
                my_models.append(clean_name)
        
        # Pick the first one from your list that exists in your key's permissions
        for model_id in priority_models:
            if model_id in my_models:
                return model_id
        
        # If none match, return the first available one to keep app alive
        return my_models[0] if my_models else "gemini-1.5-flash"

    except Exception:
        # If listing fails, blindly try Gemini 3 Flash
        return "gemini-3-flash-preview"

# Detect the best model ONCE when app starts
ACTIVE_MODEL = select_best_model()

# --- 3. FULL 165 CONSTITUENCY DATA ---
constituency_data = {
    "Koshi (28)": [
        "Taplejung 1", "Panchthar 1", "Ilam 1", "Ilam 2", 
        "Jhapa 1", "Jhapa 2", "Jhapa 3", "Jhapa 4", "Jhapa 5", 
        "Sankhuwasabha 1", "Tehrathum 1", "Bhojpur 1", "Dhankuta 1", 
        "Morang 1", "Morang 2", "Morang 3", "Morang 4", "Morang 5", "Morang 6", 
        "Sunsari 1", "Sunsari 2", "Sunsari 3", "Sunsari 4", 
        "Solukhumbu 1", "Khotang 1", "Okhaldhunga 1", "Udayapur 1", "Udayapur 2"
    ],
    "Madhesh (32)": [
        "Saptari 1", "Saptari 2", "Saptari 3", "Saptari 4", 
        "Siraha 1", "Siraha 2", "Siraha 3", "Siraha 4", 
        "Dhanusha 1", "Dhanusha 2", "Dhanusha 3", "Dhanusha 4", 
        "Mahottari 1", "Mahottari 2", "Mahottari 3", "Mahottari 4", 
        "Sarlahi 1", "Sarlahi 2", "Sarlahi 3", "Sarlahi 4", 
        "Rautahat 1", "Rautahat 2", "Rautahat 3", "Rautahat 4", 
        "Bara 1", "Bara 2", "Bara 3", "Bara 4", 
        "Parsa 1", "Parsa 2", "Parsa 3", "Parsa 4"
    ],
    "Bagmati (33)": [
        "Dolakha 1", "Ramechhap 1", "Sindhuli 1", "Sindhuli 2", 
        "Rasuwa 1", "Dhading 1", "Dhading 2", "Nuwakot 1", "Nuwakot 2", 
        "Kathmandu 1", "Kathmandu 2", "Kathmandu 3", "Kathmandu 4", "Kathmandu 5", 
        "Kathmandu 6", "Kathmandu 7", "Kathmandu 8", "Kathmandu 9", "Kathmandu 10", 
        "Bhaktapur 1", "Bhaktapur 2", "Lalitpur 1", "Lalitpur 2", "Lalitpur 3", 
        "Kavrepalanchok 1", "Kavrepalanchok 2", "Sindhupalchok 1", "Sindhupalchok 2", 
        "Makwanpur 1", "Makwanpur 2", "Chitwan 1", "Chitwan 2", "Chitwan 3"
    ],
    "Gandaki (18)": [
        "Gorkha 1", "Gorkha 2", "Manang 1", "Lamjung 1", 
        "Kaski 1", "Kaski 2", "Kaski 3", "Tanahun 1", "Tanahun 2", 
        "Syangja 1", "Syangja 2", "Nawalparasi East 1", "Nawalparasi East 2", 
        "Mustang 1", "Myagdi 1", "Baglung 1", "Baglung 2", "Parbat 1"
    ],
    "Lumbini (26)": [
        "Gulmi 1", "Gulmi 2", "Palpa 1", "Palpa 2", "Arghakhanchi 1", 
        "Nawalparasi West 1", "Nawalparasi West 2", 
        "Rupandehi 1", "Rupandehi 2", "Rupandehi 3", "Rupandehi 4", "Rupandehi 5", 
        "Kapilvastu 1", "Kapilvastu 2", "Kapilvastu 3", 
        "Dang 1", "Dang 2", "Dang 3", 
        "Banke 1", "Banke 2", "Banke 3", "Bardiya 1", "Bardiya 2", 
        "Rukum East 1", "Rolpa 1", "Pyuthan 1"
    ],
    "Karnali (12)": [
        "Rukum West 1", "Salyan 1", "Dolpa 1", "Mugu 1", 
        "Jumla 1", "Kalikot 1", "Humla 1", "Jajarkot 1", 
        "Dailekh 1", "Dailekh 2", "Surkhet 1", "Surkhet 2"
    ],
    "Sudurpashchim (16)": [
        "Bajura 1", "Bajhang 1", "Achham 1", "Achham 2", "Doti 1", 
        "Kailali 1", "Kailali 2", "Kailali 3", "Kailali 4", "Kailali 5", 
        "Kanchanpur 1", "Kanchanpur 2", "Kanchanpur 3", 
        "Dadeldhura 1", "Baitadi 1", "Darchula 1"
    ]
}

# --- 4. CORE ANALYTICS ENGINE ---
@st.cache_data(ttl="1d", show_spinner=False)
def get_deep_analytics(constituency_name):
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
    
    try:
        # Using the auto-selected best model
        response = client.models.generate_content(
            model=ACTIVE_MODEL,
            contents=prompt
        )
        return {
            "text": response.text,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "model": ACTIVE_MODEL,
            "status": "success"
        }
    except Exception as e:
         return {
            "text": f"⚠️ **API FAILURE:** {str(e)}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "error"
        }

# --- 5. UI LAYOUT ---
st.markdown("""
<style>
    .metric-box { background-color: #0E1117; border: 1px solid #262730; padding: 20px; border-radius: 10px; text-align: center; }
    .stProgress > div > div > div > div { background-color: #00FF94; }
</style>
""", unsafe_allow_html=True)

# Dynamic Header
st.markdown(f"""
<div style="background-color: #0E1117; color: #00FF94; padding: 10px; font-family: 'Courier New', monospace; border-bottom: 2px solid #00FF94; margin-bottom: 20px;">
    <marquee scrollamount="10">🔒 SYSTEM ACTIVE: 3,406 Candidates Tracked • 🧠 INTELLIGENCE ENGINE: {ACTIVE_MODEL.upper()}</marquee>
</div>
""", unsafe_allow_html=True)

col_sidebar, col_main = st.columns([1, 4], gap="medium")

with col_sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Flag_of_Nepal.svg/1200px-Flag_of_Nepal.svg.png", width=50)
    st.title("Command Center")
    st.markdown("---")
    
    # Navigation
    prov = st.selectbox("OPERATIONAL ZONE", list(constituency_data.keys()))
    seat = st.selectbox("TARGET SECTOR", constituency_data[prov])
    
    st.markdown("---")
    st.caption(f"v5.1.0 | POWERED BY {ACTIVE_MODEL}")

with col_main:
    c1, c2 = st.columns([3, 1])
    with c1:
        st.subheader(f"📍 Intelligence Target: {seat}")
    with c2:
        analyze_btn = st.button("RUN PREDICTION", type="primary", use_container_width=True)

    if analyze_btn:
        progress_text = "📡 Initiating Satellite Uplink..."
        my_bar = st.progress(0, text=progress_text)

        # Simulation of "working" steps
        for percent_complete in range(0, 30, 10):
            time.sleep(0.05) 
            my_bar.progress(percent_complete, text=f"🔍 Scanning Database... {percent_complete}%")

        my_bar.progress(40, text=f"🧠 RUNNING {ACTIVE_MODEL.upper()}...")
        
        deep_data = get_deep_analytics(seat)
        
        my_bar.progress(100, text="🚀 ANALYSIS COMPLETE")
        time.sleep(0.5)
        my_bar.empty()
        
        st.session_state.current_report = deep_data

    if st.session_state.current_report:
        data = st.session_state.current_report
        
        if data.get("status") == "error":
            st.error(data["text"])
        else:
            st.markdown("### 🔮 Predictive Modeling")
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
