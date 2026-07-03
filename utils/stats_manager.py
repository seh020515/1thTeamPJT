from utils.log_manager import load_logs, filter_today   # 내가 만든 log_manager에서 두 함수 재사용

'''
함수
    count_today    오늘 감지 건수 세기      -> 가희 "오늘 감지 건수" 카드
    count_by_hour  시간대별 건수 세기       -> 가희 시간대별 그래프
    count_by_type  유형별 건수 세기         -> 가희 "감지 유형별 비율" 파이차트
    count_total    전체 누적 건수 세기      -> 가희 "전체 감지 건수" 카드
'''

def count_today():                      # 1. 오늘 몇 건인지 세는 함수
    return len(filter_today())          # filter_today()가 준 오늘치 목록의 길이(개수) 반환


def count_by_hour():                    # 2. 시간대(00~23시)별로 몇 건인지 세는 함수
    logs = load_logs()                  # 전체 로그를 전부 불러온다
    result = {}                         # {"시": 횟수} 형태로 채울 빈 딕셔너리

    for log in logs:                    # 로그를 한 개씩 반복
        hour = log["time"][11:13]       # "2026-07-02 14:31:00"에서 시(14)만 잘라냄
        result[hour] = result.get(hour, 0) + 1   # 그 시간 칸을 +1

    return result                       # 예: {"14": 3, "15": 5}


def count_by_type():                    # 3. 유형(침입/익수/구조요청)별로 세는 함수
    logs = load_logs()                  # 전체 로그 불러오기
    result = {}                         # {"유형": 횟수} 담을 빈 딕셔너리

    for log in logs:                    # 로그 한 개씩 반복
        # ★ 화면 파이차트는 한글 라벨이 필요하므로 type_name 기준으로 센다
        #   (없으면 type 코드값으로 대체 → 예전 형식 로그도 안전하게 처리)
        type_name = log.get("type_name", log.get("type", "기타"))
        result[type_name] = result.get(type_name, 0) + 1   # 그 유형 칸을 +1

    return result                       # 예: {"위험구역 침입": 8, "익수": 3}


def count_total():                      # 4. 지금까지 쌓인 전체 건수를 세는 함수
    return len(load_logs())             # 전체 로그 목록의 길이(개수) 반환


# 테스트 (이 파일을 직접 실행할 때만 아래가 돈다)
if __name__ == "__main__":
    print("오늘 건수 :", count_today())
    print("시간대별 :", count_by_hour())
    print("유형별   :", count_by_type())
    print("전체 건수 :", count_total())
