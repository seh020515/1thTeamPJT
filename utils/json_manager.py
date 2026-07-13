import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DB_DIR = os.path.join(BASE_DIR, "db")
SETTINGS_FILE = os.path.join(DB_DIR, "settings.json")
LOG_FILE = os.path.join(DB_DIR, "detection_logs.json")
DANGER_ZONE_FILE = os.path.join(DB_DIR, "danger_zone.json")


def ensure_db_dir():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)


def get_default_settings():
    return {
        "danger_zone_enabled": "on",
        "sensitivity": "middle",
        "alert_enabled": "on",
        "save_video": "off"
    }


def get_default_logs():
    return []


def get_default_danger_zone():
    return {
        "x1": 250,
        "y1": 100,
        "x2": 550,
        "y2": 350
    }


def load_json(file_path, default_data):
    ensure_db_dir()

    if not os.path.exists(file_path):
        save_json(file_path, default_data)
        return default_data

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            return default_data

        return data

    except:
        save_json(file_path, default_data)
        return default_data


def save_json(file_path, data):
    ensure_db_dir()

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# =========================
# 설정
# =========================

def load_settings():
    return load_json(SETTINGS_FILE, get_default_settings())


def save_settings(settings):
    save_json(SETTINGS_FILE, settings)


# =========================
# 로그
# =========================

def load_logs():
    return load_json(LOG_FILE, get_default_logs())


def save_logs(logs):
    save_json(LOG_FILE, logs)


def add_log(log_type, type_name, location, status):
    logs = load_logs()

    new_log = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": log_type,
        "type_name": type_name,
        "location": location,
        "status": status
    }

    logs.insert(0, new_log)
    save_logs(logs)

    return new_log


# =========================
# YOLO 감지 로그용
# =========================

def load_intrusion_logs():
    return load_logs()


def save_intrusion_logs(logs):
    save_logs(logs)


# =========================
# 위험구역 좌표
# =========================

def load_danger_zone():
    return load_json(DANGER_ZONE_FILE, get_default_danger_zone())


def save_danger_zone(zone):
    save_json(DANGER_ZONE_FILE, zone)