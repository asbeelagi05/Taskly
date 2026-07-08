from extensions import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)

    labour_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("jobs.id"),
        nullable=False
    )

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("applications.id"),
        nullable=True
    )

    message = db.Column(db.String(255), nullable=False)

    is_read = db.Column(db.Boolean, default=False)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    job = db.relationship("Job")

    labour = db.relationship("User")

    def __repr__(self):
        return f"<Notification Job:{self.job_id} Labour:{self.labour_id}>"