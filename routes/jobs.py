from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.job import Job
from models.application import Application
from utils.auth_decorators import customer_required

jobs = Blueprint("jobs", __name__)


# --------------------------------------------------
# Post Job
# --------------------------------------------------
@jobs.route("/post-job", methods=["GET", "POST"])
@login_required
@customer_required
def post_job():

    if request.method == "POST":

        job = Job(
            title=request.form["title"],
            description=request.form["description"],
            location=request.form["location"],
            budget=float(request.form["budget"]),
            workers_required=int(request.form["workers_required"]),
            customer_id=current_user.id
        )

        db.session.add(job)
        db.session.commit()

        flash("Job posted successfully!", "success")

        return redirect(url_for("customer.dashboard"))

    return render_template("customer/post_job.html")


# --------------------------------------------------
# View Job
# --------------------------------------------------
@jobs.route("/view-job/<int:job_id>")
@login_required
@customer_required
def view_job(job_id):

    job = Job.query.get_or_404(job_id)

    if job.customer_id != current_user.id:
        return "Access Denied", 403

    return render_template(
        "customer/view_job.html",
        job=job
    )


# --------------------------------------------------
# Edit Job
# --------------------------------------------------
@jobs.route("/edit-job/<int:job_id>", methods=["GET", "POST"])
@login_required
@customer_required
def edit_job(job_id):

    job = Job.query.get_or_404(job_id)

    if job.customer_id != current_user.id:
        return "Access Denied", 403

    if job.status != "Open":

        flash(
            "Only open jobs can be edited.",
            "warning"
        )

        return redirect(
            url_for(
                "jobs.view_job",
                job_id=job.id
            )
        )

    if request.method == "POST":

        job.title = request.form["title"]
        job.description = request.form["description"]
        job.location = request.form["location"]
        job.budget = float(request.form["budget"])
        job.workers_required = int(request.form["workers_required"])

        db.session.commit()

        flash("Job updated successfully!", "success")

        return redirect(url_for("customer.my_jobs"))

    return render_template(
        "customer/edit_job.html",
        job=job
    )


# --------------------------------------------------
# Delete Job
# --------------------------------------------------
@jobs.route("/delete-job/<int:job_id>", methods=["GET", "POST"])
@login_required
@customer_required
def delete_job(job_id):

    job = Job.query.get_or_404(job_id)

    if job.customer_id != current_user.id:
        return "Access Denied", 403

    if job.status != "Open":

        flash(
            "Only open jobs can be deleted.",
            "warning"
        )

        return redirect(
            url_for(
                "jobs.view_job",
                job_id=job.id
            )
        )

    if request.method == "POST":

        db.session.delete(job)
        db.session.commit()

        flash("Job deleted successfully!", "danger")

        return redirect(url_for("customer.my_jobs"))

    return render_template(
        "customer/delete_job.html",
        job=job
    )


# --------------------------------------------------
# View Applicants
# --------------------------------------------------
@jobs.route("/applicants/<int:job_id>")
@login_required
@customer_required
def applicants(job_id):

    job = Job.query.get_or_404(job_id)

    if job.customer_id != current_user.id:
        return "Access Denied", 403

    applications = Application.query.filter_by(
        job_id=job.id
    ).all()

    return render_template(
        "customer/applicants.html",
        job=job,
        applications=applications
    )


# --------------------------------------------------
# Accept Applicant
# --------------------------------------------------
@jobs.route("/accept/<int:application_id>")
@login_required
@customer_required
def accept(application_id):

    application = Application.query.get_or_404(application_id)
    job = Job.query.get_or_404(application.job_id)

    if job.customer_id != current_user.id:
        return "Access Denied", 403

    if job.status != "Open":

        flash(
            "This job has already started.",
            "warning"
        )

        return redirect(
            url_for(
                "jobs.applicants",
                job_id=job.id
            )
        )

    # Don't accept the same worker twice
    if application.status == "Accepted":

        flash(
            "This worker is already accepted.",
            "info"
        )

        return redirect(
            url_for(
                "jobs.applicants",
                job_id=job.id
            )
        )

    # Accept selected worker
    application.status = "Accepted"

    db.session.commit()

    # Count accepted workers
    accepted_count = Application.query.filter_by(
        job_id=job.id,
        status="Accepted"
    ).count()

    # When required workers are reached
    if accepted_count >= job.workers_required:

        job.status = "In Progress"

        remaining = Application.query.filter(
            Application.job_id == job.id,
            Application.status == "Applied"
        ).all()

        for app in remaining:
            app.status = "Rejected"

        db.session.commit()

        flash(
            "Required workers selected. Job is now In Progress.",
            "success"
        )

    else:

        flash(
            f"Worker accepted ({accepted_count}/{job.workers_required}).",
            "success"
        )

    return redirect(
        url_for(
            "jobs.applicants",
            job_id=job.id
        )
    )

    # Reject everyone else
    other_applications = Application.query.filter(
        Application.job_id == job.id,
        Application.id != application.id
    ).all()

    for app in other_applications:
        app.status = "Rejected"

    # Accept selected applicant
    application.status = "Accepted"

    # Update job
    job.status = "In Progress"

    db.session.commit()

    flash(
        "Applicant accepted successfully!",
        "success"
    )

    return redirect(
        url_for(
            "jobs.applicants",
            job_id=job.id
        )
    )


# --------------------------------------------------
# Reject Applicant
# --------------------------------------------------
@jobs.route("/reject/<int:application_id>")
@login_required
@customer_required
def reject(application_id):

    application = Application.query.get_or_404(application_id)

    job = Job.query.get_or_404(application.job_id)

    if job.customer_id != current_user.id:
        return "Access Denied", 403

    if application.status == "Accepted":

        flash(
            "Accepted applicant cannot be rejected.",
            "danger"
        )

        return redirect(
            url_for(
                "jobs.applicants",
                job_id=job.id
            )
        )

    application.status = "Rejected"

    db.session.commit()

    flash(
        "Applicant rejected.",
        "warning"
    )

    return redirect(
        url_for(
            "jobs.applicants",
            job_id=job.id
        )
    )


# --------------------------------------------------
# Complete Job
# --------------------------------------------------
@jobs.route("/complete-job/<int:job_id>")
@login_required
@customer_required
def complete_job(job_id):

    job = Job.query.get_or_404(job_id)

    if job.customer_id != current_user.id:
        return "Access Denied", 403

    if job.status != "In Progress":

        flash(
            "Only jobs in progress can be completed.",
            "warning"
        )

        return redirect(
            url_for(
                "jobs.view_job",
                job_id=job.id
            )
        )

    job.status = "Completed"

    db.session.commit()

    flash(
        "Job marked as completed!",
        "success"
    )

    return redirect(
        url_for(
            "jobs.view_job",
            job_id=job.id
        )
    )