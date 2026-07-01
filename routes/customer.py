from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import datetime

from models.job import Job
from extensions import db
from sqlalchemy import func

customer = Blueprint("customer", __name__)


# ---------------------------------
# Customer Dashboard
# ---------------------------------
@customer.route("/customer/dashboard")
@login_required
def dashboard():

    hour = datetime.now().hour

    if hour < 12:
        greeting = "Good Morning ☀️"
    elif hour < 17:
        greeting = "Good Afternoon 🌤️"
    else:
        greeting = "Good Evening 🌙"

    jobs = Job.query.filter_by(customer_id=current_user.id)

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
        Job.query.filter_by(customer_id=current_user.id)
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
        recent_jobs=recent_jobs
    )


# ---------------------------------
# My Jobs
# ---------------------------------
@customer.route("/my-jobs")
@login_required
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
            Job.title.ilike(f"%{search}%")
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