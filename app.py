import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- CONFIG ---
API_KEY = "112fec4c09d4945a08467c1476fe0e24"  # Your API key
BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

# Streamlit setup
st.set_page_config(page_title="Weather Dashboard", page_icon="🌦", layout="wide")
st.title("🌍 Weather Dashboard")

# Input city
city = st.text_input("Enter a city name:", "London")

if city:
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if response.status_code == 200 and "list" in data:
        # Extract forecast
        forecast = []
        for entry in data["list"]:
            forecast.append({
                "datetime": entry["dt_txt"],
                "temperature": entry["main"]["temp"],
                "humidity": entry["main"]["humidity"],
                "wind_speed": entry["wind"]["speed"],
            })

        df = pd.DataFrame(forecast)

        # Display table
        st.subheader(f"📅 5-Day Forecast for {city}")
        st.dataframe(df.head(10))

        # Plotly graphs
        st.subheader("📊 Weather Trends")

        fig_temp = px.line(df, x="datetime", y="temperature", title="🌡 Temperature over Time")
        st.plotly_chart(fig_temp, use_container_width=True)

        fig_humidity = px.line(df, x="datetime", y="humidity", title="💧 Humidity over Time")
        st.plotly_chart(fig_humidity, use_container_width=True)

        fig_wind = px.line(df, x="datetime", y="wind_speed", title="🌬 Wind Speed over Time")
        st.plotly_chart(fig_wind, use_container_width=True)

    else:
        st.error("Could not fetch forecast data.")
