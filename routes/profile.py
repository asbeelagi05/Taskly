from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.user import User
from models.job import Job
from models.application import Application

profile = Blueprint("profile", __name__)


# ----------------------------
# View Profile
# ----------------------------
@profile.route("/profile")
@login_required
def view_profile():

    stats = {}

    if current_user.role == "customer":

        stats["total_jobs"] = Job.query.filter_by(
            customer_id=current_user.id
        ).count()

        stats["open_jobs"] = Job.query.filter_by(
            customer_id=current_user.id,
            status="Open"
        ).count()

    else:

        stats["applications"] = Application.query.filter_by(
            labour_id=current_user.id
        ).count()

        stats["accepted"] = Application.query.filter_by(
            labour_id=current_user.id,
            status="Accepted"
        ).count()

    return render_template(
        "profile.html",
        stats=stats
    )


# ----------------------------
# Edit Profile
# ----------------------------
@profile.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():

    if request.method == "POST":

        current_user.name = request.form["name"]
        current_user.phone = request.form["phone"]
        current_user.email = request.form["email"]

        db.session.commit()

        flash(
            "Profile updated successfully!",
            "success"
        )

        return redirect(url_for("profile.view_profile"))

    return render_template(
        "edit_profile.html"
    )