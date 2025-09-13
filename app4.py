import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- CONFIG ---
API_KEY = "112fec4c09d4945a08467c1476fe0e24"
BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

# Streamlit setup
st.set_page_config(page_title="Weather Dashboard", page_icon="🌦", layout="wide")
st.title("🌍 Weather Dashboard")

# Sidebar for user input
st.sidebar.header("⚙️ Settings")
city_input = st.sidebar.text_input("Enter city names (comma separated):", "London, New York, Paris")

if city_input:
    cities = [c.strip() for c in city_input.split(",") if c.strip()]
    all_data = []
    latest_forecasts = {}

    for city in cities:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if response.status_code == 200 and "list" in data:
            for entry in data["list"]:
                all_data.append({
                    "city": city,
                    "datetime": entry["dt_txt"],
                    "temperature": entry["main"]["temp"],
                    "humidity": entry["main"]["humidity"],
                    "wind_speed": entry["wind"]["speed"],
                })

            # Store the latest forecast (first entry of API)
            first_entry = data["list"][0]
            latest_forecasts[city] = {
                "temperature": first_entry["main"]["temp"],
                "humidity": first_entry["main"]["humidity"],
                "wind_speed": first_entry["wind"]["speed"],
            }
        else:
            st.error(f"⚠ Could not fetch data for {city}")

    if all_data:
        df = pd.DataFrame(all_data)

        # --- SUMMARY CARDS ---
        st.subheader("🌟 Latest Weather Overview")
        cols = st.columns(len(latest_forecasts))  # one card per city
        for i, (city, vals) in enumerate(latest_forecasts.items()):
            with cols[i]:
                st.markdown(f"### {city}")
                st.metric("🌡 Temp (°C)", vals["temperature"])
                st.metric("💧 Humidity (%)", vals["humidity"])
                st.metric("🌬 Wind (m/s)", vals["wind_speed"])

        # --- FULL FORECAST TABLES ---
        st.subheader("📅 5-Day Forecast Data (3h intervals)")
        for city in cities:
            st.write(f"**🔹 Forecast for {city}**")
            st.dataframe(df[df["city"] == city])

        # --- COMPARISON PLOTS ---
        st.subheader("📊 Multi-City Graphical Comparison")
        fig_temp = px.line(df, x="datetime", y="temperature", color="city", title="🌡 Temperature Comparison")
        st.plotly_chart(fig_temp, use_container_width=True)

        fig_humidity = px.line(df, x="datetime", y="humidity", color="city", title="💧 Humidity Comparison")
        st.plotly_chart(fig_humidity, use_container_width=True)

        fig_wind = px.line(df, x="datetime", y="wind_speed", color="city", title="🌬 Wind Speed Comparison")
        st.plotly_chart(fig_wind, use_container_width=True)
