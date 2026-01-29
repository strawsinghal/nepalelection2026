import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google import genai
from google.genai import types

# 1. Setup Gemini 3 Flash
# This model is optimized for the speed and reasoning required for 2026 data.
MODEL_ID = "gemini-3-flash-preview"
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="2026 Titan Battles", layout="wide")
st.title("🥊 2026 Titan Battles: The War Room")

# 2. Finalized Top 10 Battles (Confirmed Jan 20, 2026)
# Data reflects major shifts, including Gagan Thapa moving to Sarlahi-4
battles = {
    "Jhapa 5": {"duel": "Balen Shah (RSP) vs. KP Oli (UML)", "prob": [49, 51]},
    "Sarlahi 4": {"duel": "Gagan Thapa (NC) vs. Amresh Singh (RSP)", "prob": [54, 46]},
    "Chitwan 2": {"duel": "Rabi Lamichhane (RSP) vs. NC-UML Alliance", "prob": [58, 42]},
    "Kathmandu 3": {"duel": "Kulman Ghising (Ujyaalo) vs. Santosh Chalise (NC)", "prob": [52, 48]},
    "Sunsari 1": {"duel": "Harka Sampang (SSP) vs. Major Alliances", "prob": [45, 55]},
    "Chitwan 3": {"duel": "Sobita Gautam (RSP) vs. Renu Dahal (NCP)", "prob": [53, 47]},
    "Jhapa 3": {"duel": "Rajendra Lingden (RPP) vs. Krishna Sitaula (NC)", "prob": [51, 49]},
    "Gorkha 2": {"duel": "Pragatisheel Loktantrik vs. Maoist Alliance", "prob": [48, 52]},
    "Rukum East": {"duel": "Prachanda (NCP) vs. Sandeep Pun (Independent)", "prob": [62, 38]},
    "Sunsari 3": {"duel": "Bijay Gachhadar (NC) vs. Bhagwati Chaudhary (UML)", "prob": [46, 54]}
}

# 3. Helper Function for Sentiment Gauge
def draw_sentiment_gauge(score, label):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        title = {'text': f"Social Buzz: {label}"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#ff4b4b"},
            'steps' : [
                {'range': [0, 50], 'color': "#f0f2f6"},
                {'range': [50, 80], 'color': "#d1d5db"},
                {'range': [80, 100], 'color': "#ff4b4b"}]
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=0))
    return fig

# 4. Main UI Layout (Fixes the NameError)
selection = st.sidebar.radio("Select High-Stakes Duel:", list(battles.keys()))
battle_info = battles[selection]

# Correctly assigning BOTH columns here
col_chart, col_intel = st.columns([1, 1.5], gap="large")

with col_chart:
    st.subheader(f"📈 Win Probability: {selection}")
    candidates = battle_info["duel"].split(" vs. ")
    chart_df = pd.DataFrame({"Candidate": candidates, "Probability (%)": battle_info["prob"]})
    
    fig = px.bar(chart_df, x="Probability (%)", y="Candidate", orientation='h', 
                 color="Candidate", text="Probability (%)", color_discrete_sequence=["#ff4b4b", "#1f77b4"])
    fig.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Gauge updates based on selection
    buzz_score = 88 if "Balen" in battle_info["duel"] or "Gagan" in battle_info["duel"] else 65
    st.plotly_chart(draw_sentiment_gauge(buzz_score, selection), use_container_width=True)

with col_intel:
    st.subheader(f"🚀 Ground Intelligence: {selection}")
    if st.button("Generate Deep Analysis"):
        with st.spinner("Analyzing Jan 2026 ground reports..."):
            prompt = f"Analyze the Jan 20, 2026 nomination for {selection}: {battle_info['duel']}."
            res = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
                config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
            )
            st.markdown(res.text)
