import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MEMBER_FILE = os.path.join(BASE_DIR, "db", "members.json")
INTRUSION_LOG_FILE = os.path.join(BASE_DIR, "db", "intrusion_log.json")

def load_members():

    try:
        with open(MEMBER_FILE, encoding = 'utf-8') as f:
            return json.load(f)

    except:
        return {}

def save_members(members):

    with open(MEMBER_FILE, "w", encoding='utf-8') as f:
        json.dump(
            members,
            f,
            ensure_ascii = False,
            indent = 4
        )

def load_intrusion_logs():

    try:
        with open(INTRUSION_LOG_FILE, encoding='utf-8') as f:
            return json.load(f)

    except:
        return []


def save_intrusion_logs(logs):

    with open(INTRUSION_LOG_FILE, "w", encoding='utf-8') as f:
        json.dump(
            logs,
            f,
            ensure_ascii=False,
            indent=4
        )

DANGER_ZONE_FILE = os.path.join(BASE_DIR, "db", "danger_zone.json")

def load_danger_zone():
    try:
        with open(DANGER_ZONE_FILE, encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"x1": 250, "y1": 100, "x2": 550, "y2": 350}

def save_danger_zone(zone):
    with open(DANGER_ZONE_FILE, "w", encoding='utf-8') as f:
        json.dump(zone, f, ensure_ascii=False, indent=4)