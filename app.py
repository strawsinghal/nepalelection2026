import streamlit as st
import sqlite3
import hashlib
import time
import json
import pandas as pd
from google import genai
from google.genai import types

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="NECC: Official Election Dashboard",
    page_icon="🇳🇵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; color: #212529; font-family: 'Inter', sans-serif; }
    h1 { color: #0f172a; font-weight: 700; letter-spacing: -0.5px; }
    .auth-box { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); max-width: 450px; margin: auto; }
    .stButton>button { background-color: #0f172a; color: white; border-radius: 6px; font-weight: 600; border: none; }
    .stButton>button:hover { background-color: #334155; }
    div[data-testid="stMetric"] { background-color: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE ENGINE (SQLite) ---
# This runs locally. No external setup required.

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Create table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT,
            approved INTEGER,
            mobile TEXT,
            email TEXT
        )
    ''')
    # Create Default Admin if not exists (admin / admin123)
    c.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not c.fetchone():
        # Hash password for security
        pwd_hash = hashlib.sha256("admin123".encode()).hexdigest() 
        c.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)', 
                  ('admin', pwd_hash, 'admin', 1, '0000000000', 'admin@necc.gov.np'))
    conn.commit()
    conn.close()

def register_user(username, password, email, mobile):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)', 
                  (username, pwd_hash, 'user', 0, mobile, email)) # 0 = Not Approved
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_login(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute('SELECT role, approved FROM users WHERE username = ? AND password = ?', (username, pwd_hash))
    result = c.fetchone()
    conn.close()
    return result # Returns (role, approved) or None

def get_pending_users():
    conn = sqlite3.connect('users.db')
    df = pd.read_sql_query("SELECT username, email, mobile FROM users WHERE approved = 0", conn)
    conn.close()
    return df

def approve_user(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('UPDATE users SET approved = 1 WHERE username = ?', (username,))
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# --- 3. CORE AI ENGINE (From your best version) ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("System Error: API Configuration Missing.")
        st.stop()
except:
    st.error("System Error: Connection Failed.")
    st.stop()

@st.cache_data(ttl=3600, show_spinner=False)
def get_election_research(constituency_name):
    prompt = f"""
    Act as a Senior Election Analyst for Nepal (Jan 29, 2026 Context).
    Target: {constituency_name}
    
    TASK:
    1. SEARCH for the latest confirmed candidate list (Jan 2026 nominations).
    2. CHECK: Has the incumbent withdrawn?
    3. CHECK: Are there high-profile challengers (Balen/RSP)?
    
    OUTPUT JSON ONLY:
    {{
        "candidates": [
            {{"name": "Name", "party": "Party", "status": "Incumbent/Challenger"}}
        ],
        "prediction": {{
            "winner": "Name",
            "probability": "XX",
            "margin": "XX Votes"
        }},
        "analysis": "Short strategic summary."
    }}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp", # Using Flash for speed + tools
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except:
        return None

# --- 4. AUTHENTICATION LOGIC ---
if "user" not in st.session_state:
    st.session_state.user = None

def main_app():
    # --- ADMIN SIDEBAR ---
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Flag_of_Nepal.svg/1200px-Flag_of_Nepal.svg.png", width=40)
        st.markdown(f"**User:** {st.session_state.user['name']}")
        st.markdown(f"**Role:** {st.session_state.user['role'].upper()}")
        
        # ADMIN PANEL
        if st.session_state.user['role'] == 'admin':
            st.markdown("---")
            st.markdown("### 🛡️ Admin Panel")
            pending_df = get_pending_users()
            if not pending_df.empty:
                st.warning(f"{len(pending_df)} Pending Approvals")
                for index, row in pending_df.iterrows():
                    c1, c2 = st.columns([3, 1])
                    c1.text(f"{row['username']} ({row['mobile']})")
                    if c2.button("Approve", key=row['username']):
                        approve_user(row['username'])
                        st.rerun()
            else:
                st.success("No pending users.")
        
        st.markdown("---")
        if st.button("Log Out"):
            st.session_state.user = None
            st.rerun()

    # --- MAIN DASHBOARD CONTENT ---
    st.title("🗳️ NECC: Election Intelligence")
    st.markdown("Authorized Access Only • Live Strategy Terminal")
    st.markdown("---")

    # The Election Logic
    constituency_data = {
        "Koshi": ["Taplejung 1", "Jhapa 1", "Jhapa 5", "Ilam 2", "Morang 6"],
        "Madhesh": ["Saptari 2", "Rautahat 1", "Sarlahi 4", "Dhanusha 3"],
        "Bagmati": ["Kathmandu 4", "Kathmandu 5", "Chitwan 2", "Lalitpur 3"],
        "Gandaki": ["Gorkha 2", "Tanahun 1", "Kaski 2"],
        "Lumbini": ["Rupandehi 2", "Dang 2", "Banke 2"],
        "Karnali": ["Surkhet 1"],
        "Sudurpashchim": ["Dadeldhura 1"]
    }

    c1, c2, c3 = st.columns([2,2,1])
    prov = c1.selectbox("Province", list(constituency_data.keys()))
    seat = c2.selectbox("Constituency", constituency_data[prov])
    run = c3.button("Run Deep Scan", type="primary", use_container_width=True)

    if run:
        with st.status("📡 Establishing Secure Uplink...", expanded=True):
            st.write("🔍 Verifying Candidate Lists...")
            data = get_election_research(seat)
            st.write("✅ Intelligence Acquired.")

        if data:
            st.markdown("### 🎯 Projected Outcome")
            m1, m2, m3 = st.columns(3)
            pred = data.get("prediction", {})
            m1.metric("Winner", pred.get("winner", "Unknown"))
            m2.metric("Probability", f"{pred.get('probability', '0')}%")
            m3.metric("Margin", pred.get("margin", "N/A"))

            st.markdown("### 📋 Candidate Ledger")
            df = pd.DataFrame(data.get("candidates", []))
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.info(f"**Analyst Note:** {data.get('analysis', 'No data')}")

# --- 5. LOGIN SCREEN (The "Socially Accepted" Face) ---
if st.session_state.user is None:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        # Tabbed Interface
        tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Request Access"])
        
        with tab1:
            st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
            st.subheader("NECC Portal Login")
            l_user = st.text_input("Username", key="l_user")
            l_pass = st.text_input("Password", type="password", key="l_pass")
            
            if st.button("Access Dashboard", use_container_width=True):
                result = verify_login(l_user, l_pass)
                if result:
                    role, approved = result
                    if approved:
                        st.session_state.user = {'name': l_user, 'role': role}
                        st.rerun()
                    else:
                        st.warning("⚠️ Account created but pending Admin Approval. Please check back later.")
                else:
                    st.error("⛔ Invalid Credentials")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
            st.subheader("New Analyst Registration")
            r_user = st.text_input("Choose Username", key="r_user")
            r_email = st.text_input("Official Email", key="r_email")
            r_mobile = st.text_input("Mobile Number", key="r_mobile")
            r_pass = st.text_input("Set Password", type="password", key="r_pass")
            
            if st.button("Submit Registration", use_container_width=True):
                if r_user and r_pass:
                    if register_user(r_user, r_pass, r_email, r_mobile):
                        st.success("✅ Registration Successful! Your account is pending Admin approval.")
                    else:
                        st.error("Username already taken.")
                else:
                    st.error("Please fill all fields.")
            st.markdown("</div>", unsafe_allow_html=True)

else:
    main_app()
