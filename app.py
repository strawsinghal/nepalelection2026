import streamlit as st
from google import genai
from google.genai import types

# Initialize the Gemini 2.0 Client (Recommended for Grounding)
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="165 Seat Predictor", layout="wide")

st.title("🇳🇵 165 Constituency Intelligence Predictor")
st.markdown("---")

# 1. Selection Logic for all 165 Constituencies
provinces = {
    "Koshi (28)": ["Jhapa 5", "Morang 6", "Sunsari 1", "Jhapa 3", "Ilam 2"],
    "Madhesh (32)": ["Sarlahi 4", "Dhanusha 3", "Saptari 2", "Parsa 1"],
    "Bagmati (33)": ["Kathmandu 1", "Kathmandu 4", "Chitwan 2", "Chitwan 3", "Lalitpur 3"],
    "Gandaki (18)": ["Gorkha 2", "Kaski 2", "Tanahun 1"],
    "Lumbini (26)": ["Rupandehi 2", "Dang 2", "Banke 2"],
    "Karnali (12)": ["Surkhet 2", "Jumla 1"],
    "Sudurpashchim (16)": ["Kailali 5", "Kanchanpur 2"]
}

col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    prov = st.selectbox("1. Filter by Province", list(provinces.keys()))
with col_nav2:
    seat = st.selectbox("2. Select Target Seat", provinces[prov])

# 2. Research Engine with 2026 Grounding
@st.cache_data(ttl=600) # Caches results for 10 mins to save API quota
def get_detailed_report(constituency_name):
    # This prompt forces the AI to check Jan 2026 data specifically
    prompt = f"""
    Analyze the {constituency_name} constituency for the March 5, 2026 Nepal Election. 
    1. Identify all major candidates filed on Jan 20, 2026.
    2. Analyze the impact of Gagan Thapa's move to Sarlahi 4 or Balen Shah's PM projection.
    3. Predict the current 'Youth Wave' (Gen
