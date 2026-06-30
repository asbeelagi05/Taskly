from extensions import db


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)

    description = db.Column(db.Text, nullable=False)

    location = db.Column(db.String(100), nullable=False)

    budget = db.Column(db.Float, nullable=False)

    workers_required = db.Column(db.Integer, nullable=False)

    status = db.Column(db.String(20), default="Open")

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def __repr__(self):
        return f"<Job {self.title}>"