from flask import Flask, render_template
from blueprints.dashboard.routes import dashboard_bp
from blueprints.member.routes import member_bp
from blueprints.data_alert import data_alert_bp
app = Flask(__name__)

app.secret_key = "drone-secret-key"

app.register_blueprint(dashboard_bp)
app.register_blueprint(member_bp)
app.register_blueprint(data_alert_bp, url_prefix="/data")

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)