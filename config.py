class Config:
    SECRET_KEY = "taskly-secret-key"

    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://taskly_user:Taskly123@localhost/taskly"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False