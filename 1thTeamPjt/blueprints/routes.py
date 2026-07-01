from flask import Blueprint, render_template

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)


@dashboard_bp.route("/")
def dashboard():

    today_count = 3
    warning_message = "현재 위험 없음"

    logs = [
        {
            "time": "2026-06-25 10:30",
            "type": "위험구역 침입",
            "location": "A구역"
        },
        {
            "time": "2026-06-25 11:10",
            "type": "이상 움직임",
            "location": "B구역"
        }
    ]

    return render_template(
        "dashboard/dashboard.html",
        today_count=today_count,
        warning_message=warning_message,
        logs=logs
    )


@dashboard_bp.route("/live")
def live():

    detect_time = "감지 없음"

    return render_template(
        "dashboard/live.html",
        detect_time=detect_time
    )


@dashboard_bp.route("/logs")
def logs():

    logs = [
        {
            "time": "2026-06-25 10:30",
            "type": "위험구역 침입",
            "location": "A구역",
            "status": "처리 완료"
        }
    ]

    return render_template(
        "dashboard/logs.html",
        logs=logs
    )


@dashboard_bp.route("/statistics")
def statistics():

    return render_template(
        "dashboard/statistics.html",
        today_count=3,
        week_count=12,
        month_count=45,
        total_count=120,
        labels=["월", "화", "수", "목", "금"],
        values=[2, 5, 1, 3, 4],
        type_labels=["침입", "움직임", "기타"],
        type_values=[8, 3, 1]
    )


@dashboard_bp.route("/settings")
def settings():

    return render_template("dashboard/settings.html")


@dashboard_bp.route("/settings/save", methods=["POST"])
def settings_save():

    return "설정 저장 완료"