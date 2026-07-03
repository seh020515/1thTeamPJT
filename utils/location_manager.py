import json
import os

LOCATION_FILE = os.path.join(os.path.dirname(__file__), 'data', 'location.json')

def save_location(lat, lng):
    data = {"lat": lat, "lng": lng}
    try:
        os.makedirs(os.path.dirname(LOCATION_FILE), exist_ok=True)   # ★ 추가: data 폴더 없으면 자동 생성
        with open(LOCATION_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        print(f"위치 저장 실패: {e}")
        return False

def get_location():
    if not os.path.exists(LOCATION_FILE):
        return {"lat": None, "lng": None}
    try:
        with open(LOCATION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"lat": None, "lng": None}