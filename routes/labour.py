from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.job import Job
from models.application import Application
from utils.auth_decorators import labour_required

labour = Blueprint("labour", __name__)


@labour.route("/labour/dashboard")
@login_required
@labour_required
def dashboard():

    available_jobs = Job.query.filter_by(
        status="Open"
    ).order_by(Job.id.desc()).limit(6).all()

    assigned_jobs = (
        Job.query.join(Application)
        .filter(
            Application.labour_id == current_user.id,
            Application.status == "Accepted"
        )
        .all()
    )

    application_count = (
        Application.query.filter_by(
            labour_id=current_user.id
        ).count()
    )

    return render_template(
        "labour/dashboard.html",
        jobs=available_jobs,
        assigned_jobs=assigned_jobs,
        application_count=application_count
    )