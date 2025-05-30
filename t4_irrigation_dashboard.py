
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Dashboard Title ---
st.title("T4 Smart Irrigation Scheduler Dashboard")
st.markdown("""
This dashboard schedules irrigation for T4 treatment based on:
- **NDVI readings**
- **Soil moisture at 15 cm**
- **Evapotranspiration (ET0)**
- **Rain Forecast**

**Irrigation is triggered when:**
- NDVI < 0.65 (plant stress)
- Soil moisture < 70% of FC
- ET0 > 3.5 mm
- Rain forecast < 2 mm
""")

# --- Upload CSV ---
uploaded_file = st.file_uploader("Upload NDVI, soil moisture, and weather data (.csv)", type="csv")

# --- Parameters ---
st.sidebar.header("Scheduler Parameters")
ndvi_threshold = st.sidebar.number_input("NDVI Stress Threshold", value=0.65)
fc = st.sidebar.number_input("Field Capacity (FC) [%]", value=38.0)
soil_moisture_threshold = 0.70 * fc
et0_threshold = st.sidebar.number_input("ET0 Threshold (mm)", value=3.5)
rain_threshold = st.sidebar.number_input("Rain Forecast Threshold (mm)", value=2.0)
kc = st.sidebar.number_input("Crop Coefficient (Kc)", value=1.15)

# --- Main Logic ---
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, parse_dates=['timestamp'])

    def t4_irrigation_decision(row):
        if (row['NDVI'] < ndvi_threshold and
            row['soil_moisture'] < soil_moisture_threshold and
            row['ET0'] > et0_threshold and
            row['forecast_rain'] < rain_threshold):
            etc = row['ET0'] * kc
            irrigation = max(0, etc - row['forecast_rain'])
            return pd.Series([True, etc, irrigation])
        else:
            return pd.Series([False, 0, 0])

    df[['irrigate', 'ETc', 'irrigation_mm']] = df.apply(t4_irrigation_decision, axis=1)

    # Show Results
    st.success("Irrigation schedule calculated successfully!")
    st.dataframe(df[['timestamp', 'NDVI', 'soil_moisture', 'ET0', 'forecast_rain', 'irrigate', 'ETc', 'irrigation_mm']])

    # --- Visualization ---
    st.subheader("📈 Data Visualization")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=df, x='timestamp', y='NDVI', label='NDVI', marker='o', ax=ax)
    sns.lineplot(data=df, x='timestamp', y='soil_moisture', label='Soil Moisture', marker='x', ax=ax)
    sns.lineplot(data=df, x='timestamp', y='ET0', label='ET0', marker='s', ax=ax)
    sns.lineplot(data=df, x='timestamp', y='forecast_rain', label='Rain Forecast', marker='^', ax=ax)
    sns.lineplot(data=df, x='timestamp', y='irrigation_mm', label='Irrigation (mm)', marker='D', ax=ax)
    ax.set_title("NDVI, Soil Moisture, ET0, Rain Forecast, and Irrigation Schedule")
    ax.set_xlabel("Date")
    ax.set_ylabel("Values")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # Download CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download T4 Irrigation Schedule", csv, "T4_irrigation_schedule.csv", "text/csv")

else:
    st.warning("Please upload your NDVI, soil moisture, and weather data file to proceed.")

# --- Sample Format Guidance ---
st.markdown("""
#### 📄 Sample CSV Format:
| timestamp | NDVI | soil_moisture | ET0 | forecast_rain |
|-----------|------|----------------|-----|----------------|
| 2025-06-01 06:00 | 0.62 | 25 | 4.2 | 0.5 |
| 2025-06-02 06:00 | 0.68 | 28 | 3.9 | 3.0 |
| 2025-06-03 06:00 | 0.60 | 24 | 4.0 | 1.5 |
""")
