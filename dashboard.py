import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Fungsi untuk Memuat Data (Caching agar Cepat) ---
@st.cache_data
def load_data():
    # Asumsikan file 'day_dataset.csv' dan 'hour_dataset.csv' ada di direktori yang sama
    try:
        day_df = pd.read_csv("day_dataset.csv")
        hour_df = pd.read_csv("hour_dataset.csv")
        return day_df, hour_df
    except FileNotFoundError:
        st.error("Pastikan file 'day_dataset.csv' dan 'hour_dataset.csv' ada di direktori yang sama.")
        return pd.DataFrame(), pd.DataFrame()

day_df, hour_df = load_data()

# Hanya lanjutkan jika data berhasil dimuat
if not day_df.empty and not hour_df.empty:

    # --- Judul Dashboard ---
    st.title("🚲 Bike Sharing Dashboard Interaktif")
    st.markdown("Analisis Pola Penggunaan dan Pengaruh Cuaca")

    # --- Sidebar untuk Filter Global ---
    st.sidebar.header("⚙️ Pengaturan Filter")

    # Filter Tahun (Jika ada kolom 'yr' di day_df, gunakan itu)
    if 'yr' in day_df.columns:
        year_options = day_df['yr'].unique().tolist()
        selected_years = st.sidebar.multiselect(
            "Pilih Tahun:",
            options=[0, 1], # Asumsi 0=2011, 1=2012
            default=[0, 1],
            format_func=lambda x: f"20{'11' if x == 0 else '12'}"
        )
        day_df_filtered = day_df[day_df['yr'].isin(selected_years)]
        hour_df_filtered = hour_df[hour_df['yr'].isin(selected_years)]
    else:
        day_df_filtered = day_df
        hour_df_filtered = hour_df


    # --- Bagian 1: Pola Penggunaan Harian & Jam Tersibuk (Pertanyaan Bisnis 1) ---
    st.header("1️⃣ Pola Penggunaan Sepeda (Jam Tersibuk)")
    st.markdown("Visualisasi ini menunjukkan distribusi penyewaan berdasarkan jam dalam sehari.")

    # Peta Hari-Hari dalam Seminggu (0=Minggu, 1=Senin, ..., 6=Sabtu)
    day_map = {0: 'Minggu', 1: 'Senin', 2: 'Selasa', 3: 'Rabu', 4: 'Kamis', 5: 'Jumat', 6: 'Sabtu'}
    hour_df_filtered['day_name'] = hour_df_filtered['weekday'].map(day_map)

    # Filter Hari Kerja/Akhir Pekan
    is_workingday = st.selectbox(
        "Pilih Jenis Hari:",
        options=['Semua Hari', 'Hari Kerja (Senin-Jumat)', 'Akhir Pekan/Libur'],
        key='workingday_filter'
    )

    if is_workingday == 'Hari Kerja (Senin-Jumat)':
        hour_plot_data = hour_df_filtered[hour_df_filtered['workingday'] == 1]
    elif is_workingday == 'Akhir Pekan/Libur':
        hour_plot_data = hour_df_filtered[hour_df_filtered['workingday'] == 0]
    else:
        hour_plot_data = hour_df_filtered

    # Visualisasi Jam Tersibuk (Line Plot)
    hourly_usage = hour_plot_data.groupby('hr')['cnt'].mean().reset_index()
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    sns.lineplot(x='hr', y='cnt', data=hourly_usage, ax=ax1, marker='o')
    ax1.set_title(f"Rata-rata Penggunaan Sepeda per Jam ({is_workingday})", fontsize=14)
    ax1.set_xlabel("Jam (hr)", fontsize=12)
    ax1.set_ylabel("Rata-rata Jumlah Penyewaan", fontsize=12)
    ax1.set_xticks(range(24))
    ax1.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig1)

    st.markdown(
        f"""
        > **Kesimpulan Kunci (Pola Penggunaan):**
        > Jam tersibuk secara keseluruhan adalah antara **pukul 7–9 dan 17–19**, terutama pada hari kerja. Ini mengindikasikan pola penggunaan **komuter**.
        """
    )
    st.write("---")

    # --- Bagian 2: Pengaruh Kondisi Cuaca (Pertanyaan Bisnis 2) ---
    st.header("2️⃣ Pengaruh Kondisi Cuaca")
    st.markdown("Visualisasi ini menunjukkan jumlah penyewaan berdasarkan kondisi cuaca.")

    # Mapping Kategori Cuaca (berdasarkan notebook Anda)
    weather_map = {
        1: 'Cerah/Sedikit Awan',
        2: 'Berkabut/Berawan',
        3: 'Hujan Ringan/Salju Ringan',
        4: 'Hujan Lebat/Badai Salju'
    }
    day_df_filtered['weathersit_name'] = day_df_filtered['weathersit'].map(weather_map)

    # Visualisasi Pengaruh Cuaca (Bar Plot)
    weather_usage = day_df_filtered.groupby('weathersit_name')['cnt'].mean().sort_values(ascending=False).reset_index()
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.barplot(x='weathersit_name', y='cnt', data=weather_usage, ax=ax2, palette="viridis")
    ax2.set_title("Rata-rata Penyewaan Berdasarkan Kondisi Cuaca", fontsize=14)
    ax2.set_xlabel("Kondisi Cuaca", fontsize=12)
    ax2.set_ylabel("Rata-rata Jumlah Penyewaan", fontsize=12)
    plt.xticks(rotation=15, ha='right')
    st.pyplot(fig2)

    st.markdown(
        """
        > **Kesimpulan Kunci (Cuaca):**
        > Penggunaan sepeda tertinggi terjadi pada saat cuaca **Cerah/Sedikit Awan**. Penyewaan **menurun drastis** saat terjadi cuaca ekstrem, menunjukkan bahwa kenyamanan cuaca adalah faktor utama.
        """
    )