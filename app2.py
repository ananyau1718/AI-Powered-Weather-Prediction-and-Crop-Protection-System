import os
import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
import io

# --- 1. CONFIGURATION & SECRETS ---
st.set_page_config(page_title="AgroAssist", page_icon="🌾", layout="wide")

google_api_key = st.secrets["google"]["api_key"]
weather_api_key = st.secrets["weather"]["api_key"]

genai.configure(api_key=google_api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. CUSTOM CSS (To make it look like a modern web app) ---
st.markdown("""
    <style>
    /* Main background and font */
    .stApp {
        background-color: #000000;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Headers */
    h1, h2, h3 {
        color: #1b5e20;
    }
    /* Style the tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #e8f5e9;
        border-radius: 5px 5px 0px 0px;
        padding: 10px 20px;
        color: #2e7d32;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4caf50;
        color: white;
    }
    /* Style buttons */
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #1b5e20;
        border-color: #1b5e20;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. HERO SECTION ---
st.markdown("<h1 style='text-align: center; font-size: 3rem;'>🌾 AgroAssist</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #555;'>Your AI-Powered Smart Farming Assistant</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 4. SIDEBAR (Kept minimal for settings/links) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2674/2674099.png", width=100) # Placeholder farm icon
    st.title("Settings")
    language = st.selectbox("🌍 Language", ["English", "Español", "Français", "اردو", "Deutsch", "中文", "العربية", "Русский"])
    
    st.markdown("---")
   
    

# --- 5. MAIN NAVIGATION TABS ---
tab_weather, tab_crops, tab_soil, tab_chat = st.tabs([
    "🌤️ Weather Forecast", 
    "🌱 Crop & Spraying", 
    "🧪 Soil Health", 
    "🤖 AgroBot"
])

# ==========================================
# TAB 1: WEATHER FORECAST
# ==========================================
with tab_weather:
    st.header("Local Weather Forecast")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        location = st.text_input("📍 Enter your location", placeholder="e.g., Bhopal, India")
        get_weather = st.button("Check Weather")
        
    with col2:
        if get_weather and location:
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={weather_api_key}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                weather_data = response.json()
                st.success(f"Weather data retrieved for {location}")
                # Display in a nice grid format using columns
                w_cols = st.columns(5)
                for i, forecast in enumerate(weather_data['list'][:5]):
                    with w_cols[i]:
                        st.info(f"**{forecast['dt_txt'].split(' ')[1][:5]}**\n\n{forecast['main']['temp']}°C\n\n{forecast['weather'][0]['description'].title()}")
            else:
                st.error("Error fetching weather data. Please check the location.")

# ==========================================
# TAB 2: CROP & SPRAYING ADVISORY
# ==========================================
with tab_crops:
    st.header("Smart Recommendations")
    col_crop, col_spray = st.columns(2)
    
    with col_crop:
        st.subheader("Crop Recommendations")
        with st.container(border=True):
            region = st.text_input("Region", placeholder="e.g., Madhya Pradesh")
            soil_type = st.selectbox("Soil Type", ["Clay", "Sandy", "Loamy", "Silt", "Peaty"])
            if st.button("Get Crop Advice"):
                with st.spinner("Analyzing..."):
                    prompt = f"Provide 3 suitable crop recommendations for {region} with {soil_type} soil. Keep it concise."
                    res = model.generate_content(prompt)
                    st.write(res.text)

    with col_spray:
        st.subheader("Spraying Advisory")
        with st.container(border=True):
            crop = st.text_input("Target Crop", placeholder="e.g., Wheat, Cotton")
            if st.button("Get Spraying Schedule"):
                with st.spinner("Generating schedule..."):
                    prompt = f"What is a standard, safe spraying and pesticide schedule for {crop}? Bullet points."
                    res = model.generate_content(prompt)
                    st.write(res.text)

# ==========================================
# TAB 3: SOIL HEALTH
# ==========================================
with tab_soil:
    st.header("Soil Health Analysis")
    st.markdown("Enter your soil metrics below for a comprehensive AI evaluation.")
    
    # Group inputs into columns for a cleaner look
    col1, col2, col3 = st.columns(3)
    with col1:
        ph_level = st.number_input("pH Level", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
        nitrogen = st.number_input("Nitrogen (N) ppm", min_value=0, max_value=200, value=30)
        organic_matter = st.number_input("Organic Matter (%)", min_value=0.0, max_value=20.0, value=5.0)
    with col2:
        moisture = st.number_input("Moisture (%)", min_value=0, max_value=100, value=50)
        phosphorus = st.number_input("Phosphorus (P) ppm", min_value=0, max_value=150, value=20)
        compaction = st.number_input("Compaction (g/cm³)", min_value=0.5, max_value=3.0, value=1.4)
    with col3:
        temperature = st.number_input("Temperature (°C)", min_value=-10, max_value=60, value=25)
        potassium = st.number_input("Potassium (K) ppm", min_value=0, max_value=300, value=40)
        
    st.write("") # Spacer
    if st.button("Run Soil Diagnostics", use_container_width=True):
        with st.spinner("AgroBot is diagnosing your soil..."):
            prompt = f"Assess soil health: pH {ph_level}, moisture {moisture}%, temp {temperature}°C, N {nitrogen}ppm, P {phosphorus}ppm, K {potassium}ppm, organic {organic_matter}%, compaction {compaction}. Give actionable advice."
            res = model.generate_content(prompt)
            st.success("Diagnostics Complete!")
            st.write(res.text)

# ==========================================
# TAB 4: AGROBOT CHAT
# ==========================================
with tab_chat:
    st.header("Chat with AgroBot")
    st.markdown("Ask anything about farming, pest control, or government schemes.")
    
    # Create a nice chat interface look
    chat_container = st.container(border=True, height=300)
    
    user_input = st.chat_input("Ask AgroBot a question...")
    if user_input:
        with chat_container:
            st.markdown(f"**🧑‍🌾 You:** {user_input}")
            with st.spinner("AgroBot is typing..."):
                response = model.generate_content(user_input)
                st.markdown(f"**🤖 AgroBot:** {response.text}")
