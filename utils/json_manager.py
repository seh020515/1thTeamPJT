import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DB_DIR = os.path.join(BASE_DIR, "db")
SETTINGS_FILE = os.path.join(DB_DIR, "settings.json")
LOG_FILE = os.path.join(DB_DIR, "detection_logs.json")

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


def load_settings():
    ensure_db_dir()

    if not os.path.exists(SETTINGS_FILE):
        save_settings(get_default_settings())
        return get_default_settings()

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)

        if not settings:
            return get_default_settings()

        return settings

    except:
        save_settings(get_default_settings())
        return get_default_settings()


def save_settings(settings):
    ensure_db_dir()

    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

def get_default_logs():
    return []


def load_logs():
    ensure_db_dir()

    if not os.path.exists(LOG_FILE):
        save_logs(get_default_logs())
        return get_default_logs()

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)

        if not logs:
            return get_default_logs()

        return logs

    except:
        save_logs(get_default_logs())
        return get_default_logs()


def save_logs(logs):
    ensure_db_dir()

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)


def add_log(log_type, type_name, location, status):
    logs = load_logs()

    from datetime import datetime

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