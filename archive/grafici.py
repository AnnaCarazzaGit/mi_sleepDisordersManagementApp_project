import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random

# Imposta il seed per la riproducibilità
np.random.seed(42)
random.seed(42)

# Simula dati per 7 notti
nights = pd.date_range(end=pd.Timestamp.today(), periods=7).date

data = {
    "Date": nights,
    "Total Sleep Time (min)": np.random.normal(420, 30, 7).astype(int),  # media 7h
    "Time in Bed vs Asleep (%)": np.random.uniform(75, 95, 7).round(1),
    "REM Sleep (min)": np.random.normal(90, 10, 7).astype(int),
    "Light Sleep (min)": np.random.normal(210, 20, 7).astype(int),
    "Deep Sleep (min)": np.random.normal(100, 15, 7).astype(int),
    "Average Heart Rate (bpm)": np.random.normal(60, 5, 7).astype(int),
    "Respiratory Rate (breaths/min)": np.random.normal(16, 1.5, 7).round(1),
    "SpO₂ (%)": np.random.normal(97, 1, 7).round(1),
    "Snoring Intensity (0-10)": np.random.randint(0, 11, 7),
    "Snoring Frequency (events/hour)": np.random.randint(0, 15, 7),
    "Body Position": random.choices(["Supine", "Side", "Prone"], k=7),
    "Body Temperature (°C)": np.random.normal(36.6, 0.3, 7).round(1),
    "Room Temperature (°C)": np.random.normal(20, 1.5, 7).round(1)
}

sleep_df = pd.DataFrame(data)

def plot_time_in_bed_vs_asleep(df):
    """Genera un grafico a torta per l'ultima notte registrata."""
    last_row = df.iloc[-1]
    asleep_percentage = last_row["Time in Bed vs Asleep (%)"]
    awake_percentage = 100 - asleep_percentage

    labels = ["Asleep", "Awake"]
    sizes = [asleep_percentage, awake_percentage]

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title(f"Time in Bed vs Asleep - {last_row['Date']}")
    plt.axis('equal')
    plt.show()


def plot_sleep_stages(df):
    """Genera un grafico a barre per le fasi del sonno dell'ultima notte."""
    last_row = df.iloc[-1]
    stages = {
        "REM": last_row["REM Sleep (min)"],
        "Light": last_row["Light Sleep (min)"],
        "Deep": last_row["Deep Sleep (min)"]
    }

    plt.figure(figsize=(8, 5))
    plt.bar(stages.keys(), stages.values())
    plt.title(f"Sleep Stages - {last_row['Date']}")
    plt.ylabel("Minutes")
    plt.xlabel("Stage")
    plt.tight_layout()
    plt.show()

plot_time_in_bed_vs_asleep(sleep_df)
plot_sleep_stages(sleep_df)

import matplotlib.pyplot as plt

def plot_all_sleep_metrics(df):
    """
    Genera grafici a linee per tutti i parametri principali del monitoraggio del sonno.
    Ogni parametro viene visualizzato in un grafico separato.

    Parametri:
        df (pd.DataFrame): DataFrame contenente i dati del sonno.
    """
    metrics = {
        "Total Sleep Time (min)": "Minuti",
        "Time in Bed vs Asleep (%)": "%",
        "Average Heart Rate (bpm)": "bpm",
        "Respiratory Rate (breaths/min)": "Atti/min",
        "SpO₂ (%)": "%",
        "Snoring Intensity (0-10)": "Intensità (0-10)",
        "Snoring Frequency (events/hour)": "Eventi/ora",
        "Body Temperature (°C)": "°C",
        "Room Temperature (°C)": "°C"
    }

    for metric, unit in metrics.items():
        plt.figure(figsize=(10, 4))
        plt.plot(df["Date"], df[metric], marker='o', linestyle='-')
        plt.title(metric)
        plt.xlabel("Data")
        plt.ylabel(unit)
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()


plot_all_sleep_metrics(sleep_df)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def generate_one_night_data():
    """
    Genera dati simulati per una notte di sonno con campionamento ogni minuto.
    Include: frequenza cardiaca, respiratoria, SpO₂ e temperatura cutanea.
    
    Ritorna:
        pd.DataFrame con colonna 'Time' e 4 parametri biometrici.
    """
    minutes = pd.date_range("2025-05-12 22:00", periods=481, freq="T")  # dalle 22:00 alle 06:00
    np.random.seed(42)

    data = {
        "Time": minutes,
        "Heart Rate (bpm)": np.random.normal(60, 5, 481).round(1),
        "Respiratory Rate (breaths/min)": np.random.normal(16, 1.2, 481).round(1),
        "SpO₂ (%)": np.random.normal(97, 0.5, 481).round(1),
        "Skin Temperature (°C)": np.random.normal(36.5, 0.3, 481).round(1)
    }

    return pd.DataFrame(data)

import matplotlib.pyplot as plt
import numpy as np

def plot_one_night_metrics(df):
    """
    Genera grafici a linee per i dati biometrici raccolti durante una notte di sonno.
    Mostra solo l'orario sull'asse X, rimuovendo la data.
    
    Parametri:
        df (pd.DataFrame): Il dataframe con la colonna 'Time' e i parametri biometrici.
    """
    metrics = {
        "Heart Rate (bpm)": "bpm",
        "Respiratory Rate (breaths/min)": "Atti/min",
        "SpO₂ (%)": "%",
        "Skin Temperature (°C)": "°C"
    }

    # Crea una nuova colonna solo con l’orario (stringhe "HH:MM")
    df["TimeOnly"] = df["Time"].dt.strftime("%H:%M")

    for metric, unit in metrics.items():
        plt.figure(figsize=(12, 4))
        plt.plot(df["TimeOnly"], df[metric], linewidth=1)
        plt.title(f"Andamento {metric}")
        plt.xlabel("Orario")
        plt.ylabel(unit)

        # Mostra solo un numero limitato di etichette orarie (ogni ora)
        tick_indices = np.linspace(0, len(df["TimeOnly"])-1, 9, dtype=int)
        plt.xticks(tick_indices, df["TimeOnly"].iloc[tick_indices], rotation=45)

        plt.grid(True)
        plt.tight_layout()
        plt.show()

# Crea i dati
night_df = generate_one_night_data()

# Mostra i grafici
#plot_one_night_metrics(night_df)

def generate_night_data(date):
    """
    Genera dati simulati per una notte intera con campionamento al minuto.
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
def generate_sleep_data_range(start_date, num_days):
    """
    Genera dati simulati per più notti consecutive.
    """
    dates = pd.date_range(start=start_date, periods=num_days, freq='D')
    full_data = pd.concat([generate_night_data(date) for date in dates], ignore_index=True)
    return full_data

def compute_daily_averages(df):
    """
    Calcola la media giornaliera dei parametri biometrici.
    """
    return df.groupby("Date")[[
        "Heart Rate (bpm)",
        "Respiratory Rate (breaths/min)",
        "SpO₂ (%)",
        "Skin Temperature (°C)"
    ]].mean().reset_index()
import matplotlib.pyplot as plt

def plot_daily_trends(daily_df):
    """
    Plotta i trend giornalieri dei parametri biometrici.
    """
    metrics = {
        "Heart Rate (bpm)": "bpm",
        "Respiratory Rate (breaths/min)": "Atti/min",
        "SpO₂ (%)": "%",
        "Skin Temperature (°C)": "°C"
    }

    for metric, unit in metrics.items():
        plt.figure(figsize=(12, 4))
        plt.plot(daily_df["Date"], daily_df[metric], marker='o', linestyle='-')
        plt.title(f"Andamento Giornaliero - {metric}")
        plt.xlabel("Data")
        plt.ylabel(unit)
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
# Genera dati per 1 mese
sleep_data_1_month = generate_sleep_data_range("2025-04-12", 30)

# Calcola medie giornaliere
daily_avg_1_month = compute_daily_averages(sleep_data_1_month)

# Mostra i grafici giornalieri
#plot_daily_trends(daily_avg_1_month)




