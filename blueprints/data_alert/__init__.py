from flask import Blueprint            # Flask의 Blueprint(주소 묶음) 도구 불러오기

# "data_alert"라는 이름표를 붙인 주소 묶음(Blueprint)을 하나 만든다
# __name__ = 지금 이 폴더 위치를 Flask에게 알려주는 값
data_alert_bp = Blueprint("data_alert", __name__)

# 같은 폴더의 routes.py를 불러와서 위 묶음(data_alert_bp)에 실제 주소들을 등록한다
# ★ 반드시 맨 아래에 둬야 함 (data_alert_bp가 먼저 만들어진 뒤에 routes가 그걸 가져다 쓰기 때문)
from . import routes