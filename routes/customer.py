from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import func, or_

from extensions import db
from models.job import Job
from utils.auth_decorators import customer_required
from routes.profile import build_profile_context

customer = Blueprint("customer", __name__)


# ---------------------------------
# Customer Profile
# ---------------------------------
@customer.route("/customer/profile")
@login_required
@customer_required
def profile_page():

    return render_template(
        "profile.html",
        **build_profile_context(current_user)
    )


# ---------------------------------
# Customer Dashboard
# ---------------------------------
@customer.route("/customer/dashboard")
@login_required
@customer_required
def dashboard():

    hour = datetime.now().hour

    if hour < 12:
        greeting = "Good Morning ☀️"
    elif hour < 17:
        greeting = "Good Afternoon 🌤️"
    else:
        greeting = "Good Evening 🌙"

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "All")

    jobs = Job.query.filter_by(customer_id=current_user.id)

    if search:
        jobs = jobs.filter(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.location.ilike(f"%{search}%"),
                Job.description.ilike(f"%{search}%")
            )
        )

    if status and status != "All":
        jobs = jobs.filter(Job.status == status)

    total_jobs = jobs.count()

    open_jobs = jobs.filter_by(status="Open").count()

    completed_jobs = jobs.filter_by(status="Completed").count()

    average_budget = (
        db.session.query(func.avg(Job.budget))
        .filter(Job.customer_id == current_user.id)
        .scalar()
    )

    if average_budget is None:
        average_budget = 0

    latest_job = (
        Job.query.filter_by(customer_id=current_user.id)
        .order_by(Job.id.desc())
        .first()
    )

    recent_jobs = (
        jobs
        .order_by(Job.id.desc())
        .limit(5)
        .all()
    )

    finished_jobs = (
        jobs.filter(Job.status == "Completed")
        .order_by(Job.id.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "customer/dashboard.html",
        greeting=greeting,
        total_jobs=total_jobs,
        open_jobs=open_jobs,
        completed_jobs=completed_jobs,
        average_budget=round(average_budget),
        latest_job=latest_job,
        recent_jobs=recent_jobs,
        finished_jobs=finished_jobs,
        search=search,
        selected_status=status
    )


# ---------------------------------
# My Jobs
# ---------------------------------
@customer.route("/my-jobs")
@login_required
@customer_required
def my_jobs():

    status = request.args.get("status")

    search = request.args.get("search")

    query = Job.query.filter_by(
        customer_id=current_user.id
    )

    if status and status != "All":
        query = query.filter(Job.status == status)

    if search:
        query = query.filter(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.location.ilike(f"%{search}%"),
                Job.description.ilike(f"%{search}%")
            )
        )

    jobs = (
        query.order_by(Job.id.desc())
        .all()
    )

    return render_template(
        "customer/my_jobs.html",
        jobs=jobs,
        selected_status=status or "All",
        search=search or "",
        job_count=len(jobs)
    )