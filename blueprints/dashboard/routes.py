from flask import Blueprint, render_template, request, Response, url_for, redirect
import requests
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


@dashboard_bp.route("/")
def dashboard():
    return render_template(
        "dashboard/dashboard.html",
        today_count=0,
        warning_message="현재 위험 없음",
        logs=[]
    )


@dashboard_bp.route("/live")
def live():
    return render_template(
        "dashboard/live.html",
        detect_time="감지 없음"
    )


@dashboard_bp.route("/logs")
def logs():

    log_type = request.args.get("type", "all")

    logs = load_logs()

    if log_type != "all":
        logs = [
            log for log in logs
            if log["type"] == log_type
        ]

    return render_template(
        "dashboard/logs.html",
        logs=logs,
        selected_type=log_type
    )


@dashboard_bp.route("/statistics")
def statistics():
    return render_template(
        "dashboard/statistics.html",
        today_count=0,
        week_count=0,
        month_count=0,
        total_count=0,
        labels=["월", "화", "수", "목", "금"],
        values=[0, 0, 0, 0, 0],
        type_labels=["침입", "움직임", "기타"],
        type_values=[0, 0, 0],
        hour_labels=["00시", "03시", "06시", "09시", "12시", "15시", "18시", "21시"],
        hour_values=[0, 1, 2, 1, 3, 5, 2, 1]
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
        "danger_zone_enabled": request.form.get("danger_zone_enabled"),
        "sensitivity": request.form.get("sensitivity"),
        "alert_enabled": request.form.get("alert_enabled"),
        "save_video": request.form.get("save_video")
    }

    save_settings(settings_data)

    return redirect(url_for("dashboard.settings"))


# ★ 유성 ESP32-CAM 스트림 주소
#   핫스팟 재연결 시 IP가 바뀔 수 있음 -> 그럴 땐 이 줄만 새 IP로 수정하면 됨
ESP32_STREAM_URL = "http://192.168.137.156:81/stream"


@dashboard_bp.route("/video_feed")
def video_feed():

    try:
        # 실제 ESP32-CAM 스트림을 그대로 받아서 대시보드로 전달(프록시)
        resp = requests.get(ESP32_STREAM_URL, stream=True, timeout=5)
        return Response(
            resp.iter_content(chunk_size=1024),
            content_type=resp.headers.get(
                "Content-Type", "multipart/x-mixed-replace; boundary=frame"
            )
        )
    
    except requests.exceptions.RequestException as e:
        print("[video_feed 에러]", e)
    
        # 카메라가 꺼져있거나 연결이 안 될 때는 더미 화면으로 자동 대체 (서버가 죽지 않도록 방어)
        frame = """
        <svg xmlns="http://www.w3.org/2000/svg" width="900" height="500">
            <rect width="100%" height="100%" fill="#020617"/>
            <text x="50%" y="45%" text-anchor="middle" fill="#38bdf8" font-size="32">
                DRONE CAMERA READY
            </text>
            <text x="50%" y="55%" text-anchor="middle" fill="#94a3b8" font-size="18">
                ESP32-CAM 연결 대기중
            </text>
        </svg>
        """.encode("utf-8")
        return Response(frame, mimetype="image/svg+xml")


@dashboard_bp.route("/test/add_log")
def test_add_log():

    add_log(
        log_type="intrusion",
        type_name="위험구역 침입",
        location="A구역",
        status="처리 완료"
    )

    return "OK"
