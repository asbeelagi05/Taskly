from flask import Flask
from config import Config
from extensions import db
from routes.auth import auth
from extensions import db, login_manager
from routes.customer import customer
from routes.labour import labour
from models.job import Job
from routes.jobs import jobs
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)

app.register_blueprint(auth)
app.register_blueprint(customer)
app.register_blueprint(labour)
app.register_blueprint(jobs)
from models.user import User

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return "<h1>Taskly Backend Running</h1>"

if __name__ == "__main__":
    app.run(debug=True)