from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import config

app=Flask(__name__)

app.config.from_object(config.Config)

db = SQLAlchemy(app)

socketio=SocketIO(app,cors_allowed_origins="*")

from application import routes