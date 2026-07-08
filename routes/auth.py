import re

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models.user import User

auth = Blueprint("auth", __name__)
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$")


def dashboard_redirect():
    if current_user.role == "customer":
        return redirect(url_for("customer.dashboard"))

    if current_user.role == "labour":
        return redirect(url_for("labour.dashboard"))

    return redirect(url_for("auth.login"))


# ----------------------------
# Register
# ----------------------------
@auth.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return dashboard_redirect()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        raw_password = request.form["password"]
        role = request.form["role"]

        if not PASSWORD_REGEX.match(raw_password):
            flash(
                "Password must be at least 8 characters and include uppercase, lowercase, number, and special character.",
                "danger",
            )
            return redirect(url_for("auth.register"))

        password = generate_password_hash(raw_password)

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


@auth.route("/check-email", methods=["GET"])
def check_email():
    email = request.args.get("email", "").strip().lower()

    if not email:
        return jsonify({"exists": False})

    existing_user = User.query.filter_by(email=email).first()
    return jsonify({"exists": existing_user is not None})


# ----------------------------
# Login
# ----------------------------
@auth.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return dashboard_redirect()

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        if not PASSWORD_REGEX.match(password):
            flash(
                "Incorrect password. Use at least 8 characters with uppercase, lowercase, number, and special character.",
                "danger",
            )
            return redirect(url_for("auth.login"))

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

        flash("Invalid Email or Password", "danger")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html")
# ----------------------------
# Logout
# ----------------------------
@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.", "success")

    return redirect(url_for("auth.login"))