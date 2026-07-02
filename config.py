class Config:
    SECRET_KEY = "taskly-secret-key"

    SQLALCHEMY_DATABASE_URI = "sqlite:///taskly.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False