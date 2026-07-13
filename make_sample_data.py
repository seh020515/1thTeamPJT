import json
import random
from datetime import datetime, timedelta

'''
발표·시연용 샘플 데이터 생성 스크립트
    - 최근 3일치 감지 로그를 현실적인 분포로 만들어 db/detection_logs.json에 채워넣는다
    - 시간대별 그래프(오전 한산, 낮 12~16시 집중), 유형별 파이차트, 오늘 건수 카드가
      전부 "0건"이 아니라 실제 데이터로 보이도록 하기 위함
    - 이 파일을 직접 실행(python make_sample_data.py)하면 db/detection_logs.json이 덮어써짐
      ★ 실제 팀원 데이터가 이미 쌓여있다면 실행 전 백업 권장
'''

LOG_PATH = "db/detection_logs.json"

TYPES = [
    ("intrusion", "위험구역 침입", 0.55),   # (코드, 한글명, 발생비중)
    ("drowning", "익수", 0.20),
    ("rescue", "구조요청", 0.10),
]
# 나머지 0.15는 낮은 신뢰도의 오탐성 침입으로 채워 "필터링 전/후" 시연에 쓸 수 있게 함

LOCATIONS = ["A구역", "B구역", "C구역"]

# 시간대별 가중치: 해수욕장이므로 오전엔 한산, 낮 12~17시에 사람이 몰림
HOUR_WEIGHTS = {
    6: 1, 7: 1, 8: 2, 9: 3, 10: 5, 11: 7,
    12: 9, 13: 10, 14: 10, 15: 9, 16: 8, 17: 6,
    18: 4, 19: 2, 20: 1,
}


def weighted_hour():
    hours = list(HOUR_WEIGHTS.keys())
    weights = list(HOUR_WEIGHTS.values())
    return random.choices(hours, weights=weights, k=1)[0]


def pick_type():
    r = random.random()
    cum = 0
    for code, name, weight in TYPES:
        cum += weight
        if r <= cum:
            return code, name
    return TYPES[0][0], TYPES[0][1]  # fallback


def make_logs(days_back=3, per_day_range=(8, 14)):
    logs = []
    today = datetime.now().date()
    log_id = 1

    for day_offset in range(days_back, -1, -1):  # 오래된 날짜 -> 오늘 순
        day = today - timedelta(days=day_offset)
        count = random.randint(*per_day_range)

        for _ in range(count):
            hour = weighted_hour()
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            dt = datetime(day.year, day.month, day.day, hour, minute, second)

            code, name = pick_type()
            # 침입 유형의 15%는 오탐성 저신뢰도로 만들어 confidence 필터 시연용
            if code == "intrusion" and random.random() < 0.15:
                confidence = round(random.uniform(0.30, 0.55), 2)
            else:
                confidence = round(random.uniform(0.75, 0.99), 2)

            logs.append({
                "id": log_id,
                "type": code,
                "type_name": name,
                "time": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "location": random.choice(LOCATIONS),
                "confidence": confidence,
                "status": random.choice(["미처리", "처리 완료", "확인중"]),
            })
            log_id += 1

    # 최신순(맨 앞) 정렬 - log_manager.save_log의 insert(0, ...) 방식과 동일하게
    logs.sort(key=lambda x: x["time"], reverse=True)
    for i, log in enumerate(logs, start=1):
        log["id"] = i
    return logs


if __name__ == "__main__":
    data = make_logs()
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"샘플 로그 {len(data)}건 생성 완료 -> {LOG_PATH}")

    # 요약 출력
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_count = sum(1 for d in data if d["time"].startswith(today_str))
    by_type = {}
    for d in data:
        by_type[d["type_name"]] = by_type.get(d["type_name"], 0) + 1
    print("오늘 건수:", today_count)
    print("유형별:", by_type)
