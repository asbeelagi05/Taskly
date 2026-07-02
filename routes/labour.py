from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from sqlalchemy import or_

from extensions import db
from models.job import Job
from models.application import Application
from models.notification import Notification
from utils.auth_decorators import labour_required
from routes.profile import build_profile_context

labour = Blueprint("labour", __name__)


# ---------------------------------
# Labour Profile
# ---------------------------------
@labour.route("/labour/profile")
@login_required
@labour_required
def profile_page():

    return render_template(
        "profile.html",
        **build_profile_context(current_user)
    )


# ---------------------------------
# Labour Dashboard
# ---------------------------------
@labour.route("/labour/dashboard")
@login_required
@labour_required
def dashboard():

    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "newest")

    jobs_query = Job.query.filter_by(status="Open")

    if search:
        jobs_query = jobs_query.filter(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.location.ilike(f"%{search}%"),
                Job.description.ilike(f"%{search}%")
            )
        )

    if sort == "budget_low":
        jobs_query = jobs_query.order_by(Job.budget.asc())
    elif sort == "budget_high":
        jobs_query = jobs_query.order_by(Job.budget.desc())
    else:
        jobs_query = jobs_query.order_by(Job.created_at.desc())

    jobs = jobs_query.limit(6).all()

    finished_tasks = (
        Application.query
        .filter_by(labour_id=current_user.id, status="Finished")
        .order_by(Application.id.desc())
        .limit(5)
        .all()
    )

    job_alerts = (
        Notification.query
        .filter_by(labour_id=current_user.id, is_read=False)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return render_template(
        "labour/dashboard.html",
        jobs=jobs,
        finished_tasks=finished_tasks,
        job_alerts=job_alerts,
        search=search,
        selected_sort=sort
    )


# ---------------------------------
# Available Jobs
# ---------------------------------
@labour.route("/available-jobs")
@login_required
@labour_required
def available_jobs():

    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "newest")

    jobs = Job.query.filter_by(status="Open")

    if search:
        jobs = jobs.filter(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.location.ilike(f"%{search}%"),
                Job.description.ilike(f"%{search}%")
            )
        )

    if sort == "budget_low":
        jobs = jobs.order_by(Job.budget.asc())
    elif sort == "budget_high":
        jobs = jobs.order_by(Job.budget.desc())
    else:
        jobs = jobs.order_by(Job.created_at.desc())

    jobs = jobs.all()

    return render_template(
        "labour/available_jobs.html",
        jobs=jobs,
        search=search,
        selected_sort=sort
    )


# ---------------------------------
# View Job
# ---------------------------------
@labour.route("/labour/job/<int:job_id>")
@login_required
@labour_required
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
@labour_required
def apply(job_id):

    job = Job.query.get_or_404(job_id)

    if job.status != "Open":

        flash("This job is no longer open for applications.", "warning")

        return redirect(
            url_for(
                "labour.view_job",
                job_id=job.id
            )
        )

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
@labour_required
def my_applications():

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "All")

    applications = Application.query.filter_by(labour_id=current_user.id)

    if search:
        applications = applications.join(Application.job).filter(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.location.ilike(f"%{search}%")
            )
        )

    if status and status != "All":
        applications = applications.filter(Application.status == status)

    applications = applications.order_by(Application.applied_at.desc()).all()

    total_applications = len(applications)
    applied_applications = sum(1 for application in applications if application.status == "Applied")
    accepted_applications = sum(1 for application in applications if application.status == "Accepted")
    declared_finished_applications = sum(1 for application in applications if application.status == "Declared Finished")
    finished_applications = sum(1 for application in applications if application.status == "Finished")
    rejected_applications = sum(1 for application in applications if application.status == "Rejected")

    job_alerts = (
        Notification.query
        .filter_by(labour_id=current_user.id, is_read=False)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return render_template(
        "labour/my_applications.html",
        applications=applications,
        total_applications=total_applications,
        applied_applications=applied_applications,
        accepted_applications=accepted_applications,
        declared_finished_applications=declared_finished_applications,
        finished_applications=finished_applications,
        rejected_applications=rejected_applications,
        job_alerts=job_alerts,
        search=search,
        selected_status=status
    )