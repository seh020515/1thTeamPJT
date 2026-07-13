from flask import request, jsonify                          # request=들어온 요청 읽기, jsonify=파이썬→JSON 변환
from . import data_alert_bp                                  # 같은 폴더 __init__.py에서 만든 주소 묶음 가져오기
from utils.log_manager import save_log, load_logs           # 내가 만든 log_manager의 저장/읽기 함수
from utils.image_manager import save_image                  # 내가 만든 image_manager의 이미지 저장 함수
from utils.stats_manager import count_today, count_by_hour, count_by_type, count_total   # 통계 함수들
from utils.location_manager import save_location, get_location


# ① 감지결과 받아 저장  (서은호 → 나 : POST /log)
@data_alert_bp.route("/log", methods=["POST"])              # 누가 /log 주소로 POST를 보내면 아래 함수 실행
def create_log():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON 데이터가 필요합니다."}), 400

    saved = save_log(data)
    return jsonify(saved), 201


# ② 로그 목록 조회
@data_alert_bp.route("/log", methods=["GET"])
def get_logs():
    return jsonify(load_logs()), 200


# ③ 캡처 이미지 저장
@data_alert_bp.route("/image", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "image 파일이 필요합니다."}), 400

    file = request.files["image"]
    drone_id = request.form.get("drone_id")
    location = request.form.get("location")

    if file.filename == "":
        return jsonify({"error": "파일명이 비어있습니다."}), 400

    filepath = save_image(file, drone_id, location)

    return jsonify({
        "filepath": filepath
    }), 201


# ④ 알림 트리거
@data_alert_bp.route("/alert", methods=["POST"])
def send_alert():
    data = request.get_json()

    if not data:
        return jsonify({"error": "알림 데이터가 필요합니다."}), 400

    return jsonify({
        "alert": True,
        "data": data
    }), 200


# ⑤ 통계 조회
@data_alert_bp.route("/stats", methods=["GET"])
def get_stats():
    return jsonify({
        "today_count": count_today(),
        "total_count": count_total(),
        "by_hour": count_by_hour(),
        "by_type": count_by_type()
    }), 200


# ⑥ 드론 위치 저장
@data_alert_bp.route("/location", methods=["POST"])
def post_location():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON 데이터가 필요합니다."}), 400

    lat = data.get("lat")
    lng = data.get("lng")

    if lat is None or lng is None:
        return jsonify({"error": "lat, lng 필요"}), 400

    saved = save_location(lat, lng)

    return jsonify(saved), 200


# ⑦ 드론 위치 조회
@data_alert_bp.route("/location", methods=["GET"])
def get_location_api():
    return jsonify(get_location()), 200
