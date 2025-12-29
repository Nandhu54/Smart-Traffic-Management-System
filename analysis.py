import pandas as pd
import datetime
from threading import Lock

EXCEL_FILE = "traffic_data.xlsx"
file_lock = Lock()

def log_traffic_data(road, count, duration):
    with file_lock:
        df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
        new_entry = {
            "Timestamp": datetime.datetime.now(),
            "Road": road,
            "Vehicle Count": count,
            "Green Light Duration": duration
        }
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")

def get_traffic_metrics():
    with file_lock:
        df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today_data = df[df["Timestamp"].astype(str).str.startswith(today)]

    total_vehicles_today = today_data["Vehicle Count"].sum()
    avg_waiting_time = today_data["Green Light Duration"].mean() if not today_data.empty else 0
    peak_hour = (today_data.groupby(today_data["Timestamp"].astype(str).str[11:13])["Vehicle Count"].sum()
                 .idxmax() if not today_data.empty else "N/A")
    total_vehicles_recorded = df["Vehicle Count"].sum()

    return {
        "total_vehicles_today": int(total_vehicles_today),
        "avg_waiting_time": float(avg_waiting_time),
        "peak_hour": str(peak_hour),
        "total_vehicles_recorded": int(total_vehicles_recorded)
    }

def get_peak_hour_trends(filter_type):
    with file_lock:
        df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    if filter_type == "day":
        df["Hour"] = df["Timestamp"].dt.hour
        grouped = df.groupby("Hour")["Vehicle Count"].sum()
    elif filter_type == "week":
        df["Day"] = df["Timestamp"].dt.day
        grouped = df.groupby("Day")["Vehicle Count"].sum()
    else:
        df["Week"] = df["Timestamp"].dt.isocalendar().week
        grouped = df.groupby("Week")["Vehicle Count"].sum()

    return {"labels": grouped.index.tolist(), "values": grouped.values.tolist()}
