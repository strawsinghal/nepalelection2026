import streamlit as st
from google import genai
from google.genai import types

# 1. Setup the High-Speed Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Nepal 2026 War Room", layout="wide")

# 2. Professional Sidebar Navigation
st.sidebar.title("🗳️ Constituency Navigator")

# Data organization by Province (All 165)
provinces = {
    "Koshi (28)": ["Jhapa 5", "Morang 6", "Sunsari 1", "Jhapa 3", "Ilam 2"],
    "Madhesh (32)": ["Sarlahi 4", "Dhanusha 3", "Saptari 2", "Parsa 1"],
    "Bagmati (33)": ["Kathmandu 1", "Kathmandu 4", "Chitwan 2", "Chitwan 3", "Lalitpur 3"],
    "Gandaki (18)": ["Gorkha 2", "Kaski 2", "Tanahun 1"],
    "Lumbini (26)": ["Rupandehi 2", "Dang 2", "Banke 2"],
    "Karnali (12)": ["Surkhet 2", "Jumla 1"],
    "Sudurpashchim (16)": ["Kailali 5", "Kanchanpur 2"]
}

selected_province = st.sidebar.selectbox("Select Province", list(provinces.keys()))
selected_constituency = st.sidebar.selectbox("Select Seat", provinces[selected_province])

# 3. Top 10 High-Stakes Battles (Pinned on Left)
st.sidebar.markdown("---")
st.sidebar.subheader("🔥 Top 10 Titan Battles")
top_10 = {
    "Jhapa 5": "Balen Shah vs. KP Oli",
    "Sarlahi 4": "Gagan Thapa vs. Amresh Singh",
    "Chitwan 2": "Rabi Lamichhane vs. NC/UML Alliance",
    "Gorkha 2": "Prachanda vs. Madhav Devkota",
    "Sunsari 1": "Harka Sampang vs. Major Parties",
    "Jhapa 3": "Rajendra Lingden vs. Krishna Sitaula",
    "Chitwan 3": "Sobita Gautam vs. Renu Dahal",
    "Tanahun 1": "Swarnim Wagle vs. NC Candidate",
    "Kathmandu 1": "Pukar Bam vs. Prakash Man Singh",
    "Kathmandu 4": "Dr. Toshima Karki vs. Nain Singh Mahar"
}
battle_pick = st.sidebar.radio("Quick View Battle:", list(top_10.keys()))

# 4. Standardized War Room Intelligence Logic
@st.cache_data(ttl=600)
def get_war_room_report(constituency):
    prompt = f"""
    Act as a 2026 Election Intelligence Officer. 
    Analyze {constituency}, Nepal for the March 5 election. 
    FACTS TO INCLUDE:
    - Balen/Rabi PM candidacy impact.
    - Jan 20, 2026 nomination data (3,406 total candidates nationwide).
    - Gen Z sentiment (52% of voters are 18-40).
    
    FORMAT: Use tables for stats and bold headers for ground analysis.
    """
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
        config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
    )
    return response.text

# 5. Main Display
col_info, col_battle = st.columns([1, 1])

with col_info:
    st.header(f"📊 Report: {selected_constituency}")
    if st.button(f"Analyze {selected_constituency}"):
        st.markdown(get_war_room_report(selected_constituency))

with col_battle:
    st.header(f"🥊 Battle: {battle_pick}")
    if st.button(f"Show {battle_pick} Duel"):
        st.markdown(get_war_room_report(battle_pick))
