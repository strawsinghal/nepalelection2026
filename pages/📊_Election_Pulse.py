import streamlit as st
from google import genai
from google.genai import types

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("📊 2026 Social Media Sentiment Pulse")
st.markdown("---")

# 1. Targeted Keywords for 2026
keywords = ["#BalenForPM", "#NoNotAgain", "#RabiAlliance", "#GenZNepal", "#March5Revolution"]

# 2. Sentiment Scraping Logic
@st.cache_data(ttl=1800) # Refresh every 30 minutes
def scrape_social_sentiment(keyword_list):
    # This prompt forces the AI to look at LIVE social trends from Jan 2026
    prompt = f"""
    Analyze current social media sentiment (TikTok, Twitter, Facebook) in Nepal as of late Jan 2026.
    Focus on these specific keywords: {keyword_list}.
    
    REQUIRED FORMAT:
    1. TRENDING TOPIC: (e.g., Balen-Rabi Alliance momentum)
    2. SENTIMENT SCORE: (Positive/Negative/Neutral %)
    3. TOP GEN Z NARRATIVE: (What is the youth saying about traditional parties vs alternative?)
    4. ANOMALY DETECTOR: (Identify any sudden shifts in mood since Jan 20 nominations)
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    return response.text

# 3. Display Interface
st.subheader("🔥 Live Sentiment Tracker")
if st.button("🔍 Scrape Live 2026 Trends"):
    with st.spinner("Analyzing TikTok and Twitter data clusters..."):
        pulse_report = scrape_social_sentiment(keywords)
        st.markdown(pulse_report)
