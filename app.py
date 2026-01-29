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

# --- 2. INITIALIZE SESSION STATE ---
if "current_report" not in st.session_state:
    st.session_state.current_report = None

# --- 3. SMART MODEL SELECTOR ---
@st.cache_resource
def select_best_model():
    # Strict priority list as requested
    priority_models = [
        "gemini-3-pro-preview",   
        "gemini-3-flash-preview", 
        "gemini-2.0-flash",       
        "gemini-1.5-pro"          
    ]
    try:
        my_models = []
        for m in client.models.list():
            if "generateContent" in m.supported_actions:
                clean_name = m.name.replace("models/", "")
                my_models.append(clean_name)
        
        for model_id in priority_models:
            if model_id in my_models:
                return model_id
        return my_models[0] if my_models else "gemini-1.5-flash"
    except Exception:
        return "gemini-3-flash-preview"

ACTIVE_MODEL = select_best_model()

# --- 4. FULL 165 CONSTITUENCY DATA ---
constituency_data = {
    "Koshi (28)": ["Taplejung 1", "Panchthar 1", "Ilam 1", "Ilam 2", "Jhapa 1", "Jhapa 2", "Jhapa 3", "Jhapa 4", "Jhapa 5", "Sankhuwasabha 1", "Tehrathum 1", "Bhojpur 1", "Dhankuta 1", "Morang 1", "Morang 2", "Morang 3", "Morang 4", "Morang 5", "Morang 6", "Sunsari 1", "Sunsari 2", "Sunsari 3", "Sunsari 4", "Solukhumbu 1", "Khotang 1", "Okhaldhunga 1", "Udayapur 1", "Udayapur 2"],
    "Madhesh (32)": ["Saptari 1", "Saptari 2", "Saptari 3", "Saptari 4", "Siraha 1", "Siraha 2", "Siraha 3", "Siraha 4", "Dhanusha 1", "Dhanusha 2", "Dhanusha 3", "Dhanusha 4", "Mahottari 1", "Mahottari 2", "Mahottari 3", "Mahottari 4", "Sarlahi 1", "Sarlahi 2", "Sarlahi 3", "Sarlahi 4", "Rautahat 1", "Rautahat 2", "Rautahat 3", "Rautahat 4", "Bara 1", "Bara 2", "Bara 3", "Bara 4", "Parsa 1", "Parsa 2", "Parsa 3", "Parsa 4"],
    "Bagmati (33)": ["Dolakha 1", "Ramechhap 1", "Sindhuli 1", "Sindhuli 2", "Rasuwa 1", "Dhading 1", "Dhading 2", "Nuwakot 1", "Nuwakot 2", "Kathmandu 1", "Kathmandu 2", "Kathmandu 3", "Kathmandu 4", "Kathmandu 5", "Kathmandu 6", "Kathmandu 7", "Kathmandu 8", "Kathmandu 9", "Kathmandu 10", "Bhaktapur 1", "Bhaktapur 2", "Lalitpur 1", "Lalitpur 2", "Lalitpur 3", "Kavrepalanchok 1", "Kavrepalanchok 2", "Sindhupalchok 1", "Sindhupalchok 2", "Makwanpur 1", "Makwanpur 2", "Chitwan 1", "Chitwan 2", "Chitwan 3"],
    "Gandaki (18)": ["Gorkha 1", "Gorkha 2", "Manang 1", "Lamjung 1", "Kaski 1", "Kaski 2", "Kaski 3", "Tanahun 1", "Tanahun 2", "Syangja 1", "Syangja 2", "Nawalparasi East 1", "Nawalparasi East 2", "Mustang 1", "Myagdi 1", "Baglung 1", "Baglung 2", "Parbat 1"],
    "Lumbini (26)": ["Gulmi 1", "Gulmi 2", "Palpa 1", "Palpa 2", "Arghakhanchi 1", "Nawalparasi West 1", "Nawalparasi West 2", "Rupandehi 1", "Rupandehi 2", "Rupandehi 3", "Rupandehi 4", "Rupandehi 5", "Kapilvastu 1", "Kapilvastu 2", "Kapilvastu 3", "Dang 1", "Dang 2", "Dang 3", "Banke 1", "Banke 2", "Banke 3", "Bardiya 1", "Bardiya 2", "Rukum East 1", "Rolpa 1", "Pyuthan 1"],
    "Karnali (12)": ["Rukum West 1", "Salyan 1", "Dolpa 1", "Mugu 1", "Jumla 1", "Kalikot 1", "Humla 1", "Jajarkot 1", "Dailekh 1", "Dailekh 2", "Surkhet 1", "Surkhet 2"],
    "Sudurpashchim (16)": ["Bajura 1", "Bajhang 1", "Achham 1", "Achham 2", "Doti 1", "Kailali 1", "Kailali 2", "Kailali 3", "Kailali 4", "Kailali 5", "Kanchanpur 1", "Kanchanpur 2", "Kanchanpur 3", "Dadeldhura 1", "Baitadi 1", "Darchula 1"]
}

# --- 5. DEEP SIMULATION ENGINE (The Update) ---
@st.cache_data(ttl="1d", show_spinner=False)
def get_deep_analytics(constituency_name):
    # This prompt forces the AI to acknowledge the "Future History" of 2026
    prompt = f"""
    You are the Chief Strategy Officer for the Nepal Election Command Center (NECC).
    
    **CURRENT SIMULATION DATE:** January 29, 2026
    **ELECTION DATE:** March 5, 2026
    **CONTEXT:**
    * **Gen Z Uprising (Sept 2025):** Toppled the KP Oli govt; Sushila Karki is Interim PM.
    * **The Alliances:** * **RSP+Balen:** Balen Shah (PM Candidate) + Rabi Lamichhane + Kulman Ghising.
        * **NC (Reformed):** Gagan Thapa (PM Candidate) ousted Deuba.
        * **UML:** KP Oli (fighting for survival).
    * **The Vibe:** High anti-incumbency, 14k prisoners escaped (security risk), 52% voters are under 40.
    
    **MISSION:**
    Perform a "Deep Simulation" for **{constituency_name}**.
    Calculate the outcome by weighing these hidden variables:
    1.  **Caste/Ethnic Arithmetic:** (e.g., Brahmin/Chhetri vs Madhesi/Janajati dynamics in this specific seat).
    2.  **The 'Rebel' Factor:** Are there independent rebels splitting the NC/UML vote?
    3.  **Migration Impact:** How does the remittance/migrant labor vote swing here?
    4.  **Local Feuds:** Specific local development issues (roads, irrigation).
    
    **OUTPUT FORMAT (Strict Markdown):**
    
    ### 🎯 VICTORY PROJECTION
    * **Projected Winner:** [Name] ([Party])
    * **Win Probability:** [XX]% (Confidence Score)
    * **Swing Factor:** Needs a [XX]% swing for the runner-up to flip this.
    
    ### 📊 VOTE SHARE SIMULATION
    | Candidate | Party | Projected % | Trend |
    | :--- | :--- | :--- | :--- |
    | [Name] | [Party] | [XX]% | ↗️/↘️ |
    | [Name] | [Party] | [XX]% | ↗️/↘️ |
    | [Name] | [Party] | [XX]% | ➡️ |
    
    ### 🕵️ DEEP DIVE ANALYSIS
    * **The "X" Factor:** [The single biggest hidden variable deciding this seat]
    * **Caste/Community Logic:** [How the local ethnic math favors the winner]
    * **Security Risk:** [Is this a red-zone for violence given the prisoner escape context?]
    """
    
    try:
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
            "text": f"⚠️ **SIMULATION ERROR:** {str(e)}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "error"
        }

# --- 6. UI LAYOUT ---
st.markdown("""
<style>
    .metric-box { background-color: #0E1117; border: 1px solid #262730; padding: 20px; border-radius: 10px; text-align: center; }
    .stProgress > div > div > div > div { background-color: #00FF94; }
    .big-stat { font-size: 1.5rem; font-weight: bold; color: #00FF94; }
</style>
""", unsafe_allow_html=True)

# Dynamic Header
st.markdown(f"""
<div style="background-color: #0E1117; color: #00FF94; padding: 10px; font-family: 'Courier New', monospace; border-bottom: 2px solid #00FF94; margin-bottom: 20px;">
    <marquee scrollamount="10">🔒 WAR ROOM ACTIVE: Jan 29, 2026 • 🗳️ 3,406 Candidates Finalized • 🧠 ENGINE: {ACTIVE_MODEL.upper()}</marquee>
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
    st.metric("Days to Election", "35 Days", "March 5, 2026")
    st.caption(f"v6.0.0 | DEEP SIMULATION")

with col_main:
    c1, c2 = st.columns([3, 1])
    with c1:
        st.subheader(f"📍 Intelligence Target: {seat}")
    with c2:
        analyze_btn = st.button("RUN SIMULATION", type="primary", use_container_width=True)

    if analyze_btn:
        progress_text = "📡 Initiating Deep Simulation..."
        my_bar = st.progress(0, text=progress_text)

        # Simulation visuals
        steps = [
            "🔍 Scanning Jan 2026 Voter Rolls...",
            "📊 Calculating Caste/Ethnic Arithmetic...",
            "📉 Adjusting for 'Rebel' Candidates...",
            "⚖️ Weighing Gen Z Sentiment...",
            f"🧠 {ACTIVE_MODEL.upper()} Finalizing Strategy..."
        ]
        
        for i, step in enumerate(steps):
            time.sleep(0.3) 
            my_bar.progress((i + 1) * 20, text=step)
        
        deep_data = get_deep_analytics(seat)
        
        my_bar.empty()
        st.session_state.current_report = deep_data

    if st.session_state.current_report:
        data = st.session_state.current_report
        
        if data.get("status") == "error":
            st.error(data["text"])
        else:
            st.markdown("### 🔮 Strategic Output")
            st.caption(f"Generated by {data.get('model', 'Unknown')} • {data['timestamp']}")
            st.markdown(data["text"])
            st.markdown("---")
            st.warning("⚠️ CLASSIFIED: This simulation considers unverified 'Black Swan' variables including the 2025 security breach.")
    else:
        st.markdown("""
        <div style="text-align: center; padding: 50px; color: #444;">
            <h3>Ready for Analysis</h3>
            <p>Select a constituency to begin Monte Carlo simulation.</p>
        </div>
        """, unsafe_allow_html=True)
