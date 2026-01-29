import streamlit as st
from google import genai
from google.genai import types

# 1. Setup Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Nepal 2026 War Room", layout="wide")

# Top 10 High-Stakes Battles Data (Jan 2026)
battles = {
    "Jhapa 5": "Balen Shah vs. KP Oli",
    "Sarlahi 4": "Gagan Thapa vs. Amresh Singh",
    "Chitwan 2": "Rabi Lamichhane vs. NC/UML",
    "Gorkha 2": "Prachanda vs. Madhav Devkota",
    "Sunsari 1": "Harka Sampang vs. Major Parties",
    "Jhapa 3": "Rajendra Lingden vs. NC",
    "Chitwan 3": "Sobita Gautam vs. Renu Dahal",
    "Tanahun 1": "Swarnim Wagle vs. Govinda Bhattarai",
    "Kathmandu 1": "Pukar Bam vs. Prakash Man Singh",
    "Kathmandu 4": "Dr. Toshima Karki vs. Nain Singh Mahar"
}

# Standardized Research Function
@st.cache_data(ttl=600)
def get_report(constituency, battle_name, detail_level="summary"):
    prompt = f"Analyze {constituency} ({battle_name}) for March 5, 2026. Detail level: {detail_level}."
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
        config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
    )
    return response.text

# --- 3-COLUMN LAYOUT ---
col_left, col_center, col_right = st.columns([1, 2, 1], gap="large")

# LEFT COLUMN: Top 10 Battle List & Summary
with col_left:
    st.subheader("🔥 Top 10 Battles")
    battle_selection = st.radio("Select to see summary:", list(battles.keys()), label_visibility="collapsed")
    
    st.markdown(f"**{battle_selection}**")
    st.caption(battles[battle_selection])
    
    # Summary Result within the left side
    summary = get_report(battle_selection, battles[battle_selection], "summary")
    st.write(summary[:250] + "...") # Show short summary
    
    if st.button("🔍 See More (Move to Center)"):
        st.session_state.center_view = battle_selection

# CENTER COLUMN: The Main Predictor & Deep Results
with col_center:
    st.subheader("🎯 Election Predictor")
    
    # Constituency Dropdown
    all_constituencies = ["Kathmandu 4", "Kaski 2", "Jhapa 5", "Sarlahi 4"] # Simplified list
    target = st.selectbox("Choose a constituency to predict:", all_constituencies)
    
    if st.button(f"Analyze {target}") or 'center_view' in st.session_state:
        # If 'See More' was clicked on left, override center target
        display_target = st.session_state.get('center_view', target)
        with st.spinner(f"Analyzing {display_target}..."):
            full_report = get_report(display_target, battles.get(display_target, ""), "full")
            st.markdown(full_report)

# RIGHT COLUMN: Auto-Populating Battle Results
with col_right:
    st.subheader("📈 Live Battle Stats")
    # This automatically updates whenever the 'battle_selection' on the left changes
    with st.container(border=True):
        st.write(f"**Live Pulse: {battle_selection}**")
        st.metric("Voter Interest", "High", delta="7% Jan 2026")
        st.write(get_report(battle_selection, battles[battle_selection], "metrics"))
