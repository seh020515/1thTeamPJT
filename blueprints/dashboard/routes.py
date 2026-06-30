from flask import Blueprint, render_template

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
    return render_template(
        "dashboard/logs.html",
        logs=[]
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
        type_values=[0, 0, 0]
    )


@dashboard_bp.route("/settings")
def settings():
    return render_template("dashboard/settings.html")


@dashboard_bp.route("/settings/save", methods=["POST"])
def settings_save():
    return "설정 저장 완료"


@dashboard_bp.route("/video_feed")
def video_feed():
    return ""