from flask import Flask
from config import Config
from jinja2 import StrictUndefined
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.jinja_env.undefined = StrictUndefined
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)

# Message if user does not have access to page
login.login_message = 'Please log in to access this page.'
login.login_message_category = 'danger'

login.login_view = 'login'

from app import views, models
from app.utils.General.debug_utils import reset_db


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, generate_password_hash=generate_password_hash, reset_db=reset_db)
