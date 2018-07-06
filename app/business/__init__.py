from flask import Blueprint

bp = Blueprint('business', __name__)

from app.business import routes