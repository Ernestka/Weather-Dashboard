from datetime import datetime, timedelta
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
# import matplotlib.pyplot as plt

# --- CONFIG ---
API_KEY = "112fec4c09d4945a08467c1476fe0e24"  # Your API key
api_key="cd5a01c5e8ad457b9764fd68b2681a5d"
BASE_URL = "https://api.openweathermap.org/data/2.5"
GEOCODING_URL = "http://api.openweathermap.org/geo/1.0/direct"  # city -> coords
TIMEMACHINE_URL = "https://api.weatherbit.io/v2.0/history/daily"
# Streamlit page setup
# ========= 1) CONFIGURATION =========
API_KEY2 = "8cef7cd2d8f24dd680d162755251309"  # <-- Remplacez par votre clé API personnelle WeatherAPI

# ========= 2) FONCTIONS UTILES =========
def get_weather_history(city, days=30):
    """
    Récupère les données météo des 'days' derniers jours pour une ville donnée.
    Retourne une liste de dictionnaires.
    """
    records = []
    today = datetime.today()
    for i in range(days):
        date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY2}&q={city}&dt={date_str}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            try:
                day = data['forecast']['forecastday'][0]['day']
                records.append({
                    "city": city,
                    "datetime": date_str,
                    "temperature": day['avgtemp_c'],
                    "humidity": day['avghumidity'],
                    "wind_speed": day['maxwind_kph'],
                })
            except KeyError:
                # Parfois WeatherAPI ne retourne pas de data pour certaines dates
                pass
        else:
            st.error(f"Erreur {response.status_code} pour {city} à la date {date_str}")
    return records

def create_combined_dataframe(cities, days=60):
    """
    Construit un DataFrame pandas contenant les données pour toutes les villes.
    """
    all_records = []
    for city in cities:
        all_records.extend(get_weather_history(city, days))
    df = pd.DataFrame(all_records)
    if not df.empty:
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime")
    return df


st.set_page_config(page_title="Weather Dashboard", page_icon="🌦", layout="wide")

# Sidebar
st.sidebar.title("🌦 Weather Dashboard")
st.sidebar.markdown("Enter one or more cities to view live weather forecasts and compare trends.")
st.sidebar.info("Example: Limbe, Yaounde, Kinshasa")

# Main title
st.title("🌍Weather Dashboard")

# def get_coords_for_city(city_name, limit=1):
#     """
#     Retourne une liste de résultats de géocodage (dicts avec 'lat' et 'lon').
#     Par défaut on demande limit=1 pour ne récupérer qu'un résultat.
#     """
#     params = {"q": city_name, "limit": limit, "appid": API_KEY}
#     resp = requests.get(GEOCODING_URL, params=params, timeout=10)
#     resp.raise_for_status()  # lève une erreur HTTP si code != 200
#     results = resp.json()    # liste de dicts (peut être vide)
#     if not results:
#         return []            # aucune correspondance
#     # Normaliser les types (float) et garder uniquement champs utiles
#     normalized = []
#     for r in results:
#         if "lat" in r and "lon" in r:
#             normalized.append({
#                 "name": r.get("name"),
#                 "lat": float(r["lat"]),
#                 "lon": float(r["lon"]),
#                 "country": r.get("country"),
#                 "state": r.get("state")
#             })
#     return normalized


# User input for cities
city_input = st.text_input("Enter city names (separated by commas):", "Limbe, ")

if city_input:
    cities = [c.strip() for c in city_input.split(",") if c.strip()]
    all_data_forecast = []
    all_records=[]
    for city in cities:
        # city_coor=get_coords_for_city(city_name=city)
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        # params2 = {"lat":city_coor[0]["lat"],"lon":city_coor[0]["lon"],
        #             "start_date":datetime.strptime("2025-09-4", "%Y-%m-%d").date(),
        #             "end_date":datetime.strptime("2025-09-14", "%Y-%m-%d").date(), 
        #             "key": api_key}
        response1 = requests.get(BASE_URL+"/forecast", params=params)
        data1 = response1.json()
        if response1.status_code == 200 and "list" in data1:
            # Collect forecast
            for entry in data1["list"]:
                all_data_forecast.append({
                    "city": city,
                    "datetime": entry["dt_txt"],
                    "temperature": entry["main"]["temp"],
                    "humidity": entry["main"]["humidity"],
                    "wind_speed": entry["wind"]["speed"],
                })
        

            # Show current metrics (latest forecast)
            latest = data1["list"][0]
            col1, col2, col3= st.columns(3)
            with col1:
                st.metric(label=f"{city} 🌡 Temperature (°C)", value=f"{latest['main']['temp']} °C")
            with col2:
                st.metric(label=f"{city} 💧 Humidity (%)", value=f"{latest['main']['humidity']} %")
            with col3:
                st.metric(label=f"{city} 🌬 Wind (m/s)", value=f"{latest['wind']['speed']} m/s")
            # with col4:
            #     st.metric(label=f"{city} 💧 Precipitation(%)", value=f"{latest['pop']*100}%")
            # with col5:
            #     st.metric(label=f"{city} 🌦 cloud(%)", value=f"{latest['clouds']['all'] }%")
            

        else:
            st.error(f"⚠ Could not fetch data for {city}")
        
        all_records.extend(get_weather_history(city, 30))# st.text(data2)
    # If we have data, display it
    if all_data_forecast:
        # st.text(all_data_forecast)
        # st.text(all_records)
        # all_data=all_data_forecast.extend(all_records)
        # st.text(all_data)
        df = pd.DataFrame(all_data_forecast)
        df2=pd.DataFrame(all_records)
        if not df.empty:
            df["datetime"] = pd.to_datetime(df["datetime"])
            df = df.sort_values("datetime")
   
        # Tabs for better navigation
        tab0,tab1, tab2 ,tab3= st.tabs(["📅 Forecast Tables","📅  Historical Tables", "📊 Forecast Graphical Comparison","📊 Historical Graphical Comparison"])

        with tab0:
            st.subheader("📅 Full 5-Day Forecast Data")
            for city in cities:
                st.write(f"**🔹 Forecast for {city}**")
                st.dataframe(df[df["city"] == city])
                csv = df.to_csv(index=False)
                st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"weather_data_forecast_{city}_{datetime.now().strftime('%Y%m%d %H:%M:%S')}.csv",
                mime="text/csv"
            )
        with tab1:
            st.subheader("📅 Historical Data")
            for city in cities:
                st.write(f"**🔹 Historic for {city}**")
                st.dataframe(df2[df2["city"] == city])
                csv = df2.to_csv(index=False)
                st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"weather_data_hist_{city}_{datetime.now().strftime('%Y%m%d %H:%M:%S')}.csv",
                mime="text/csv"
            )
        with tab2:
            st.subheader("📊 Multi-City Graphs")

            fig_temp = px.line(df, x="datetime", y="temperature", color="city", title="🌡 Temperature Comparison")
            st.plotly_chart(fig_temp, use_container_width=True)

            fig_humidity = px.line(df, x="datetime", y="humidity", color="city", title="💧 Humidity Comparison")
            st.plotly_chart(fig_humidity, use_container_width=True)

            fig_wind = px.line(df, x="datetime", y="wind_speed", color="city", title="🌬 Wind Speed Comparison")
            st.plotly_chart(fig_wind, use_container_width=True)
        with tab3:
            
            st.subheader("📊 Multi-City Graphs")

            fig_temp = px.line(df2, x="datetime", y="temperature", color="city", title="🌡 Temperature Comparison")
            st.plotly_chart(fig_temp, use_container_width=True)

            fig_humidity = px.line(df2, x="datetime", y="humidity", color="city", title="💧 Humidity Comparison")
            st.plotly_chart(fig_humidity, use_container_width=True)

            fig_wind = px.line(df2, x="datetime", y="wind_speed", color="city", title="🌬 Wind Speed Comparison")
            st.plotly_chart(fig_wind, use_container_width=True)

            # fig_precipitation = px.line(df, x="datetime", y="precipitation", color="city", title="💧 probability of precipitation Comparison")
            # st.plotly_chart(fig_precipitation, use_container_width=True)

            # fig_cloud = px.line(df, x="datetime", y="cloud", color="city", title="🌦 clouds percentage")
            # st.plotly_chart(fig_cloud, use_container_width=True)
