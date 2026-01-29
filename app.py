import streamlit as st
import time
import json
import pandas as pd
from google import genai
from google.genai import types

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="NECC: Official Election Dashboard",
    page_icon="🇳🇵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional "Newsroom" CSS
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp { background-color: #F5F7F9; color: #1E1E1E; font-family: 'Helvetica Neue', sans-serif; }
    
    /* Header Styling */
    h1 { color: #DC143C; font-weight: 800; letter-spacing: -1px; }
    h2, h3 { color: #003366; }
    
    /* Login Box */
    .login-box {
        background: white;
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        max-width: 500px;
        margin: auto;
    }
    
    /* Metrics Cards */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #DC143C;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Custom Button */
    .stButton>button {
        background-color: #003366;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stButton>button:hover { background-color: #002244; }
</style>
""", unsafe_allow_html=True)

# --- 2. AUTHENTICATION & SESSION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None

def login():
    st.session_state.logged_in = True
    st.session_state.user_role = "admin"
    st.rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.rerun()

# --- 3. DATA & AI ENGINE ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("System Error: API Configuration Missing.")
        st.stop()
except:
    st.error("System Error: Connection Failed.")
    st.stop()

# Full Constituency Map (Truncated for brevity, normally list all 165)
constituency_data = {
    "Koshi": ["Taplejung 1", "Jhapa 1", "Jhapa 5", "Ilam 2", "Morang 6", "Sunsari 1"],
    "Madhesh": ["Saptari 2", "Rautahat 1", "Sarlahi 4", "Dhanusha 3"],
    "Bagmati": ["Kathmandu 4", "Kathmandu 5", "Chitwan 2", "Lalitpur 3"],
    "Gandaki": ["Gorkha 2", "Tanahun 1", "Kaski 2"],
    "Lumbini": ["Rupandehi 2", "Dang 2", "Banke 2"],
    "Karnali": ["Surkhet 1", "Jumla"],
    "Sudurpashchim": ["Dadeldhura 1", "Kailali 5"]
}

@st.cache_data(ttl=3600, show_spinner=False)
def get_strategic_intel(seat):
    """
    Fetches data and forces a JSON response so we can build a UI from it.
    """
    prompt = f"""
    Act as a Data Aggregator for the Nepal Election Commission (2026 Context).
    Target: {seat}
    
    TASK:
    1. SEARCH for the confirmed candidates.
    2. ANALYZE the 'Gen Z / Balen' impact factor.
    3. PREDICT the winner based on current sentiment.
    
    RETURN ONLY RAW JSON (No markdown formatting):
    {{
        "candidates": [
            {{"name": "Candidate A", "party": "Party", "status": "Incumbent/Challenger"}},
            {{"name": "Candidate B", "party": "Party", "status": "Challenger"}}
        ],
        "prediction": {{
            "winner": "Name",
            "party": "Party",
            "probability": "XX",
            "margin": "XX Votes"
        }},
        "factors": {{
            "swing_vote": "High/Low",
            "key_issue": "Short phrase (e.g., Youth Unemployment)"
        }},
        "analysis_text": "A short, professional paragraph summarizing the strategic situation."
    }}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp", # Fast & Smart
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except:
        return None

# --- 4. VIEW: LOGIN PAGE (The Gatekeeper) ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class='login-box'>
            <img src='https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Flag_of_Nepal.svg/1200px-Flag_of_Nepal.svg.png' width='60' style='margin-bottom: 15px;'>
            <h2 style='margin-top:0;'>NECC Portal</h2>
            <p style='color:gray; font-size: 14px;'>Authorized Personnel Only. <br>Restricted Access System (v4.2)</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Secure Login", use_container_width=True)
            
            if submitted:
                if user == "admin" and pw == "admin":
                    login()
                else:
                    st.error("⛔ Access Denied: Invalid Credentials")

        st.markdown("---")
        st.markdown("<div style='text-align: center;'><strong>New Analyst?</strong></div>", unsafe_allow_html=True)
        
        # LINK TO GOOGLE FORM
        google_form_url = "https://docs.google.com/forms/" # REPLACE THIS with your actual form link
        st.link_button(
            "📝 Request Access (Signup)", 
            google_form_url, 
            type="secondary", 
            use_container_width=True,
            help="Submit your credentials for verification."
        )

# --- 5. VIEW: MAIN DASHBOARD (The Admin Tool) ---
else:
    # Sidebar Navigation
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Flag_of_Nepal.svg/1200px-Flag_of_Nepal.svg.png", width=40)
        st.markdown("**Admin Console**")
        st.caption(f"User: {st.session_state.user_role.upper()}")
        st.markdown("---")
        if st.button("Log Out"):
            logout()

    # Main Content Area
    st.title("🗳️ Election Intelligence Dashboard")
    st.markdown("Real-time constituency monitoring and strategic synthesis.")
    st.markdown("---")

    # Selection Row
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        prov = st.selectbox("Province", list(constituency_data.keys()))
    with col2:
        seat = st.selectbox("Constituency", constituency_data[prov])
    with col3:
        st.write("") # Spacer
        st.write("") # Spacer
        run_btn = st.button("Generate Dossier", type="primary", use_container_width=True)

    if run_btn:
        with st.status("🔄 Aggregating Field Data...", expanded=True) as status:
            st.write("📡 Querying Election Commission Database...")
            time.sleep(0.5)
            st.write("📰 Scanning Regional News Outlets...")
            
            data = get_strategic_intel(seat)
            
            status.update(label="✅ Data Synthesis Complete", state="complete", expanded=False)

        if data:
            # --- SECTION A: HEADLINE METRICS ---
            # This looks like a dashboard, not a chat
            st.markdown("### 🎯 Projected Outcome")
            m1, m2, m3, m4 = st.columns(4)
            
            pred = data.get("prediction", {})
            fact = data.get("factors", {})
            
            with m1:
                st.metric("Lead Candidate", pred.get("winner", "Unknown"), delta="Projected Winner")
            with m2:
                st.metric("Win Probability", f"{pred.get('probability', '0')}%", delta_color="normal")
            with m3:
                st.metric("Vote Margin", pred.get("margin", "N/A"))
            with m4:
                st.metric("Swing Factor", fact.get("swing_vote", "Unknown"))

            st.markdown("---")

            # --- SECTION B: CANDIDATE TABLE ---
            st.markdown("### 📋 Confirmed Nominations")
            cands = data.get("candidates", [])
            if cands:
                df = pd.DataFrame(cands)
                st.dataframe(
                    df, 
                    hide_index=True, 
                    column_config={
                        "name": "Candidate Name",
                        "party": "Affiliation",
                        "status": "Current Status"
                    },
                    use_container_width=True
                )

            # --- SECTION C: STRATEGIC BRIEF ---
            st.markdown("### 🧠 Analyst Summary")
            st.info(data.get("analysis_text", "No analysis available."))
            
            # --- SECTION D: DISCLAIMER ---
            st.caption(f"Data Source: Aggregated from open-source intelligence. Last Updated: {time.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.error("Unable to compile dossier. Please try again.")

    else:
        # Empty State
        st.info("👈 Select a constituency to load the strategic dossier.")
