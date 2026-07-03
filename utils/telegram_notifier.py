import os              # 환경변수(비밀값) 읽기용
import requests         # 텔레그램 서버에 HTTP 요청 보내는 모듈

'''
텔레그램 봇 알림 모듈
    send_telegram_alert(log_data)  ->  위험 감지 로그를 텔레그램 메시지로 발송

★ 준비물 (아래 두 값은 코드에 직접 적지 않고 환경변수로 넣는다 - 유출 방지)
    1) BOT_TOKEN : @BotFather 에게 /newbot 하면 발급되는 토큰
    2) CHAT_ID   : 알림 받을 사람/방의 고유 ID (아래 "발급받는 법" 참고)

★ 발급받는 법
    1. 텔레그램에서 @BotFather 검색 -> /newbot -> 봇 이름 정하기
       -> "Use this token" 뒤에 나오는 긴 문자열이 BOT_TOKEN
    2. 방금 만든 내 봇과 대화창을 열고 아무 메시지나 하나 보낸다 (예: "hi")
    3. 브라우저에서 아래 주소 접속 (BOT_TOKEN 자리만 내 토큰으로 교체)
       https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
    4. 결과 JSON 안에서 "chat":{"id": 123456789 ...} 의 숫자가 CHAT_ID

★ 환경변수 설정법 (터미널에서, venv 켠 상태로)
    PowerShell : $env:TG_BOT_TOKEN="여기에토큰"; $env:TG_CHAT_ID="여기에챗아이디"
    이후 python app.py 를 "같은 터미널"에서 실행해야 값이 적용됨
'''

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TG_CHAT_ID", "")

# 유형별로 다르게 보일 이모지 (메시지 가독성용)
TYPE_EMOJI = {
    "intrusion": "🚧",
    "drowning": "🌊",
    "rescue": "🆘",
}


def send_telegram_alert(log_data):
    """
    log_data: log_manager.save_log()가 저장한 dict (type, type_name, time, location, confidence 등)
    반환값: True(발송 성공) / False(발송 실패 또는 설정 안 됨)
    """

    if not BOT_TOKEN or not CHAT_ID:
        # 토큰/챗아이디가 아직 설정 안 된 상태 -> 서버가 죽지 않도록 조용히 실패 처리
        print("[텔레그램] BOT_TOKEN 또는 CHAT_ID가 설정되지 않아 알림을 건너뜁니다.")
        return False

    emoji = TYPE_EMOJI.get(log_data.get("type"), "⚠️")
    type_name = log_data.get("type_name", log_data.get("type", "알 수 없음"))
    location = log_data.get("location", "위치 미상")
    time_str = log_data.get("time", "")
    confidence = log_data.get("confidence")
    conf_str = f"{confidence*100:.0f}%" if isinstance(confidence, (int, float)) else "N/A"

    message = (
        f"{emoji} [해수욕장 안전 알림]\n"
        f"유형: {type_name}\n"
        f"위치: {location}\n"
        f"시간: {time_str}\n"
        f"신뢰도: {conf_str}"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}

    try:
        res = requests.post(url, data=payload, timeout=5)
        # 텔레그램이 에러를 줘도(예: 잘못된 토큰) 여기서 예외로 서버 전체가 죽으면 안 되므로 status_code만 확인
        if res.status_code == 200:
            return True
        print(f"[텔레그램] 발송 실패: {res.status_code} {res.text}")
        return False
    except requests.exceptions.RequestException as e:
        # 네트워크 문제 등으로 텔레그램 서버에 연결 자체가 안 될 때도 서버가 죽지 않도록 방어
        print(f"[텔레그램] 연결 오류: {e}")
        return False


# 테스트 (이 파일을 직접 실행할 때만 동작)
if __name__ == "__main__":
    sample = {
        "type": "rescue",
        "type_name": "구조요청",
        "time": "2026-07-02 15:00:00",
        "location": "C구역",
        "confidence": 0.93,
    }
    ok = send_telegram_alert(sample)
    print("발송 결과:", ok)
