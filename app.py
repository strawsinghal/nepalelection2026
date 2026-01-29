import streamlit as st
import datetime
from google import genai
from google.genai import types

# 1. Setup Models & Client
DEEP_MODEL = "gemini-3-pro-preview" 
FAST_MODEL = "gemini-3-flash-preview"

# Initialize Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Nepal 2026: 165 Seat Predictor", layout="wide")

# 2. LIVE NEWS TICKER (January 29, 2026)
ticker_news = [
    "🚨 NEWS: 150,000 election police to be deployed starting Feb 10.",
    "🥊 BATTLE: Tensions high in Jhapa-5 as Balen vs Oli duel enters final phase.",
    "📋 FINALIZED: 3,406 total candidates confirmed for 165 FPTP seats.",
    "✈️ LOGISTICS: Helicopters readied for voting in snowbound districts.",
    "⚖️ COMPLIANCE: Election Code of Conduct strictly enforced since Jan 19."
]

st.markdown(
    f"""
    <div style="background-color: #ff4b4b; color: white; padding: 10px; border-radius: 5px; overflow: hidden; margin-bottom: 20px;">
        <marquee behavior="scroll" direction="left" scrollamount="8">
            {' &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; '.join(ticker_news)}
        </marquee>
    </div>
    """, 
    unsafe_allow_html=True
)

st.title("🇳🇵 Nepal Election 2026: 165 Constituency Intelligence")

# 3. Data Organization (All 165 Seats)
constituency_data = {
    "Koshi (28)": ["Taplejung 1", "Panchthar 1", "Ilam 1", "Ilam 2", "Jhapa 1", "Jhapa 2", "Jhapa 3", "Jhapa 4", "Jhapa 5", "Sankhuwasabha 1", "Tehrathum 1", "Bhojpur 1", "Dhankuta 1", "Morang 1", "Morang 2", "Morang 3", "Morang 4", "Morang 5", "Morang 6", "Sunsari 1", "Sunsari 2", "Sunsari 3", "Sunsari 4", "Solukhumbu 1", "Khotang 1", "Okhaldhunga 1", "Udayapur 1", "Udayapur 2"],
    "Madhesh (32)": ["Saptari 1", "Saptari 2", "Saptari 3", "Saptari 4", "Siraha 1", "Siraha 2", "Siraha 3", "Siraha 4", "Dhanusha 1", "Dhanusha 2", "Dhanusha 3", "Dhanusha 4", "Mahottari 1", "Mahottari 2", "Mahottari 3", "Mahottari 4", "Sarlahi 1", "Sarlahi 2", "Sarlahi 3", "Sarlahi 4", "Rautahat 1", "Rautahat 2", "Rautahat 3", "Rautahat 4", "Bara 1", "Bara 2", "Bara 3", "Bara 4", "Parsa 1", "Parsa 2", "Parsa 3", "Parsa 4"],
    "Bagmati (33)": ["Dolakha 1", "Ramechhap 1", "Sindhuli 1", "Sindhuli 2", "Rasuwa 1", "Dhading 1", "Dhading 2", "Nuwakot 1", "Nuwakot 2", "Kathmandu 1", "Kathmandu 2", "Kathmandu 3", "Kathmandu 4", "Kathmandu 5", "Kathmandu 6", "Kathmandu 7", "Kathmandu 8", "Kathmandu 9", "Kathmandu 10", "Bhaktapur 1", "Bhaktapur 2", "Lalitpur 1", "Lalitpur 2", "Lalitpur 3", "Kavrepalanchok 1", "Kavrepalanchok 2", "Sindhupalchok 1", "Sindhupalchok 2", "Makwanpur 1", "Makwanpur 2", "Chitwan 1", "Chitwan 2", "Chitwan 3"],
    "Gandaki (18)": ["Gorkha 1", "Gorkha 2", "Manang 1", "Lamjung 1", "Kaski 1", "Kaski 2", "Kaski 3", "Tanahun 1", "Tanahun 2", "Syangja 1", "Syangja 2", "Nawalparasi East 1", "Nawalparasi East 2", "Mustang 1", "Myagdi 1", "Baglung 1", "Baglung 2", "Parbat 1"],
    "Lumbini (26)": ["Gulmi 1", "Gulmi 2", "Palpa 1", "Palpa 2", "Arghakhanchi 1", "Nawalparasi West 1", "Nawalparasi West 2", "Rupandehi 1", "Rupandehi 2", "Rupandehi 3", "Rupandehi 4", "Rupandehi 5", "Kapilvastu 1", "Kapilvastu 2", "Kapilvastu 3", "Dang 1", "Dang 2", "Dang 3", "Banke 1", "Banke 2", "Banke 3", "Bardiya 1", "Bardiya 2", "Rukum East 1", "Rolpa 1", "Pyuthan 1"],
    "Karnali (12)": ["Rukum West 1", "Salyan 1", "Dolpa 1", "Mugu 1", "Jumla 1", "Kalikot 1", "Humla 1", "Jajarkot 1", "Dailekh 1", "Dailekh 2", "Surkhet 1", "Surkhet 2"],
    "Sudurpashchim (16)": ["Bajura 1", "Bajhang 1", "Achham 1", "Achham 2", "Doti 1", "Kailali 1", "Kailali 2", "Kailali 3", "Kailali 4", "Kailali 5", "Kanchanpur 1", "Kanchanpur 2", "Kanchanpur 3", "Dadeldhura 1", "Baitadi 1", "Darchula 1"]
}

# 4. The 24-Hour Cache Logic Function
@st.cache_data(ttl="1d", show_spinner=False)
def get_daily_deep_intel(constituency_name):
    """
    Runs DEEP research using Gemini 3 Pro once every 24 hours.
    Subsequent calls for the same constituency return the cached result instantly.
    """
    prompt = f"""
    Perform a professional political deep dive for {constituency_name}, Nepal (March 5, 2026 Election).
    1. Identify major candidates using Jan 20, 2026 nomination data.
    2. Analyze the 'Gen Z' and 'Balen-Rabi Alliance' impact.
    3. Predict the winner probability based on ground sentiment.
    """
    
    # Use Gemini 3 Pro for the Seed Research
    # Removed 'thinking_level' to fix ValidationError
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

# 5. Multipage Structure UI
col_sidebar, col_main, col_stats = st.columns([1, 2, 1], gap="large")

with col_sidebar:
    st.subheader("📁 Navigation")
    prov = st.selectbox("1. Province Filter", list(constituency_data.keys()))
    seat = st.selectbox("2. Target Seat", constituency_data[prov])
    
    st.markdown("---")
    # NEW VOTER SURGE
    st.metric("New Voters (2026 Surge)", "915,119", delta="5.09% increase")
    st.caption("Total: 18,903,689 voters registered.")

with col_main:
    st.subheader(f"📊 Detailed Report: {seat}")
    if st.button(f"Search {seat}"):
        with st.spinner(f"Accessing Verified Jan 2026 Data for {seat}..."):
            # Call the cached function
            data = get_daily_deep_intel(seat)
            
            # Display Timestamp to show cache age
            st.caption(f"⚡ Data Refreshed: {data['timestamp']} (Valid for 24h)")
            st.markdown(data['text'])

with col_stats:
    st.subheader("📈 Quick Pulse")
    st.markdown("""
    * **Candidates:** 3,406
    * **Youth Voters:** 52% (18-40)
    * **Centers:** 23,112 centres
    * **Status:** 35 days remaining
    """)
    st.info("Election Day: March 5, 2026")
