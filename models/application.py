
from extensions import db


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("jobs.id"),
        nullable=False
    )

    labour_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Applied"
    )

    applied_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    job = db.relationship(
        "Job",
        backref="applications"
    )

    labour = db.relationship(
        "User",
        backref="applications"
    )

    def __repr__(self):
        return f"<Application Job:{self.job_id} Labour:{self.labour_id}>"