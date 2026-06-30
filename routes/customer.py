from flask import Blueprint

from flask_login import login_required, current_user

customer = Blueprint("customer", __name__)


@customer.route("/customer/dashboard")
@login_required
def dashboard():

    return f"""
    <h1>Customer Dashboard</h1>

    <h3>Welcome {current_user.name}</h3>

    <a href="/post-job">Post Job</a><br><br>

    <a href="/logout">Logout</a>

    """