from flask import Blueprint, render_template, request, redirect, url_for, session

member_bp = Blueprint(
    "member",
    __name__,
    url_prefix="/member"
)


@member_bp.route("/signin/form")
def signin_form():
    return render_template("member/signin_form.html")


@member_bp.route("/signin", methods=["POST"])
def signin():

    member_id = request.form.get("member_id")
    member_pw = request.form.get("member_pw")

    # 임시 로그인 처리
    session["member_id"] = member_id

    return redirect(url_for("dashboard.dashboard"))


@member_bp.route("/signup/form")
def signup_form():
    return render_template("member/signup_form.html")


@member_bp.route("/signup", methods=["POST"])
def signup():

    member_name = request.form.get("member_name")
    member_id = request.form.get("member_id")
    member_pw = request.form.get("member_pw")
    member_email = request.form.get("member_email")

    # 나중에 DB/JSON 저장 연결
    print(member_name, member_id, member_pw, member_email)

    return redirect(url_for("member.signin_form"))


@member_bp.route("/modify/form")
def modify_form():

    member = {
        "member_name": "김가희",
        "member_id": "heechuchu",
        "member_email": "test@test.com"
    }

    return render_template(
        "member/modify_form.html",
        member=member
    )


@member_bp.route("/modify", methods=["POST"])
def modify():

    member_name = request.form.get("member_name")
    member_email = request.form.get("member_email")
    member_pw = request.form.get("member_pw")

    print(member_name, member_email, member_pw)

    return redirect(url_for("dashboard.dashboard"))


@member_bp.route("/signout")
def signout():

    session.clear()

    return redirect(url_for("index"))