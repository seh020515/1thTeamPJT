from flask import request, jsonify
from . import data_alert_bp

from utils.log_manager import save_log, load_logs
from utils.image_manager import save_image
from utils.stats_manager import (
    count_today,
    count_by_hour,
    count_by_type,
    count_total
)
from utils.location_manager import save_location, get_location


# ① 감지 결과 저장
@data_alert_bp.route("/log", methods=["POST"])
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