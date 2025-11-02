import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi halaman
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")
st.title("🚲 Dashboard Bike Sharing Dataset")

# Load data
hour_df = pd.read_csv("hour_dataset.csv")

# Preprocessing tambahan
hour_df['is_weekend'] = hour_df['weekday'].isin([0, 6]).astype(int)
hour_df['temp_bin'] = pd.cut(hour_df['temp'], bins=10)
hour_df['hum_bin'] = pd.cut(hour_df['hum'], bins=10)
hour_df['wind_bin'] = pd.cut(hour_df['windspeed'], bins=10)

# ============================
# Filter
# ============================
st.sidebar.header("Filter Data")

# Filter jam
jam_range = st.sidebar.slider("Pilih Rentang Jam", 0, 23, (0, 23))
filtered_df = hour_df[(hour_df["hr"] >= jam_range[0]) & (hour_df["hr"] <= jam_range[1])]

# Filter hari kerja/libur
hari_opsi = st.sidebar.selectbox("Pilih Jenis Hari", ["Semua", "Hari Kerja", "Akhir Pekan", "Hari Libur"])
if hari_opsi == "Hari Kerja":
    filtered_df = filtered_df[filtered_df["workingday"] == 1]
elif hari_opsi == "Akhir Pekan":
    filtered_df = filtered_df[filtered_df["is_weekend"] == 1]
elif hari_opsi == "Hari Libur":
    filtered_df = filtered_df[filtered_df["holiday"] == 1]

# Filter cuaca
cuaca = st.sidebar.multiselect("Kondisi Cuaca", options=hour_df["weathersit"].unique(), default=hour_df["weathersit"].unique())
filtered_df = filtered_df[filtered_df["weathersit"].isin(cuaca)]

# ============================
# Visualisasi 1: Rata-rata Penyewaan per Jam
# ============================
st.subheader("Rata-rata Penyewaan Sepeda per Jam (Keseluruhan)")
fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.lineplot(data=filtered_df, x='hr', y='cnt', estimator='mean', ci=None, ax=ax1)
ax1.set_xticks(range(0, 24))
ax1.set_xlabel("Jam")
ax1.set_ylabel("Jumlah Penyewaan")
ax1.grid(True)
st.pyplot(fig1)

# ============================
# Visualisasi 2: Hari Kerja vs Akhir Pekan
# ============================
st.subheader("Pola Penyewaan: Hari Kerja vs Akhir Pekan")
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.lineplot(data=hour_df, x='hr', y='cnt', hue='workingday', estimator='mean', ci=None, ax=ax2)
ax2.set_xticks(range(0, 24))
ax2.set_xlabel("Jam")
ax2.set_ylabel("Jumlah Penyewaan")
ax2.legend(title='Hari Kerja', labels=['Akhir Pekan/Hari Libur', 'Hari Kerja'])
ax2.grid(True)
st.pyplot(fig2)

# ============================
# Visualisasi 3: Hari Libur
# ============================
st.subheader("Pola Penyewaan pada Hari Libur")
fig3, ax3 = plt.subplots(figsize=(10, 5))
sns.lineplot(data=hour_df[hour_df['holiday'] == 1], x='hr', y='cnt', estimator='mean', ci=None, color='orange', ax=ax3)
ax3.set_xticks(range(0, 24))
ax3.set_xlabel("Jam")
ax3.set_ylabel("Jumlah Penyewaan")
ax3.grid(True)
st.pyplot(fig3)

# ============================
# Visualisasi 4: Jam Tersibuk
# ============================
st.subheader("5 Jam Tersibuk")
top5 = hour_df.groupby('hr')['cnt'].mean().sort_values(ascending=False).head(5)
fig4, ax4 = plt.subplots()
sns.barplot(x=top5.index, y=top5.values, ax=ax4)
ax4.set_xlabel("Jam")
ax4.set_ylabel("Rata-rata Penyewaan")
st.pyplot(fig4)

# ============================
# Visualisasi 5: Cuaca
# ============================
st.subheader("Distribusi Penyewaan Berdasarkan Cuaca")
fig5, ax5 = plt.subplots()
sns.boxplot(data=hour_df, x='weathersit', y='cnt', ax=ax5)
ax5.set_xlabel("Kondisi Cuaca (1=Clear, 2=Mist, 3=Rain/Snow)")
ax5.set_ylabel("Jumlah Penyewaan")
st.pyplot(fig5)

# ============================
# Visualisasi 6–8: Suhu, Kelembaban, Angin
# ============================
def plot_bin(df, bin_col, title, xlabel):
    fig, ax = plt.subplots(figsize=(10, 5))
    avg = df.groupby(bin_col)['cnt'].mean().reset_index()
    sns.lineplot(x=avg.index, y='cnt', data=avg, marker='o', ax=ax)
    ax.set_xticks(ticks=avg.index)
    ax.set_xticklabels([f"{round(i.left,2)}–{round(i.right,2)}" for i in avg[bin_col]], rotation=45)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Rata-rata Penyewaan")
    st.pyplot(fig)

st.subheader("Suhu vs Penyewaan")
plot_bin(hour_df, 'temp_bin', 'Rata-rata Penyewaan terhadap Suhu', 'Suhu')

st.subheader("Kelembaban vs Penyewaan")
plot_bin(hour_df, 'hum_bin', 'Rata-rata Penyewaan terhadap Kelembaban', 'Kelembaban')

st.subheader("Kecepatan Angin vs Penyewaan")
plot_bin(hour_df, 'wind_bin', 'Rata-rata Penyewaan terhadap Kecepatan Angin', 'Kecepatan Angin')

# ============================
# Visualisasi 9: Cluster Casual vs Registered
# ============================
st.subheader("Rata-rata Penyewaan per Jam Berdasarkan Cluster")

casual_workday = hour_df[hour_df['workingday'] == 1].groupby('hr')['casual'].mean()
casual_holiday = hour_df[hour_df['holiday'] == 1].groupby('hr')['casual'].mean()
casual_weekend = hour_df[hour_df['is_weekend'] == 1].groupby('hr')['casual'].mean()

registered_workday = hour_df[hour_df['workingday'] == 1].groupby('hr')['registered'].mean()
registered_holiday = hour_df[hour_df['holiday'] == 1].groupby('hr')['registered'].mean()
registered_weekend = hour_df[hour_df['is_weekend'] == 1].groupby('hr')['registered'].mean()

fig, axs = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('Rata-rata Penyewaan Sepeda per Jam Berdasarkan Cluster', fontsize=16)

axs[0, 0].plot(casual_workday, color='skyblue'); axs[0, 0].set_title('Casual Workday')
axs[0, 1].plot(casual_holiday, color='lightgreen'); axs[0, 1].set_title('Casual Holiday')
axs[0, 2].plot(casual_weekend, color='orange'); axs[0, 2].set_title('Casual Weekend')

axs[1, 0].plot(registered_workday, color='blue'); axs[1, 0].set_title('Registered Workday')
axs[1, 1].plot(registered_holiday, color='green'); axs[1, 1].set_title('Registered Holiday')
axs[1, 2].plot(registered_weekend, color='red'); axs[1, 2].set_title('Registered Weekend')

for ax in axs.flat:
    ax.set_xlabel('Jam')
    ax.set_ylabel('Jumlah Penyewaan')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
st.pyplot(fig)