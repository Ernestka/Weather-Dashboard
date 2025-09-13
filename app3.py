import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- CONFIG ---
API_KEY = "112fec4c09d4945a08467c1476fe0e24"  # Your API key
BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

# Streamlit setup
st.set_page_config(page_title="Weather Dashboard",
                   page_icon="🌦", layout="wide")

# --- CSS for backgrounds ---


def set_bg(weather_main):
    if "cloud" in weather_main.lower():
        url = "https://i.ibb.co/9cQhR1g/cloudy.jpg"
    elif "rain" in weather_main.lower():
        url = "https://i.ibb.co/ZVrh7zw/rainy.jpg"
    elif "clear" in weather_main.lower():
        url = "https://i.ibb.co/6sYZT8T/sunny.jpg"
    elif "snow" in weather_main.lower():
        url = "https://i.ibb.co/DzFQqCm/snow.jpg"
    else:
        url = "https://i.ibb.co/QP3L8jn/default-weather.jpg"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("{url}");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# Sidebar
st.sidebar.title("🌦 Weather Dashboard")
st.sidebar.markdown(
    "Enter one or more cities to view live weather forecasts and compare trends.")
st.sidebar.info("Example: London, New York, Kinshasa")

# Main title
st.title("🌍 Multi-City Weather Dashboard")

# User input
city_input = st.text_input(
    "Enter city names (separated by commas):", "London, New York")

if city_input:
    cities = [c.strip() for c in city_input.split(",") if c.strip()]
    all_data = []
    first_weather = None  # track first city weather for background

    for city in cities:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if response.status_code == 200 and "list" in data:
            # Save first weather condition for background
            if not first_weather:
                first_weather = data["list"][0]["weather"][0]["main"]

            # Collect forecast
            for entry in data["list"]:
                all_data.append({
                    "city": city,
                    "datetime": entry["dt_txt"],
                    "temperature": entry["main"]["temp"],
                    "humidity": entry["main"]["humidity"],
                    "wind_speed": entry["wind"]["speed"],
                })

            # Show current metrics
            latest = data["list"][0]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label=f"{city} 🌡 Temp (°C)",
                          value=f"{latest['main']['temp']} °C")
            with col2:
                st.metric(label=f"{city} 💧 Humidity (%)",
                          value=f"{latest['main']['humidity']} %")
            with col3:
                st.metric(label=f"{city} 🌬 Wind (m/s)",
                          value=f"{latest['wind']['speed']} m/s")

        else:
            st.error(f"⚠ Could not fetch data for {city}")

    # Apply background once we know weather
    if first_weather:
        set_bg(first_weather)

    if all_data:
        df = pd.DataFrame(all_data)

        # Tabs
        tab1, tab2 = st.tabs(["📅 Forecast Tables", "📊 Graphical Comparison"])

        with tab1:
            st.subheader("📅 Full 5-Day Forecast Data")
            for city in cities:
                st.write(f"**🔹 Forecast for {city}**")
                st.dataframe(df[df["city"] == city])

        with tab2:
            st.subheader("📊 Multi-City Graphs")

            fig_temp = px.line(df, x="datetime", y="temperature",
                               color="city", title="🌡 Temperature Comparison")
            st.plotly_chart(fig_temp, use_container_width=True)

            fig_humidity = px.line(
                df, x="datetime", y="humidity", color="city", title="💧 Humidity Comparison")
            st.plotly_chart(fig_humidity, use_container_width=True)

            fig_wind = px.line(df, x="datetime", y="wind_speed",
                               color="city", title="🌬 Wind Speed Comparison")
            st.plotly_chart(fig_wind, use_container_width=True)
