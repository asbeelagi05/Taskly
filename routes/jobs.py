from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from extensions import db
from models.job import Job

jobs = Blueprint("jobs", __name__)


@jobs.route("/post-job", methods=["GET", "POST"])
@login_required
def post_job():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]
        budget = float(request.form["budget"])
        workers_required = int(request.form["workers_required"])

        job = Job(
            title=title,
            description=description,
            location=location,
            budget=budget,
            workers_required=workers_required,
            customer_id=current_user.id
        )

        db.session.add(job)
        db.session.commit()

        return redirect(url_for("customer.dashboard"))

    return render_template("post_job.html")


@jobs.route("/view-job/<int:job_id>")
@login_required
def view_job(job_id):

    job = Job.query.get_or_404(job_id)

    if job.customer_id != current_user.id:
        return "Access Denied", 403

    return render_template(
        "view_job.html",
        job=job
    )