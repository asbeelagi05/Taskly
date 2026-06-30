from flask import Blueprint
from flask_login import login_required, current_user

labour = Blueprint("labour", __name__)


@labour.route("/labour/dashboard")
@login_required
def dashboard():

    return f"""
    <h1>Labour Dashboard</h1>

    <p>Welcome {current_user.name}</p>

    <a href="/logout">Logout</a>
    """