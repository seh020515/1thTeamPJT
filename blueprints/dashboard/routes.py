from flask import Blueprint, render_template, request, Response, url_for, redirect, jsonify

from drone_manager import DroneManager

from utils.json_manager import (
    load_settings,
    save_settings,
    load_logs,
    add_log
)

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)

drone = DroneManager()
settings = load_settings()

drone.system_settings["danger_detection"] = (
    "ON"
    if settings["danger_zone_enabled"] == "on"
    else "OFF"
)

drone.system_settings["alert_mode"] = (
    "ALL"
    if settings["alert_enabled"] == "on"
    else "MUTE"
)

@dashboard_bp.route("/")
def dashboard():
    logs = load_logs()

    return render_template(
        "dashboard/dashboard.html",
        today_count=len(logs),
        warning_message="위험 감지 중" if drone.is_danger else "현재 위험 없음",
        logs=logs[:5]
    )


@dashboard_bp.route("/live")
def live():
    return render_template(
        "dashboard/live.html",
        detect_time="감지 중" if drone.is_danger else "감지 없음"
    )


@dashboard_bp.route("/logs")
def logs():
    log_type = request.args.get("type", "all")

    logs = load_logs()

    if log_type != "all":
        logs = [
            log for log in logs
            if log.get("type") == log_type
        ]

    return render_template(
        "dashboard/logs.html",
        logs=logs,
        selected_type=log_type
    )


@dashboard_bp.route("/statistics")
def statistics():
    logs = load_logs()

    intrusion_count = len([
        log for log in logs
        if log.get("type") == "intrusion" or log.get("type") == "위험진입"
    ])

    return render_template(
        "dashboard/statistics.html",
        today_count=len(logs),
        week_count=len(logs),
        month_count=len(logs),
        total_count=len(logs),
        labels=["월", "화", "수", "목", "금"],
        values=[0, 0, 0, 0, len(logs)],
        type_labels=["침입", "움직임", "기타"],
        type_values=[intrusion_count, 0, 0],
        hour_labels=["00시", "03시", "06시", "09시", "12시", "15시", "18시", "21시"],
        hour_values=[0, 0, 0, 0, 0, 0, 0, 0]
    )


@dashboard_bp.route("/settings")
def settings():
    settings_data = load_settings()

    return render_template(
        "dashboard/settings.html",
        settings=settings_data
    )


@dashboard_bp.route("/settings/save", methods=["POST"])
def settings_save():
    settings_data = {
        "danger_zone_enabled": request.form.get("danger_zone_enabled", "off"),
        "sensitivity": request.form.get("sensitivity", "middle"),
        "alert_enabled": request.form.get("alert_enabled", "off"),
        "save_video": request.form.get("save_video", "off")
    }

    save_settings(settings_data)

    drone.system_settings["danger_detection"] = (
        "ON" if settings_data["danger_zone_enabled"] == "on" else "OFF"
    )

    drone.system_settings["alert_mode"] = (
        "ALL" if settings_data["alert_enabled"] == "on" else "MUTE"
    )

    return redirect(url_for("dashboard.settings"))


@dashboard_bp.route("/video_feed")
def video_feed():
    return Response(
        drone.generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@dashboard_bp.route("/camera_status")
def camera_status():
    return jsonify({
        "connected": drone.is_connected
    })


@dashboard_bp.route("/danger_status")
def danger_status():
    return jsonify({
        "danger": drone.is_danger
    })


@dashboard_bp.route("/get_settings")
def get_settings():
    return jsonify(drone.system_settings)


@dashboard_bp.route("/update_settings", methods=["POST"])
def update_settings():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "잘못된 요청"
        }), 400

    if "danger_detection" in data:
        drone.system_settings["danger_detection"] = data["danger_detection"]

    if "alert_mode" in data:
        drone.system_settings["alert_mode"] = data["alert_mode"]

    return jsonify({
        "success": True
    })


@dashboard_bp.route("/test/add_log")
def test_add_log():
    add_log(
        log_type="intrusion",
        type_name="위험구역 침입",
        location="A구역",
        status="처리 완료"
    )

    return "OK"