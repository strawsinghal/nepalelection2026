import streamlit as st
import datetime
import time
from google import genai
from google.genai import types

# 1. Setup Models
# PRO: Runs once every 24h per seat for deep reasoning
DEEP_MODEL = "gemini-3-pro-preview" 
# FLASH: Runs instantly for immediate user feedback
FAST_MODEL = "gemini-3-flash-preview"

# Initialize Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Nepal 2026: 165 Seat Predictor", layout="wide")

# --- CACHING LOGIC ---

# TIER 1: FAST INTEL (Short Cache)
# This gives the "Instant" result while deep research happens
@st.cache_data(ttl="1h", show_spinner=False)
def get_fast_intel(constituency_name):
    prompt = f"""
    Give me a quick 3-bullet summary for {constituency_name} (Nepal 2026 Election).
    Focus on: Winner prediction and key rival. Keep it under 100 words.
    """
    response = client.models.generate_content(
        model=FAST_MODEL,
        contents=prompt
    )
    return f"⚡ **Quick Flash Analysis:**\n\n{response.text}"

# TIER 2: DEEP INTEL (24-Hour Cache)
# This is the "Gold Standard" report that stays for 1 day
@st.cache_data(ttl="1d", show_spinner=False)
def get_daily_deep_intel(constituency_name):
    """
    Runs DEEP research using Gemini 3 Pro.
    Cached for 24 hours.
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
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# --- UI LAYOUT ---

# News Ticker
ticker_news = [
    "🚨 NEWS: 150,000 election police to be deployed starting Feb 10.",
    "🥊 BATTLE: Tensions high in Jhapa-5 as Balen vs Oli duel enters final phase.",
    "📋 FINALIZED: 3,406 total candidates confirmed for 165 FPTP seats.",
    "✈️ LOGISTICS: Helicopters readied for voting in snowbound districts."
]
st.markdown(f"""<div style="background-color: #ff4b4b; color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px;"><marquee>{' | '.join(ticker_news)}</marquee></div>""", unsafe_allow_html=True)

st.title("🇳🇵 Nepal Election 2026: Intelligence Hub")

# Data Dictionary
constituency_data = {
    "Koshi (28)": ["Jhapa 5", "Jhapa 3", "Morang 6", "Sunsari 1", "Ilam 2"],
    "Madhesh (32)": ["Sarlahi 4", "Rautahat 1", "Dhanusha 3", "Saptari 2"],
    "Bagmati (33)": ["Kathmandu 4", "Chitwan 2", "Chitwan 3", "Lalitpur 3"],
    "Gandaki (18)": ["Gorkha 2", "Kaski 2", "Tanahun 1"],
    "Lumbini (26)": ["Rupandehi 2", "Dang 2", "Banke 2"],
    "Karnali (12)": ["Surkhet 2", "Jumla 1"],
    "Sudurpashchim (16)": ["Kailali 5", "Dadeldhura 1"]
}

col_sidebar, col_main = st.columns([1, 3], gap="large")

with col_sidebar:
    st.subheader("📁 Navigation")
    prov = st.selectbox("1. Province", list(constituency_data.keys()))
    seat = st.selectbox("2. Constituency", constituency_data[prov])
    
    st.markdown("---")
    st.warning("🔄 **Daily Background Sync**")
    st.caption("Run this once a day to pre-load deep research for all key seats.")
    if st.button("Run 24h Batch Update"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        # Batch update loop
        seats_to_update = constituency_data[prov] # Updates current province to save time
        for i, s in enumerate(seats_to_update):
            status_text.text(f"Deep Researching: {s}...")
            # This triggers the cache function without displaying it
            get_daily_deep_intel(s) 
            progress_bar.progress((i + 1) / len(seats_to_update))
        status_text.success("✅ Daily Intelligence Cache Updated!")

with col_main:
    st.subheader(f"📊 Intelligence Report: {seat}")
    
    # THE "FAST ASAP" LOGIC
    if st.button(f"🚀 Analyze {seat}"):
        report_placeholder = st.empty()
        
        # STEP 1: Show Fast Result IMMEDIATELY
        with st.spinner("Fetching Flash Intel..."):
            fast_res = get_fast_intel(seat)
            # Display fast result instantly
            report_placeholder.markdown(f"""
            <div style="border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f0f2f6;">
                {fast_res}
            </div>
            """, unsafe_allow_html=True)
        
        # STEP 2: Check/Run Deep Research in Background
        # The user is reading the Fast result while this runs
        with st.spinner("Verifying with Deep Research (Gemini Pro)..."):
            # This will finish instantly if cached ( < 24h), or take 10s if new
            deep_data = get_daily_deep_intel(seat)
            
            # STEP 3: Overwrite with Deep Result once ready
            report_placeholder.markdown(f"""
            <div style="border-left: 5px solid #ff4b4b; padding: 15px; background-color: #ffffff;">
                <small style="color: grey;">⚡ Verified Deep Report • Refreshed: {deep_data['timestamp']}</small>
                <br><br>
                {deep_data['text']}
            </div>
            """, unsafe_allow_html=True)
            
            st.success("Analysis upgraded to Deep Research.")
