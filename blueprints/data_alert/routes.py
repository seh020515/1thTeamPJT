from flask import request, jsonify                          # request=들어온 요청 읽기, jsonify=파이썬→JSON 변환
from . import data_alert_bp                                  # 같은 폴더 __init__.py에서 만든 주소 묶음 가져오기
from utils.log_manager import save_log, load_logs           # 내가 만든 log_manager의 저장/읽기 함수
from utils.image_manager import save_image                  # 내가 만든 image_manager의 이미지 저장 함수
from utils.stats_manager import count_today, count_by_hour, count_by_type, count_total   # 통계 함수들
from utils.telegram_notifier import send_telegram_alert     # ★ 8단계: 텔레그램 자동 알림 함수
from utils.location_manager import save_location, get_location

# ★ 이 신뢰도(confidence) 미만이면 오탐일 가능성이 있어 텔레그램은 생략 (화면 로그에는 그대로 남음)
ALERT_CONFIDENCE_THRESHOLD = 0.6


# ① 감지결과 받아 저장  (서은호 → 나 : POST /log)
@data_alert_bp.route("/log", methods=["POST"])              # 누가 /log 주소로 POST를 보내면 아래 함수 실행
def create_log():
    data = request.get_json()                              # 서은호가 보낸 JSON 본문을 파이썬 딕셔너리로 꺼내기
    saved = save_log(data)                                 # log_manager.save_log로 파일에 저장(자동으로 id도 붙음)

    # ★ 8단계: 저장 성공 + 신뢰도 충분하면 텔레그램으로 자동 알림
    #   send_telegram_alert 내부에서 실패해도 예외를 던지지 않으므로 /log 응답 자체는 항상 정상 반환됨
    confidence = saved.get("confidence", 0)
    if confidence >= ALERT_CONFIDENCE_THRESHOLD:
        send_telegram_alert(saved)

    return jsonify(saved), 201                             # 저장된 내용을 돌려줌, 201=만들기 성공 상태코드


# ② 로그 목록 반환  (나 → 가희 : GET /log)
@data_alert_bp.route("/log", methods=["GET"])              # /log 주소로 GET을 보내면 아래 함수 실행
def get_logs():
    return jsonify(load_logs())                            # 저장된 로그 전체를 JSON으로 만들어 돌려줌


# ③ 캡처 사진 받아 저장  (황유성 → 나 : POST /image)
@data_alert_bp.route("/image", methods=["POST"])           # /image 주소로 POST(파일 업로드)가 오면 실행
def upload_image():
    file = request.files["image"]                         # 업로드된 파일 중 "image" 이름의 파일 꺼내기
    drone_id = request.form.get("drone_id")               # 파일과 함께 온 드론 번호(폼 데이터) 꺼내기
    location = request.form.get("location")               # 파일과 함께 온 구역명(폼 데이터) 꺼내기
    filepath = save_image(file, drone_id, location)       # image_manager.save_image로 저장, 저장경로 받기
    return jsonify({"filepath": filepath}), 201           # 저장된 경로를 돌려줌, 201=만들기 성공


# ④ 브라우저 알림 트리거  (서은호 → 나 → 가희 화면 : POST /alert)
@data_alert_bp.route("/alert", methods=["POST"])           # /alert 주소로 POST가 오면 실행
def send_alert():
    data = request.get_json()                             # 서은호가 보낸 위험 상황 JSON 꺼내기
    # 지금 단계에서는 받은 내용을 그대로 돌려준다 (실제 화면 알림 표시는 가희와 협의해서 붙임)
    return jsonify({"alert": True, "data": data})         # alert=True(알림 발생) 신호 + 원본 데이터 함께 반환


# ⑤ 통계 반환  (나 → 가희 그래프 : GET /stats)
@data_alert_bp.route("/stats", methods=["GET"])            # /stats 주소로 GET이 오면 실행
def get_stats():
    return jsonify({                                      # 통계 4종을 하나의 JSON으로 묶어서 반환
        "today_count": count_today(),                     # 오늘 감지 건수
        "total_count": count_total(),                     # 전체 누적 건수
        "by_hour": count_by_hour(),                       # 시간대별 건수 {"14": 3, ...}
        "by_type": count_by_type()                        # 유형별 건수 {"익수": 2, ...}
    })

# ⑥ 드론 위치 저장  (드론/황유성 → 나 : POST /location)
@data_alert_bp.route("/location", methods=["POST"])
def post_location():
    data = request.get_json()
    lat = data.get("lat")
    lng = data.get("lng")
    if lat is None or lng is None:
        return jsonify({"error": "lat, lng 필요"}), 400
    saved = save_location(lat, lng)
    return jsonify(saved), 200


# ⑦ 드론 위치 조회  (나 → 가희 지도 : GET /location)
@data_alert_bp.route("/location", methods=["GET"])
def get_location_api():
    return jsonify(get_location()), 200