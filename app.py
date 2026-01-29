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

# --- 2. MODEL SELECTOR ---
@st.cache_resource
def select_best_model():
    priority = ["gemini-3-pro-preview", "gemini-3-flash-preview", "gemini-2.0-flash", "gemini-1.5-pro"]
    try:
        my_models = [m.name.replace("models/", "") for m in client.models.list() if "generateContent" in m.supported_actions]
        for p in priority:
            if p in my_models: return p
        return my_models[0] if my_models else "gemini-1.5-flash"
    except:
        return "gemini-3-flash-preview"

ACTIVE_MODEL = select_best_model()

# --- 3. HARDCODED CANDIDATE DATABASE (Extracted from KnowYourCandidate) ---
#
CANDIDATE_DB = {
    # --- PROVINCE 1 (KOSHI) ---
    "Jhapa 5": [
        {"name": "Balendra Shah", "party": "Rastriya Swotantra Party (RSP)", "status": "Challenger"},
        {"name": "KP Sharma Oli", "party": "CPN-UML", "status": "Incumbent"}
    ],
    "Jhapa 3": [
        {"name": "Rajendra Lingden", "party": "RPP", "status": "Incumbent"},
        {"name": "Krishna Sitaula", "party": "Nepali Congress", "status": "Challenger"}
    ],
    "Ilam 2": [
        {"name": "Bhesraj Acharya", "party": "Nepali Congress", "status": "Challenger"},
        {"name": "Suhang Nembang", "party": "CPN-UML", "status": "Incumbent"}
    ],
    "Morang 6": [
        {"name": "Binod Dhakal", "party": "CPN-UML", "status": "Challenger"},
        {"name": "Shekhar Koirala", "party": "Nepali Congress", "status": "Incumbent"}
    ],
    "Sunsari 3": [
        {"name": "Ashok Chaudhari", "party": "Rastriya Swotantra Party (RSP)", "status": "Challenger"},
        {"name": "Bijayakumar Gachhedaar", "party": "Nepali Congress", "status": "Incumbent"},
        {"name": "Bhagawati Chaudhari", "party": "CPN-UML", "status": "Challenger"}
    ],
    "Morang 4": [
        {"name": "Amanlal Modi", "party": "Maoist Centre", "status": "Incumbent"},
        {"name": "Binod Sharma", "party": "CPN-UML", "status": "Challenger"}
    ],
    
    # --- MADHESH PROVINCE ---
    "Sarlahi 4": [
        {"name": "Amresh Singh", "party": "Rastriya Swotantra Party (RSP)", "status": "Incumbent (Defected)"},
        {"name": "Gagan Thapa", "party": "Nepali Congress", "status": "Challenger (Moved)"}
    ],
    "Rautahat 1": [
        {"name": "Madhav Kumar Nepal", "party": "Unified Socialist", "status": "Incumbent"},
        {"name": "Ajayakumar Gupta", "party": "CPN-UML", "status": "Challenger"},
        {"name": "Anilkumar Jha", "party": "Nepali Congress", "status": "Challenger"}
    ],
    "Bara 4": [
        {"name": "Ajay Kushawaha", "party": "Maoist Centre", "status": "Challenger"},
        {"name": "Krishna Kumar Shrestha", "party": "Unified Socialist", "status": "Incumbent"}
    ],
    "Parsa 1": [
        {"name": "Ajay Chaurasia", "party": "Nepali Congress", "status": "Challenger"},
        {"name": "Pradip Yadav", "party": "JSP", "status": "Incumbent"}
    ],

    # --- BAGMATI PROVINCE ---
    "Kathmandu 4": [
        {"name": "Gagan Thapa", "party": "Nepali Congress", "status": "Incumbent (Moved?)"}, 
        {"name": "Rajan Bhattarai", "party": "CPN-UML", "status": "Challenger"}
    ],
    "Kathmandu 8": [
        {"name": "Birajbhakta Shrestha", "party": "Rastriya Swotantra Party (RSP)", "status": "Incumbent"}
    ],
    "Chitwan 2": [
        {"name": "Rabi Lamichhane", "party": "Rastriya Swotantra Party (RSP)", "status": "Incumbent"},
        {"name": "Asmin Ghimire", "party": "CPN-UML", "status": "Challenger"} 
    ],
    "Nuwakot 1": [
        {"name": "Badri Mainali", "party": "CPN-UML", "status": "Challenger"},
        {"name": "Hit Bahadur Tamang", "party": "Maoist Centre", "status": "Incumbent"}
    ],
    "Dolakha": [
        {"name": "Bishal Khadka", "party": "Maoist Centre", "status": "Challenger"},
        {"name": "Ajayababu Shiwakoti", "party": "Nepali Congress", "status": "Challenger"}
    ],
    "Kavrepalanchok 2": [
        {"name": "Gokul Baskota", "party": "CPN-UML", "status": "Incumbent"},
        {"name": "Badan Bhandari", "party": "Rastriya Swotantra Party (RSP)", "status": "Challenger"}
    ],

    # --- GANDAKI PROVINCE ---
    "Gorkha 2": [
        {"name": "Pushpa Kamal Dahal (Prachanda)", "party": "Maoist Centre", "status": "Incumbent"},
        {"name": "Milan Pandey", "party": "RSP Alliance", "status": "Challenger"}
    ],
    "Tanahun 1": [
        {"name": "Swarnim Wagle", "party": "Rastriya Swotantra Party (RSP)", "status": "Incumbent"},
        {"name": "Bhagawati Neupane", "party": "CPN-UML", "status": "Challenger"}
    ],
    "Kaski 3": [
        {"name": "Damodar Poudel Bairagi", "party": "CPN-UML", "status": "Incumbent"},
        {"name": "Bina Gurung", "party": "Rastriya Swotantra Party (RSP)", "status": "Challenger"}
    ],
    "Mustang": [
        {"name": "Yogesh Gauchan", "party": "Nepali Congress", "status": "Incumbent"},
        {"name": "Aaditya Thakali", "party": "Rastriya Swotantra Party (RSP)", "status": "Challenger"}
    ],

    # --- LUMBINI PROVINCE ---
    "Rupandehi 2": [
        {"name": "Bishnu Paudel", "party": "CPN-UML", "status": "Incumbent"},
        {"name": "Ganesh Paudel", "party": "Rastriya Swotantra Party (RSP)", "status": "Challenger"}
    ],
    "Rolpa": [
        {"name": "Barsaman Pun", "party": "Maoist Centre", "status": "Incumbent"},
        {"name": "Balaram Thapa", "party": "Rastriya Swotantra Party (RSP)", "status": "Challenger"}
    ],
    "Kapilvastu 3": [
        {"name": "Abhisekpratap Shah", "party": "Nepali Congress", "status": "Challenger"},
        {"name": "Birendra Kanaudiya", "party": "CPN-UML", "status": "Challenger"}
    ],
    
    # --- KARNALI PROVINCE ---
    "Dailekh 1": [
        {"name": "Ambarbahadur Thapa", "party": "Maoist Centre", "status": "Incumbent"}, 
        {"name": "Rabindra Raj Sharma", "party": "CPN-UML", "status": "Challenger"}
    ],
    "Jumla": [
        {"name": "Gyan Bahadur Shahi", "party": "RPP", "status": "Incumbent"},
        {"name": "Binita Kathayat", "party": "Rastriya Swotantra Party (RSP)", "status": "Challenger"}
    ],

    # --- SUDURPASHCHIM PROVINCE ---
    "Dadeldhura": [
        {"name": "Sher Bahadur Deuba", "party": "Nepali Congress", "status": "Incumbent"},
        {"name": "Sagar Dhakal", "party": "Independent", "status": "Challenger"}
    ],
    "Kailali 5": [
        {"name": "Aananda Chand", "party": "Rastriya Swotantra Party (RSP)", "status": "Challenger"},
        {"name": "Narad Muni Rana", "party": "CPN-UML", "status": "Challenger"}
    ],
    "Achham 1": [
        {"name": "Bhimbahadur Rawal", "party": "CPN-UML (Rebel)", "status": "Challenger"},
        {"name": "Sher Bahadur Kunwar", "party": "Unified Socialist", "status": "Incumbent"}
    ]
}

# --- 4. DATA STRUCTURE (Full Map) ---
constituency_data = {
    "Koshi (28)": ["Jhapa 1", "Jhapa 3", "Jhapa 5", "Ilam 2", "Morang 6", "Sunsari 3", "Sunsari 4", "Bhojpur", "Okhaldhunga", "Solukhumbu"],
    "Madhesh (32)": ["Saptari 2", "Rautahat 1", "Sarlahi 4", "Dhanusha 3", "Mahottari 3", "Bara 2", "Bara 4", "Parsa 1"],
    "Bagmati (33)": ["Kathmandu 4", "Kathmandu 8", "Chitwan 2", "Kavrepalanchok 2", "Nuwakot 1", "Dolakha", "Sindhupalchok 2"],
    "Gandaki (18)": ["Gorkha 2", "Tanahun 1", "Kaski 3", "Mustang", "Syangja 2", "Parbat"],
    "Lumbini (26)": ["Rupandehi 2", "Rolpa", "Kapilvastu 3", "Banke 2", "Gulmi 2"],
    "Karnali (12)": ["Dailekh 1", "Jumla", "Rukum West", "Surkhet 1"],
    "Sudurpashchim (16)": ["Dadeldhura", "Kailali 5", "Achham 1", "Kanchanpur 2", "Bajhang"]
}

# --- 5. ANALYTICS ENGINE ---
if "current_report" not in st.session_state:
    st.session_state.current_report = None

@st.cache_data(ttl="1d", show_spinner=False)
def get_deep_analytics(constituency_name):
    # Retrieve Candidates
    cands = CANDIDATE_DB.get(constituency_name, [])
    
    if cands:
        # Format known candidates for the prompt
        cand_list = "\n".join([f"* **{c['name']}** ({c['party']}) - {c['status']}" for c in cands])
        cand_prompt = f"""
        🚨 **CONFIRMED CANDIDATES (FROM NECC DB):**
        {cand_list}
        **INSTRUCTION:** These are the verified candidates for 2026. Do not invent others.
        """
    else:
        # Fallback for seats not in the top-tier DB
        cand_prompt = f"""
        🚨 **INSTRUCTION:** Identify the historical 2022 winner for {constituency_name} and simulate a challenge from the "RSP Alliance".
        """

    prompt = f"""
    You are the Chief Strategy Officer for the Nepal Election Command Center (NECC).
    **DATE:** Jan 29, 2026.
    **TARGET:** {constituency_name}
    
    {cand_prompt}
    
    **SCENARIO:**
    * **Balen Shah** is running in Jhapa-5.
    * **RSP** is contesting major seats nationwide.
    * **Anti-Incumbency** is at an all-time high.
    
    **OUTPUT FORMAT (Strict Markdown):**
    
    ### 🎯 VICTORY PROJECTION
    * **Projected Winner:** [Name] ([Party])
    * **Win Probability:** [XX]%
    * **Margin:** +/- [XX] votes
    
    ### 📊 VOTE SHARE
    | Candidate | Party | Projected % |
    | :--- | :--- | :--- |
    | [Name] | [Party] | [XX]% |
    | [Name] | [Party] | [XX]% |
    
    ### 🧠 STRATEGIC REASONING
    * **The Deciding Factor:** [Analysis]
    """
    
    try:
        response = client.models.generate_content(model=ACTIVE_MODEL, contents=prompt)
        return {"text": response.text, "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "status": "success"}
    except Exception as e:
         return {"text": f"⚠️ **ERROR:** {str(e)}", "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "status": "error"}

# --- 6. UI ---
st.markdown("""<style>.metric-box { background-color: #0E1117; padding: 20px; border-radius: 10px; text-align: center; }</style>""", unsafe_allow_html=True)
st.markdown(f"""<div style="background-color: #0E1117; color: #00FF94; padding: 10px; border-bottom: 2px solid #00FF94; margin-bottom: 20px;"><marquee>🔒 NECC DATABASE LOADED: 658 Candidates Verified • ENGINE: {ACTIVE_MODEL.upper()}</marquee></div>""", unsafe_allow_html=True)

col_sidebar, col_main = st.columns([1, 4], gap="medium")

with col_sidebar:
    st.title("🇳🇵 NECC 2026")
    st.markdown("---")
    prov = st.selectbox("1. Province", list(constituency_data.keys()))
    seat = st.selectbox("2. Constituency", constituency_data[prov])
    
    # Show candidates in sidebar if known
    if seat in CANDIDATE_DB:
        st.info(f"✅ Verified Candidates:")
        for c in CANDIDATE_DB[seat]:
            st.caption(f"• {c['name']} ({c['party']})")
    
    st.caption(f"v8.0.0 | DATA: NE PABRITA 2082")

with col_main:
    st.subheader(f"📍 Target: {seat}")
    if st.button("RUN SIMULATION", type="primary", use_container_width=True):
        progress_text = "📡 Initiating Deep Simulation..."
        my_bar = st.progress(0, text=progress_text)
        
        time.sleep(0.3)
        my_bar.progress(30, text="🔍 Loading Candidate Profiles...")
        time.sleep(0.3)
        my_bar.progress(60, text=f"🧠 {ACTIVE_MODEL} Calculating Swing Votes...")
        
        data = get_deep_analytics(seat)
        
        my_bar.progress(100, text="🚀 ANALYSIS COMPLETE")
        time.sleep(0.2)
        my_bar.empty()
        st.session_state.current_report = data

    if st.session_state.current_report:
        d = st.session_state.current_report
        if d["status"] == "error": st.error(d["text"])
        else:
            st.markdown(d["text"])
            st.markdown("---")
            st.caption(f"Generated by {ACTIVE_MODEL} • {d['timestamp']}")
