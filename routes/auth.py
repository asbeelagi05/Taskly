from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models.user import User

auth = Blueprint("auth", __name__)


# ----------------------------
# Register
# ----------------------------
@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already exists"

        # Create new user
        user = User(
            name=name,
            email=email,
            phone=phone,
            password=password,
            role=role
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


# ----------------------------
# Login
# ----------------------------
@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        # Find user by email
        user = User.query.filter_by(email=email).first()

        # Verify password
        if user and check_password_hash(user.password, password):

            # Create login session
            login_user(user)

            # Redirect based on role
            if user.role == "customer":
                return redirect(url_for("customer.dashboard"))

            elif user.role == "labour":
                return redirect(url_for("labour.dashboard"))

        return "Invalid Email or Password"

    return render_template("auth/login.html")