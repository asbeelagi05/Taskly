from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.job import Job
from models.application import Application

labour = Blueprint("labour", __name__)


# ---------------------------------
# Labour Dashboard
# ---------------------------------
@labour.route("/labour/dashboard")
@login_required
def dashboard():

    jobs = (
        Job.query
        .filter_by(status="Open")
        .order_by(Job.created_at.desc())
        .limit(6)
        .all()
    )

    return render_template(
        "labour/dashboard.html",
        jobs=jobs
    )


# ---------------------------------
# Available Jobs
# ---------------------------------
@labour.route("/available-jobs")
@login_required
def available_jobs():

    jobs = (
        Job.query
        .filter_by(status="Open")
        .order_by(Job.created_at.desc())
        .all()
    )

    return render_template(
        "labour/available_jobs.html",
        jobs=jobs
    )


# ---------------------------------
# View Job
# ---------------------------------
@labour.route("/labour/job/<int:job_id>")
@login_required
def view_job(job_id):

    job = Job.query.get_or_404(job_id)

    already_applied = Application.query.filter_by(
        job_id=job.id,
        labour_id=current_user.id
    ).first()

    return render_template(
        "labour/view_job.html",
        job=job,
        already_applied=already_applied
    )


# ---------------------------------
# Apply
# ---------------------------------
@labour.route("/apply/<int:job_id>")
@login_required
def apply(job_id):

    job = Job.query.get_or_404(job_id)

    existing = Application.query.filter_by(
        job_id=job.id,
        labour_id=current_user.id
    ).first()

    if existing:

        flash("You have already applied for this job.", "warning")

        return redirect(
            url_for(
                "labour.view_job",
                job_id=job.id
            )
        )

    application = Application(
        job_id=job.id,
        labour_id=current_user.id
    )

    db.session.add(application)
    db.session.commit()

    flash("Application submitted successfully!", "success")

    return redirect(
        url_for("labour.dashboard")
    )


# ---------------------------------
# My Applications
# ---------------------------------
@labour.route("/my-applications")
@login_required
def my_applications():

    applications = (
        Application.query
        .filter_by(labour_id=current_user.id)
        .order_by(Application.applied_at.desc())
        .all()
    )

    return render_template(
        "labour/my_applications.html",
        applications=applications
    )