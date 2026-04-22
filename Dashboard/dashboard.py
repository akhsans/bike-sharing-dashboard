import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

# LOAD DATA
@st.cache_data
def load_data():
    base_dir = os.path.dirname(__file__)
    df = pd.read_csv(os.path.join(base_dir, "main_data.csv"))

    df['dteday'] = pd.to_datetime(df['dteday'])


    if 'season_x' in df.columns:
        df.rename(columns={'season_x': 'season'}, inplace=True)
    if 'weathersit_x' in df.columns:
        df.rename(columns={'weathersit_x': 'weathersit'}, inplace=True)

 
    weather_map = {
        1: "Cerah",
        2: "Kabut / Mendung",
        3: "Hujan Ringan / Salju",
        4: "Hujan Lebat"
    }

    season_map = {
        1: "Spring",
        2: "Summer",
        3: "Fall",
        4: "Winter"
    }

    if df['weathersit'].dtype != 'O':
        df['weathersit'] = df['weathersit'].map(weather_map)

    if df['season'].dtype != 'O':
        df['season'] = df['season'].map(season_map)


    if 'workingday' in df.columns:
        df['day_type'] = df['workingday'].map({
            1: "Hari Kerja",
            0: "Libur"
        })

    return df

df = load_data()


# SIDEBAR FILTER

st.sidebar.header("🔎 Filter Data")

date_range = st.sidebar.date_input(
    "Tanggal",
    (df['dteday'].min().date(), df['dteday'].max().date())
)

weather_filter = st.sidebar.multiselect(
    "Cuaca",
    df['weathersit'].dropna().unique(),
    default=df['weathersit'].dropna().unique()
)

season_filter = st.sidebar.multiselect(
    "Musim",
    df['season'].dropna().unique(),
    default=df['season'].dropna().unique()
)

day_type_filter = st.sidebar.multiselect(
    "Tipe Hari",
    df['day_type'].dropna().unique(),
    default=df['day_type'].dropna().unique()
)


# FILTER DATA

start_date, end_date = date_range

df_filtered = df[
    (df['dteday'].dt.date >= start_date) &
    (df['dteday'].dt.date <= end_date) &
    (df['weathersit'].isin(weather_filter)) &
    (df['season'].isin(season_filter)) &
    (df['day_type'].isin(day_type_filter))
]


# TITLE
st.title("🚲 Bike Sharing Dashboard")
st.caption("Analisis berdasarkan dataset Bike Sharing")

if df_filtered.empty:
    st.warning("⚠️ Tidak ada data sesuai filter")
    st.stop()


# KPI

st.subheader("📊 Total Penyewaan")

st.metric(
    label="Total Rental Sepeda",
    value=f"{int(df_filtered['cnt'].sum()):,}"
)

st.divider()


# 1. CUACA

st.subheader("🌤️ Pengaruh Cuaca terhadap Penyewaan")

weather_avg = df_filtered.groupby('weathersit')['cnt'].mean()
st.bar_chart(weather_avg)


# 2. JAM

st.subheader("⏰ Jam dengan Penyewaan Tertinggi")

if 'hr' in df_filtered.columns:
    hour_avg = df_filtered.groupby('hr')['cnt'].mean()
    st.line_chart(hour_avg)
else:
    st.warning("Kolom 'hr' tidak tersedia")

st.divider()


# 3. HARI KERJA VS LIBUR

st.subheader("💼 Hari Kerja vs Libur")

day_avg = df_filtered.groupby('day_type')['cnt'].mean()
st.bar_chart(day_avg)

st.divider()


# 4. MUSIM

st.subheader("🍂 Pengaruh Musim terhadap Penyewaan")

season_order = ["Spring", "Summer", "Fall", "Winter"]
season_avg = df_filtered.groupby('season')['cnt'].mean().reindex(season_order)

st.bar_chart(season_avg)

st.divider()


# CLUSTERING JUMLAH

st.subheader("📊 Clustering Berdasarkan Jumlah Penyewaan")

df_filtered['cluster'] = pd.qcut(
    df_filtered['cnt'],
    q=3,
    labels=["Rendah", "Sedang", "Tinggi"]
)

st.bar_chart(df_filtered['cluster'].value_counts())


# CLUSTERING WAKTU

st.subheader("⏰ Clustering Waktu (Binning)")

if 'hr' in df_filtered.columns:
    df_filtered['time_bin'] = pd.cut(
        df_filtered['hr'],
        bins=[0, 6, 12, 18, 24],
        labels=["malam", "Pagi", "Siang", "sore"],
        right=False
    )

    time_avg = df_filtered.groupby('time_bin')['cnt'].mean()
    st.bar_chart(time_avg)

st.divider()


# INSIGHT
st.subheader("📌 Insight")

st.markdown("""
- Penyewaan meningkat saat cuaca cerah
- Jam sibuk terjadi pada pagi dan sore hari
- Hari kerja memiliki penyewaan lebih tinggi dibanding libur
- Musim Summer dan Fall mendominasi jumlah penyewaan
- Clustering menunjukkan pembagian penggunaan rendah hingga tinggi
""")

