import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Election Pulse", layout="wide")

st.title("📊 Live National Election Pulse")
st.info("Aggregated National Trends for March 5, 2026.")

# Simulated Live Data based on Jan 2026 Trends
data = pd.DataFrame({
    "Party": ["Nepali Congress", "RSP (Balen/Rabi)", "CPN-UML", "Maoist Centre"],
    "Estimated Seats": [88, 72, 65, 35]
})

fig = px.bar(data, x="Party", y="Estimated Seats", color="Party", title="National Seat Projections")
st.plotly_chart(fig, use_container_width=True)

st.subheader("🔥 Ground Sentiment Trends")
st.markdown("""
* **Youth Wave:** 52% of voters are Gen Z/Millennials.
* **The Balen Effect:** High impact in urban corridors.
* **Alliance Impact:** NC-UML upper house sweep impact.
""")
