import pandas as pd
import numpy as np

def generate_night_data(date):
    """
    Genera dati simulati minuto per minuto per una notte intera.
    """
    minutes = pd.date_range(f"{date} 22:00", periods=480, freq="T")
    return pd.DataFrame({
        "Time": minutes,
        "Heart Rate (bpm)": np.random.normal(60, 5, 480).round(1),
        "Respiratory Rate (breaths/min)": np.random.normal(16, 1.2, 480).round(1),
        "SpO₂ (%)": np.random.normal(97, 0.5, 480).round(1),
        "Skin Temperature (°C)": np.random.normal(36.5, 0.3, 480).round(1),
        "Date": pd.to_datetime(date).date()
    })

def generate_last_7_nights_data():
    """
    Genera dati simulati per le ultime 7 notti a partire da oggi.
    """
    today = pd.Timestamp.today().normalize()
    start_date = today - pd.Timedelta(days=6)
    dates = pd.date_range(start=start_date, periods=7, freq="D")
    return pd.concat([generate_night_data(date) for date in dates], ignore_index=True)

def generate_last_month_data():
    """
    Genera dati simulati per gli ultimi 30 giorni (1 mese) a partire da oggi.
    """
    today = pd.Timestamp.today().normalize()
    start_date = today - pd.Timedelta(days=29)
    dates = pd.date_range(start=start_date, periods=30, freq="D")
    return pd.concat([generate_night_data(date) for date in dates], ignore_index=True)

def generate_last_6_months_data():
    """
    Genera dati simulati per gli ultimi 180 giorni (6 mesi) a partire da oggi.
    """
    today = pd.Timestamp.today().normalize()
    start_date = today - pd.Timedelta(days=179)
    dates = pd.date_range(start=start_date, periods=180, freq="D")
    return pd.concat([generate_night_data(date) for date in dates], ignore_index=True)

sleep_data_7_nights = generate_last_7_nights_data()
sleep_data_1_month = generate_last_month_data()
sleep_data_6_months = generate_last_6_months_data()

import matplotlib.pyplot as plt

def plot_last_7_nights(df):
    """
    Plotta i 4 parametri biometrici minuto per minuto per le ultime 7 notti.
    Mostra solo gli orari sull’asse X per ogni notte.
    """
    last_7_dates = sorted(df["Date"].unique())[-7:]

    metrics = {
        "Heart Rate (bpm)": "bpm",
        "Respiratory Rate (breaths/min)": "Atti/min",
        "SpO₂ (%)": "%",
        "Skin Temperature (°C)": "°C"
    }

    for date in last_7_dates:
        night_df = df[df["Date"] == date].copy()
        night_df["TimeOnly"] = night_df["Time"].dt.strftime("%H:%M")

        for metric, unit in metrics.items():
            plt.figure(figsize=(12, 4))
            plt.plot(night_df["TimeOnly"], night_df[metric], linewidth=1)
            plt.title(f"{metric} - {date}")
            plt.xlabel("Ora")
            plt.ylabel(unit)

            tick_indices = np.linspace(0, len(night_df["TimeOnly"]) - 1, 9, dtype=int)
            plt.xticks(tick_indices, night_df["TimeOnly"].iloc[tick_indices], rotation=45)

            plt.grid(True)
            plt.tight_layout()
            plt.show()

def compute_daily_averages(df):
    """
    Calcola le medie giornaliere dei parametri biometrici.
    """
    return df.groupby("Date")[[
        "Heart Rate (bpm)",
        "Respiratory Rate (breaths/min)",
        "SpO₂ (%)",
        "Skin Temperature (°C)"
    ]].mean().reset_index()

def plot_long_term_trends(daily_df, title_suffix=""):
    """
    Plotta l'andamento giornaliero dei parametri biometrici.
    """
    metrics = {
        "Heart Rate (bpm)": "bpm",
        "Respiratory Rate (breaths/min)": "Atti/min",
        "SpO₂ (%)": "%",
        "Skin Temperature (°C)": "°C"
    }

    for metric, unit in metrics.items():
        plt.figure(figsize=(14, 4))
        plt.plot(daily_df["Date"], daily_df[metric], marker='o', linestyle='-')
        plt.title(f"{metric} - Andamento {title_suffix}")
        plt.xlabel("Data")
        plt.ylabel(unit)
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
# Dati
sleep_data_7_nights = generate_last_7_nights_data()
sleep_data_1_month = generate_last_month_data()
sleep_data_6_months = generate_last_6_months_data()

# Plotta le ultime 7 notti


# Calcola e plotta le medie giornaliere
plot_long_term_trends(compute_daily_averages(sleep_data_1_month), "Ultimo Mese")
plot_long_term_trends(compute_daily_averages(sleep_data_6_months), "Ultimi 6 Mesi")

import matplotlib.pyplot as plt

def plot_week_summary(df):
    """
    Plotta un grafico riassuntivo unico per ciascun parametro su 7 giorni.
    Ogni grafico mostra l'intera settimana su un asse temporale continuo.
    """
    metrics = {
        "Heart Rate (bpm)": "bpm",
        "Respiratory Rate (breaths/min)": "Atti/min",
        "SpO₂ (%)": "%",
        "Skin Temperature (°C)": "°C"
    }

    for metric, unit in metrics.items():
        plt.figure(figsize=(15, 5))
        plt.plot(df["Time"], df[metric], linewidth=1)
        plt.title(f"{metric} - Riassunto Ultimi 7 Giorni")
        plt.xlabel("Data e ora")
        plt.ylabel(unit)
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
sleep_data_7_nights = generate_last_7_nights_data()
plot_week_summary(sleep_data_7_nights)

