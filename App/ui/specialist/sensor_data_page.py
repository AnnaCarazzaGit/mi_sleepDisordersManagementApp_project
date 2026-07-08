import customtkinter as ctk
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from ui.style_ctk import *


class SensorDataPage(ctk.CTkFrame):
    def __init__(self, master, main_window, patient_id=None):
        super().__init__(master, fg_color=COLORS["background"])
        self.main_window = main_window
        self.patient_id = patient_id

        create_label(self, "Sensor Data Overview", size=FONT_SIZES["large"]).pack(pady=15)

        filter_frame = create_frame(self, bg_color="transparent", width=600, height=140)
        filter_frame.pack(pady=10, padx=20, fill="x")

        create_label(filter_frame, "Select Parameter:", size=22).pack(anchor="w", pady=(5,0))
        self.param_options = [
            "Total Sleep Time",
            "Time in bed vs time asleep",
            "Sleep Stages",
            "Heart Rate",
            "Respiratory Rate",
            "Oxygen Saturation (SpO₂)",
            "Snoring Alert",
            "Skin Temperature"
        ]
        self.param_dropdown, self.param_var = create_dropdown(filter_frame, self.param_options)
        self.param_dropdown.pack(fill="x", pady=5)
        self.param_var = self.param_dropdown._variable

        create_label(filter_frame, "Select Timeframe:", size=22).pack(anchor="w", pady=(15,0))
        self.tf_options = ["One night", "Last 7 Days", "Last Month", "Last 6 Months"]
        self.tf_dropdown, self.time_var = create_dropdown(filter_frame, self.tf_options)
        self.tf_dropdown.pack(fill="x", pady=5)
        self.time_var = self.tf_dropdown._variable

        self.graph_container = create_frame(self, width=800, height=350, bg_color=COLORS["card"])
        self.graph_container.pack(padx=20, pady=25, fill="both", expand=True)

        btn_frame = create_frame(self, bg_color="transparent", width=600, height=60)
        btn_frame.pack(pady=(0, 20))

        create_primary_button(btn_frame, "Show Diagram", self.open_graph_window).pack(side="left", padx=15)
        create_secondary_button(btn_frame, "Back", lambda: self.main_window.show_page("patients")).pack(side="left", padx=15)

    def open_graph_window(self):
        param = self.param_var.get()
        tf = self.time_var.get()

        if tf == "One night":
            data = self.load_one_night_data(night_id=1)
        else:
            today = datetime.today()
            if tf == "Last 7 Days":
                start_date = today - timedelta(days=6)
                data = self.load_multiple_nights(start_date.strftime("%Y-%m-%d"), 7)
            elif tf == "Last Month":
                start_date = today - timedelta(days=29)
                data = self.load_multiple_nights(start_date.strftime("%Y-%m-%d"), 30)
            else:
                start_date = today - timedelta(days=179)
                data = self.load_multiple_nights(start_date.strftime("%Y-%m-%d"), 180)

        for w in self.graph_container.winfo_children():
            w.destroy()
        plt.close('all')

        fig = self.generate_figure(param, tf, data)
        if fig:
            canvas = FigureCanvasTkAgg(fig, master=self.graph_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

    def parse_time_str_to_hours(self, time_str):
        try:
            h, m = time_str.strip().split(":")
            return int(h) + int(m) / 60
        except:
            return np.nan

    def parse_percent_str(self, pct_str):
        try:
            return float(pct_str.strip().replace("%", ""))
        except:
            return np.nan

    def load_one_night_data(self, night_id=1):
        conn = sqlite3.connect("sleep_data.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT date, total_sleep_time, time_in_bed_vs_asleep, snoring_alert,
                   avg_heart_rate, avg_respiratory_rate, avg_spo2, avg_skin_temp
            FROM nightly_summary WHERE night_id=?
        """, (night_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError(f"No nightly_summary found for night_id={night_id}")

        (date_str, total_sleep_str, time_in_bed_str, snoring_alert_str,
         avg_hr, avg_rr, avg_spo2, avg_skin_temp) = row

        total_sleep_time_h = self.parse_time_str_to_hours(total_sleep_str)
        asleep_percent = self.parse_percent_str(time_in_bed_str)

        cursor.execute("""
            SELECT minute_id, time, sleep_stage, heart_rate, respiratory_rate, spo2, skin_temp
            FROM minute_data WHERE night_id=? ORDER BY minute_id
        """, (night_id,))
        rows = cursor.fetchall()
        conn.close()

        minutes, sleep_stages, heart_rate, respiratory_rate, spo2, skin_temp = [], [], [], [], [], []
        for _, time_str, stage, hr, rr, sp, st in rows:
            try:
                dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            except:
                dt = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(hours=22) + timedelta(minutes=_)
            minutes.append(dt)
            sleep_stages.append(stage)
            heart_rate.append(hr)
            respiratory_rate.append(rr)
            spo2.append(sp)
            skin_temp.append(st)

        return {
            "date": date_str,
            "minutes": minutes,
            "total_sleep_time_h": total_sleep_time_h,
            "asleep_percent": asleep_percent,
            "heart_rate": np.array(heart_rate),
            "respiratory_rate": np.array(respiratory_rate),
            "spo2": np.array(spo2),
            "skin_temp": np.array(skin_temp),
            "sleep_stages": sleep_stages,
            "snoring_detected": snoring_alert_str.strip() != ""
        }

    def load_multiple_nights(self, start_date, n_days):
        conn = sqlite3.connect("sleep_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT night_id, date, total_sleep_time, time_in_bed_vs_asleep, snoring_alert,
                   avg_heart_rate, avg_respiratory_rate, avg_spo2, avg_skin_temp,
                   wake_pct, N1_pct, N2_pct, N3_pct, REM_pct
            FROM nightly_summary WHERE date >= ? ORDER BY date LIMIT ?
        """, (start_date, n_days))
        rows = cursor.fetchall()
        conn.close()

        nights = []
        for row in rows:
            (night_id, date_str, t_sleep, asleep_pct, snoring, hr, rr, sp, temp, wake, N1, N2, N3, REM) = row
            nights.append({
                "night_id": night_id,
                "date": date_str,
                "total_sleep_time_h": self.parse_time_str_to_hours(t_sleep),
                "asleep_percent": self.parse_percent_str(asleep_pct),
                "snoring_detected": "Yes" if snoring and snoring.strip().lower() != "none" else "No",
                "avg_heart_rate": hr,
                "avg_respiratory_rate": rr,
                "avg_spo2": sp,
                "avg_skin_temp": temp,
                "wake_pct": wake,
                "N1_pct": N1,
                "N2_pct": N2,
                "N3_pct": N3,
                "REM_pct": REM
            })
        return nights

    def compute_average_sleep_data(self, night_data_list):
        result = {
            "dates": [n["date"] for n in night_data_list],
            "total_sleep": [n["total_sleep_time_h"] for n in night_data_list],
            "asleep_percent": [n["asleep_percent"] for n in night_data_list],
            "snoring_detected": [n["snoring_detected"] for n in night_data_list],
            "avg_heart_rate": np.mean([n["avg_heart_rate"] for n in night_data_list]),
            "avg_respiratory_rate": np.mean([n["avg_respiratory_rate"] for n in night_data_list]),
            "avg_spo2": np.mean([n["avg_spo2"] for n in night_data_list]),
            "avg_skin_temp": np.mean([n["avg_skin_temp"] for n in night_data_list]),
            "wake_pct": np.mean([n["wake_pct"] for n in night_data_list]),
            "N1_pct": np.mean([n["N1_pct"] for n in night_data_list]),
            "N2_pct": np.mean([n["N2_pct"] for n in night_data_list]),
            "N3_pct": np.mean([n["N3_pct"] for n in night_data_list]),
            "REM_pct": np.mean([n["REM_pct"] for n in night_data_list])
        }
        return result

    def generate_figure(self, param, tf, data):
        if tf != "One night":
            avg = self.compute_average_sleep_data(data)

        if tf == "One night":
            if param == "Total Sleep Time":
                fig = plt.figure(figsize=(3.5, 1.5))
                val = data['total_sleep_time_h']
                label = "N/A" if np.isnan(val) else f"{int(val)}:{int(round((val % 1) * 60)):02d} h"
                plt.text(0.5, 0.5, label, fontsize=26, ha="center", va="center")
                plt.axis("off")
                return fig

            elif param == "Time in bed vs time asleep":
                fig, ax = plt.subplots(figsize=(2.5, 2.5))
                asleep = data["asleep_percent"]
                awake = 100 - asleep
                ax.pie([asleep, awake], labels=["Asleep", "Awake"], autopct="%1.1f%%",
                       colors=[COLORS["secondary"], COLORS["primary"]])
                ax.set_title(f"Sleep vs Awake - {data['date']}")
                return fig

            elif param == "Sleep Stages":
                fig, ax = plt.subplots(figsize=(6, 3))
                counts = pd.Series(data["sleep_stages"]).value_counts().sort_index()
                ax.bar(counts.index, counts.values, color=COLORS["primary"])
                ax.set_title("Sleep Stages Distribution")
                ax.set_ylabel("Minutes")
                ax.grid(axis="y")
                return fig

            elif param == "Snoring Alert":
                snoring = data["snoring_detected"]
                fig, ax = plt.subplots(figsize=(7, 1.2))
                color = COLORS["primary"] if snoring else "#cbd5e1"
                ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=color))
                ax.text(0.5, 0.5, "Snoring detected" if snoring else "No snoring detected",
                        ha="center", va="center", fontsize=14)
                ax.axis("off")
                return fig

            else:
                fig, ax = plt.subplots(figsize=(8, 3))
                key_map = {
                    "Heart Rate": ("heart_rate", "bpm"),
                    "Respiratory Rate": ("respiratory_rate", "breaths/min"),
                    "Oxygen Saturation (SpO₂)": ("spo2", "%"),
                    "Skin Temperature": ("skin_temp", "°C")
                }
                key, unit = key_map[param]
                ax.plot(data["minutes"], data[key], linewidth=1, color=COLORS["primary"])
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.set_ylabel(f"{param} ({unit})")
                ax.set_title(f"{param} Over One Night")
                fig.autofmt_xdate()
                return fig

        else:
            if param == "Total Sleep Time":
                fig, ax = plt.subplots(figsize=(7, 3))
                ax.plot(avg["dates"], avg["total_sleep"], marker='o', color=COLORS["primary"])
                ax.set_ylabel("Hours")
                ax.set_title(f"Total Sleep Time - {tf}")
                locator = mdates.AutoDateLocator(minticks=3, maxticks=8)
                formatter = mdates.DateFormatter('%d %b')
                ax.xaxis.set_major_locator(locator)
                ax.xaxis.set_major_formatter(formatter)
                fig.autofmt_xdate()
                return fig

            elif param == "Time in bed vs time asleep":
                asleep = np.mean(avg["asleep_percent"])
                awake = 100 - asleep
                fig, ax = plt.subplots(figsize=(2.5, 2.5))
                ax.pie([asleep, awake], labels=["Asleep", "Awake"], autopct="%1.1f%%",
                       colors=[COLORS["secondary"], COLORS["primary"]])
                ax.set_title(f"Avg Sleep vs Wake - {tf}")
                return fig

            elif param == "Sleep Stages":
                sleep_keys = ["wake_pct", "N1_pct", "N2_pct", "N3_pct", "REM_pct"]
                stages = [avg[k] for k in sleep_keys]
                fig, ax = plt.subplots(figsize=(7, 3))
                ax.bar(["Wake", "N1", "N2", "N3", "REM"], stages, color=COLORS["primary"])
                ax.set_title(f"Average Sleep Stages - {tf}")
                ax.set_ylabel("Percentage (%)")
                ax.grid(axis="y")
                return fig

            elif param == "Snoring Alert":
                dates = avg["dates"]
                flags = avg["snoring_detected"]
                fig, ax = plt.subplots(figsize=(7, 1.2))
                for i, (date, flag) in enumerate(zip(dates, flags)):
                    color = COLORS["primary"] if flag == "Yes" else "#cbd5e1"
                    ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color))
                    if len(dates) <= 10:  # mostra il giorno solo se pochi elementi
                        ax.text(i + 0.5, 0.5, pd.to_datetime(date).strftime("%a"), ha="center", va="center", fontsize=10)
                ax.set_xlim(0, len(dates))
                ax.set_ylim(0, 1)
                ax.axis("off")
                plt.title("Snoring This Period", fontsize=14, weight="bold")
                return fig

            else:
                fig, ax = plt.subplots(figsize=(7, 3))
                key_map = {
                    "Heart Rate": "avg_heart_rate",
                    "Respiratory Rate": "avg_respiratory_rate",
                    "Oxygen Saturation (SpO₂)": "avg_spo2",
                    "Skin Temperature": "avg_skin_temp"
                }
                y = [n[key_map[param]] for n in data]
                ax.plot(avg["dates"], y, color=COLORS["primary"])
                ax.set_ylabel(param)
                ax.set_title(f"Average {param} - {tf}")
                locator = mdates.AutoDateLocator(minticks=3, maxticks=8)
                formatter = mdates.DateFormatter('%d %b')
                ax.xaxis.set_major_locator(locator)
                ax.xaxis.set_major_formatter(formatter)
                fig.autofmt_xdate()
                return fig
