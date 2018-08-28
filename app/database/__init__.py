from flask import Blueprint

bp = Blueprint('database', __name__)

from app.database import routes
