from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.job import Job

customer = Blueprint("customer", __name__)


@customer.route("/customer/dashboard")
@login_required
def dashboard():

    total_jobs = Job.query.filter_by(
        customer_id=current_user.id
    ).count()

    open_jobs = Job.query.filter_by(
        customer_id=current_user.id,
        status="Open"
    ).count()

    return render_template(
        "customer_dashboard.html",
        total_jobs=total_jobs,
        open_jobs=open_jobs
    )


@customer.route("/my-jobs")
@login_required
def my_jobs():

    jobs = Job.query.filter_by(
        customer_id=current_user.id
    ).all()

    return render_template(
        "my_jobs.html",
        jobs=jobs
    )