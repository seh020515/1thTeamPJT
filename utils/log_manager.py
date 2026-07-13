import json  # json 읽기 쓰기 모듈 불러오기
import os    # 파일·폴더 존재확인 모듈
from datetime import datetime  # 오늘 날짜 가져오기

# ★ 가희 json_manager와 같은 파일을 쓰도록 통일 (detection_logs.json)
LOG_PATH = "db/detection_logs.json"      # 로그 저장 경로

# ★ 감지 유형 코드표 (서은호·가희·나 3명 공유)
#   서은호(YOLO)는 영문 코드(type)로 보내고, 화면 표시용 한글(type_name)은 여기서 자동 변환
TYPE_NAMES = {
    "intrusion": "위험구역 침입",
    "drowning": "익수",
    "rescue": "구조요청",
}

'''
함수
    save_log     새 로그 json파일에 저장
    load_logs    저장된 로그 전체 읽기
    filter_today 오늘날짜 필터
'''

def save_log(log_data):    # 1. 저장 함수
    logs = load_logs()      # 기존 로그 전부 불러오기

    # ★ 가희 구조에 맞춰 필드 보정 (없으면 기본값 채움) --------------------
    log_type = log_data.get("type", "intrusion")          # 영문 코드 (예: intrusion)
    log_data["type"] = log_type
    # type_name이 안 왔으면 코드표에서 한글 이름 자동 변환
    log_data.setdefault("type_name", TYPE_NAMES.get(log_type, log_type))
    log_data.setdefault("location", "미지정")              # 구역 (예: A구역)
    log_data.setdefault("status", "미처리")                # 처리 상태
    log_data.setdefault("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # 시간 없으면 현재시각
    # ------------------------------------------------------------------

    log_data["id"] = len(logs) + 1      # id값 자동부여 1씩 증가

    # ★ 가희와 동일하게 최신 로그를 맨 앞에 넣음 (insert 0)
    logs.insert(0, log_data)

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    # w=쓰기모드, ensure_ascii=False 한글 깨짐방지, indent=2 들여쓰기

    return log_data   # 저장한 내용 돌려줌


def load_logs():    # 2. 읽기 함수
    if not os.path.exists(LOG_PATH):        # 파일이 존재하지 않으면
        return []                           # 빈 목록 반환 (error 방지)

    with open(LOG_PATH, "r", encoding="utf-8") as f:    # 읽기모드로 열고
        try:
            return json.load(f)         # 파이썬 리스트로 변환 후 반환
        except json.JSONDecodeError:    # 내용이 깨졌거나 비었을 때
            return []                   # 에러 시 빈 리스트 반환


def filter_today():         # 오늘 날짜 로그만 골라 반환
    logs = load_logs()      # 전체 로그 불러오기
    today = datetime.now().strftime("%Y-%m-%d")   # 오늘 날짜를 "2026-07-02" 형태로
    return [log for log in logs if log["time"].startswith(today)]
    # 각 로그의 time이 오늘 날짜로 시작하는 것만 골라 새 목록으로


# 테스트
if __name__ == "__main__":
    save_log({
        "type": "intrusion",
        "time": "2026-07-02 14:31:00",
        "confidence": 0.92,
        "location": "A구역",
    })
    print(load_logs())