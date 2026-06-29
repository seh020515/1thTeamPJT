import json  #json 읽기 쓰기 모듈 불러오기
import os   # 파일폴더 존재확인 모듈
from datetime import datetime  #오늘 날짜 가져오기

LOG_PATH = "db/intrusion_log.json"      #로그 저장 경로


'''
함수
  save_log 새로그 json파일에 저장
load_logs 저장된 로그 전체읽기
filter_today  오늘날짜 필터
'''
def save_log(log_data):    # 1. 저장함수
    logs = load_logs()      #기존 로그 전부 불러오기(load_logs 함수사용)

    logs.append(log_data)       #새 로그를 맨뒤추가

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    #목록전체 파일에 다시저장
    # w = 쓰기모드,  ensure_ascii=False 한글 깨짐방지
    # indent=2 들여쓰기
    # as f = 파일 객체를 f 이름으로 사용

    return log_data   #저장한 내용 돌려줌

def load_logs():    # 2.읽기 함수

    if not os.path.exists(LOG_PATH):        #파일이 존재하지않으면
        return []                           # 빈 목록을 돌려준다(error 방지)
    
    with open(LOG_PATH, "r", encoding="utf-8") as f:    #읽기모드로 열고     
        try:
            return json.load(f)         #파이선 리스트로 변환후 반환
        except json.JSONDecodeError:    #내용이 문제(깨지거나 비었을때)있으면 발생하는 에러
            return []
    
def filter_today():
    logs = load_logs()      #전체 로그 불러오기

    today = datetime.now().strftime("%Y-%m-%d")
    #오늘 날짜를 "2026-06-29" 형태로

    return [log for log in logs if log["time"].startswith(today)]
    #각 로그의 time이 오늘 날짜로 시작하는 것만 골라 새목록 만들기

if __name__ == "__main__":
    save_log({"type": "위험구역 침입", "time": "2026-07-01 14:31:00", "confidence": 0.92})
    print(load_logs())




