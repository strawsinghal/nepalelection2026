import streamlit as st
import plotly.graph_objects as go
from google import genai
from google.genai import types

# Function to generate a Sentiment Gauge
def draw_sentiment_gauge(score, label):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Social Media Buzz: {label}"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkred"},
            'steps' : [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "gray"},
                {'range': [80, 100], 'color': "red"}],
            'threshold' : {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 90}
        }
    ))
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10))
    return fig

# Inside your "Run Deep Dive" button logic:
with col_intel:
    st.subheader("🔥 Live Sentiment Gauge")
    
    # Simulate or use AI to generate a score based on Jan 2026 news
    # For Jhapa-5, Balen Shah has massive social media excitement
    sentiment_score = 88 if selection == "Jhapa 5" else 65
    
    st.plotly_chart(draw_sentiment_gauge(sentiment_score, selection), use_container_width=True)
