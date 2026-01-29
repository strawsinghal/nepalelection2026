import streamlit as st
from google import genai
from google.genai import types

# 1. Setup Client with your key (using the high-performance 2.0 Flash for grounding)
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
MODEL_ID = "gemini-2.0-pro" 

st.set_page_config(page_title="Nepal 2026 War Room", layout="wide")
st.title("🇳🇵 Nepal Election 2026: 165 Constituency Intelligence")
st.sidebar.info("Data verified: January 29, 2026. Nominations finalized Jan 23.")

# 2. Complete 165 Constituency Data
constituency_data = {
    "Koshi (28)": ["Taplejung 1", "Panchthar 1", "Ilam 1", "Ilam 2", "Jhapa 1", "Jhapa 2", "Jhapa 3", "Jhapa 4", "Jhapa 5", "Sankhuwasabha 1", "Tehrathum 1", "Bhojpur 1", "Dhankuta 1", "Morang 1", "Morang 2", "Morang 3", "Morang 4", "Morang 5", "Morang 6", "Sunsari 1", "Sunsari 2", "Sunsari 3", "Sunsari 4", "Solukhumbu 1", "Khotang 1", "Okhaldhunga 1", "Udayapur 1", "Udayapur 2"],
    "Madhesh (32)": ["Saptari 1", "Saptari 2", "Saptari 3", "Saptari 4", "Siraha 1", "Siraha 2", "Siraha 3", "Siraha 4", "Dhanusha 1", "Dhanusha 2", "Dhanusha 3", "Dhanusha 4", "Mahottari 1", "Mahottari 2", "Mahottari 3", "Mahottari 4", "Sarlahi 1", "Sarlahi 2", "Sarlahi 3", "Sarlahi 4", "Rautahat 1", "Rautahat 2", "Rautahat 3", "Rautahat 4", "Bara 1", "Bara 2", "Bara 3", "Bara 4", "Parsa 1", "Parsa 2", "Parsa 3", "Parsa 4"],
    "Bagmati (33)": ["Dolakha 1", "Ramechhap 1", "Sindhuli 1", "Sindhuli 2", "Rasuwa 1", "Dhading 1", "Dhading 2", "Nuwakot 1", "Nuwakot 2", "Kathmandu 1", "Kathmandu 2", "Kathmandu 3", "Kathmandu 4", "Kathmandu 5", "Kathmandu 6", "Kathmandu 7", "Kathmandu 8", "Kathmandu 9", "Kathmandu 10", "Bhaktapur 1", "Bhaktapur 2", "Lalitpur 1", "Lalitpur 2", "Lalitpur 3", "Kavrepalanchok 1", "Kavrepalanchok 2", "Sindhupalchok 1", "Sindhupalchok 2", "Makwanpur 1", "Makwanpur 2", "Chitwan 1", "Chitwan 2", "Chitwan 3"],
    "Gandaki (18)": ["Gorkha 1", "Gorkha 2", "Manang 1", "Lamjung 1", "Kaski 1", "Kaski 2", "Kaski 3", "Tanahun 1", "Tanahun 2", "Syangja 1", "Syangja 2", "Nawalparasi East 1", "Nawalparasi East 2", "Mustang 1", "Myagdi 1", "Baglung 1", "Baglung 2", "Parbat 1"],
    "Lumbini (26)": ["Gulmi 1", "Gulmi 2", "Palpa 1", "Palpa 2", "Arghakhanchi 1", "Nawalparasi West 1", "Nawalparasi West 2", "Rupandehi 1", "Rupandehi 2", "Rupandehi 3", "Rupandehi 4", "Rupandehi 5", "Kapilvastu 1", "Kapilvastu 2", "Kapilvastu 3", "Dang 1", "Dang 2", "Dang 3", "Banke 1", "Banke 2", "Banke 3", "Bardiya 1", "Bardiya 2", "Rukum East 1", "Rolpa 1", "Pyuthan 1"],
    "Karnali (12)": ["Rukum West 1", "Salyan 1", "Dolpa 1", "Mugu 1", "Jumla 1", "Kalikot 1", "Humla 1", "Jajarkot 1", "Dailekh 1", "Dailekh 2", "Surkhet 1", "Surkhet 2"],
    "Sudurpashchim (16)": ["Bajura 1", "Bajhang 1", "Achham 1", "Achham 2", "Doti 1", "Kailali 1", "Kailali 2", "Kailali 3", "Kailali 4", "Kailali 5", "Kanchanpur 1", "Kanchanpur 2", "Kanchanpur 3", "Dadeldhura 1", "Baitadi 1", "Darchula 1"]
}

# 3. Caching & Deep Grounding Logic
@st.cache_data(ttl=3600)
def get_election_research(constituency_name):
    # Professional prompt to handle the Jan 2026 nomination surge
    prompt = f"""
    Perform a professional political analysis for {constituency_name}, Nepal for the March 5, 2026 election. 
    1. Identify all candidates nominated on Jan 20, 2026.
    2. Specifically analyze 'Disruptor' factors: Balen Shah, Rabi Lamichhane, and Kulman Ghising alliance.
    3. Analyze Gen Z sentiment following the Sept 2025 protests.
    4. Provide a WINNER PROBABILITY (%) and Predicted Vote Share.
    """
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    return response

# 4. User Interface
province = st.sidebar.selectbox("1. Select Province", list(constituency_data.keys()))
selected_constituency = st.sidebar.selectbox("2. Select Constituency", constituency_data[province])

if st.button("🔍 Run Grounded Intelligence Search"):
    with st.spinner(f"Accessing Live Jan 2026 Data for {selected_constituency}..."):
        res = get_election_research(selected_constituency)
        st.header(f"Grounded Intelligence: {selected_constituency}")
        st.markdown(res.text)
        
        # Display Citations for transparency
        if res.candidates[0].grounding_metadata.web_search_queries:
            with st.expander("🔍 Verified Search Sources"):
                st.write(res.candidates[0].grounding_metadata.web_search_queries)
