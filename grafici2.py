import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Funzione per generare i dati di una singola notte
def generate_night_data(date):
    minutes = pd.date_range(f"{date} 22:00", periods=480, freq="T")
    return pd.DataFrame({
        "Time": minutes,
        "Heart Rate (bpm)": np.random.normal(60, 5, 480).round(1),
        "Respiratory Rate (breaths/min)": np.random.normal(16, 1.2, 480).round(1),
        "SpO₂ (%)": np.random.normal(97, 0.5, 480).round(1),
        "Skin Temperature (°C)": np.random.normal(36.5, 0.3, 480).round(1),
        "Date": pd.to_datetime(date).date()
    })

# 2. Funzione per generare i dati per un intervallo di notti
def generate_sleep_data_range(start_date, num_days):
    dates = pd.date_range(start=start_date, periods=num_days, freq='D')
    full_data = pd.concat([generate_night_data(date) for date in dates], ignore_index=True)
    return full_data

# 3. Funzione per calcolare medie giornaliere
def compute_daily_averages(df):
    return df.groupby("Date")[[
        "Heart Rate (bpm)",
        "Respiratory Rate (breaths/min)",
        "SpO₂ (%)",
        "Skin Temperature (°C)"
    ]].mean().reset_index()

# 4. Funzione per plottare trend giornalieri (mensile o semestrale)
def plot_long_term_trends(daily_df, title_suffix=""):
    metrics = {
        "Heart Rate (bpm)": "bpm",
        "Respiratory Rate (breaths/min)": "Atti/min",
        "SpO₂ (%)": "%",
        "Skin Temperature (°C)": "°C"
    }

    for metric, unit in metrics.items():
        plt.figure(figsize=(14, 4))
        plt.plot(daily_df["Date"], daily_df[metric], marker='.', linestyle='-', linewidth=1)
        plt.title(f"{metric} - Andamento {title_suffix}")
        plt.xlabel("Data")
        plt.ylabel(unit)
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
# Genera i dati
sleep_data_1_month = generate_sleep_data_range("2025-04-12", 30)
sleep_data_6_months = generate_sleep_data_range("2024-11-12", 180)

# Calcola le medie giornaliere
daily_avg_1_month = compute_daily_averages(sleep_data_1_month)
daily_avg_6_months = compute_daily_averages(sleep_data_6_months)

# Plot
#plot_long_term_trends(daily_avg_1_month, "Mensile")
#plot_long_term_trends(daily_avg_6_months, "Semestrale")

def plot_single_night(df, date_string):
    """
    Plotta i 4 parametri biometrici minuto per minuto per una specifica notte.

    Parametri:
        df (pd.DataFrame): Il dataframe completo con tutte le notti.
        date_string (str): La data della notte da plottare (formato 'YYYY-MM-DD').
    """
    night_df = df[df["Date"] == pd.to_datetime(date_string).date()]
    if night_df.empty:
        print(f"Nessun dato trovato per la data {date_string}")
        return

    metrics = {
        "Heart Rate (bpm)": "bpm",
        "Respiratory Rate (breaths/min)": "Atti/min",
        "SpO₂ (%)": "%",
        "Skin Temperature (°C)": "°C"
    }

    # Estrai solo l'orario per l'asse X
    night_df["TimeOnly"] = night_df["Time"].dt.strftime("%H:%M")

    for metric, unit in metrics.items():
        plt.figure(figsize=(12, 4))
        plt.plot(night_df["TimeOnly"], night_df[metric], linewidth=1)
        plt.title(f"{metric} - {date_string}")
        plt.xlabel("Ora")
        plt.ylabel(unit)

        tick_indices = np.linspace(0, len(night_df["TimeOnly"]) - 1, 9, dtype=int)
        plt.xticks(tick_indices, night_df["TimeOnly"].iloc[tick_indices], rotation=45)

        plt.grid(True)
        plt.tight_layout()
        plt.show()
# Plotta una notte specifica (es. del mese simulato)
#plot_single_night(sleep_data_1_month, "2025-04-15")

# Ridefinisco anche la funzione per il plotting su lungo termine
def plot_long_term_trends(daily_df, title_suffix=""):
    metrics = {
        "Heart Rate (bpm)": "bpm",
        "Respiratory Rate (breaths/min)": "Atti/min",
        "SpO₂ (%)": "%",
        "Skin Temperature (°C)": "°C"
    }

    for metric, unit in metrics.items():
        plt.figure(figsize=(14, 4))
        plt.plot(daily_df["Date"], daily_df[metric], marker='.', linestyle='-', linewidth=1)
        plt.title(f"{metric} - Andamento {title_suffix}")
        plt.xlabel("Data")
        plt.ylabel(unit)
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

def plot_last_7_nights(df):
    """
    Plotta i 4 parametri biometrici minuto per minuto per le ultime 7 notti.
    Mostra solo gli orari sull’asse X per ogni notte.
    
    Parametri:
        df (pd.DataFrame): Il dataframe con tutte le notti simulate.
    """
    # Trova le ultime 7 date presenti
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
       

# Ora genero i grafici
sleep_data_7_days = generate_sleep_data_range("2025-04-12",49)
daily_avg_7days = compute_daily_averages(sleep_data_7_days)
plot_last_7_nights(daily_avg_7days, "Ultimi 7 giorni")
