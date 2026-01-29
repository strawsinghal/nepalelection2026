import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Top 10 Battles", layout="wide")
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("🥊 High-Stakes Titan Battles")

battles = {
    "Jhapa 5": "Balen Shah vs. KP Oli",
    "Sarlahi 4": "Gagan Thapa vs. Amresh Singh",
    "Chitwan 2": "Rabi Lamichhane vs. NC/UML",
}

selection = st.radio("Select a Battle to Analyze:", list(battles.keys()))
st.subheader(f"Battle: {battles[selection]}")

if st.button("🚀 Analyze Duel"):
    with st.spinner("Fetching 2026 battle data..."):
        res = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=f"Deep dive: {battles[selection]} in {selection} for Nepal 2026 election.",
            config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
        )
        st.markdown(res.text)
