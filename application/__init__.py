from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_mail import Mail
import config

app=Flask(__name__)

app.config.from_object(config.Config)

db = SQLAlchemy(app)

mail = Mail(app)

socketio=SocketIO(app,cors_allowed_origins="*")

from application import routes