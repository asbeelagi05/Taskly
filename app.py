from flask import Flask, redirect, render_template, url_for
from flask_login import current_user
from flask import Flask, render_template
from config import Config

from extensions import db, login_manager

from routes.auth import auth
from routes.customer import customer
from routes.labour import labour
from routes.jobs import jobs
from routes.profile import profile

from models.user import User
from models.job import Job
from models.application import Application
from models.notification import Notification

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)

app.register_blueprint(auth)
app.register_blueprint(customer)
app.register_blueprint(labour)
app.register_blueprint(jobs)
app.register_blueprint(profile)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    if current_user.is_authenticated:
        if current_user.role == "customer":
            return redirect(url_for("customer.dashboard"))

        return redirect(url_for("labour.dashboard"))

    return redirect(url_for("auth.login"))


@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)