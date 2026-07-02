from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.job import Job
from models.application import Application

profile = Blueprint("profile", __name__)


def build_profile_context(user):
    if user.role == "customer":
        total_jobs = Job.query.filter_by(customer_id=user.id).count()
        open_jobs = Job.query.filter_by(customer_id=user.id, status="Open").count()
        completed_jobs = Job.query.filter_by(customer_id=user.id, status="Completed").count()

        return {
            "profile_title": "Customer Profile",
            "profile_subtitle": "Manage your account details and track the jobs you have posted.",
            "profile_icon": "bi-briefcase-fill",
            "profile_badge": "Customer",
            "display_role": "Customer",
            "primary_action_label": "My Jobs",
            "primary_action_url": url_for("customer.my_jobs"),
            "secondary_action_label": "Edit Profile",
            "secondary_action_url": url_for("profile.edit_profile"),
            "stats_cards": [
                {"label": "Total Jobs", "value": total_jobs, "icon": "bi-briefcase", "tone": "primary"},
                {"label": "Open Jobs", "value": open_jobs, "icon": "bi-hourglass-split", "tone": "warning"},
                {"label": "Completed Jobs", "value": completed_jobs, "icon": "bi-check-circle-fill", "tone": "success"},
            ],
        }

    total_applications = Application.query.filter_by(labour_id=user.id).count()
    accepted_applications = Application.query.filter_by(labour_id=user.id, status="Accepted").count()
    pending_applications = Application.query.filter_by(labour_id=user.id, status="Applied").count()

    return {
        "profile_title": "Labour Profile",
        "profile_subtitle": "Track your applications and keep your account details up to date.",
        "profile_icon": "bi-tools",
        "profile_badge": "Labourer",
        "display_role": "Labourer",
        "primary_action_label": "Available Jobs",
        "primary_action_url": url_for("labour.available_jobs"),
        "secondary_action_label": "Edit Profile",
        "secondary_action_url": url_for("profile.edit_profile"),
        "stats_cards": [
            {"label": "Applications", "value": total_applications, "icon": "bi-send-check", "tone": "primary"},
            {"label": "Accepted Jobs", "value": accepted_applications, "icon": "bi-check2-circle", "tone": "success"},
            {"label": "Pending", "value": pending_applications, "icon": "bi-clock-history", "tone": "warning"},
        ],
    }


# ----------------------------
# View Profile
# ----------------------------
@profile.route("/profile")
@login_required
def view_profile():

    if current_user.role == "customer":
        return redirect(url_for("customer.profile_page"))

    return redirect(url_for("labour.profile_page"))


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