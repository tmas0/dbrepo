from datetime import datetime
from flask import render_template, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models import User, Business, Cluster
from app.main import bp
from sqlalchemy import select


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    print(Business.query.outerjoin(Cluster).order_by(Business.name.asc()).add_entity(Cluster))
    business = business.get_clusters()
    print(business)
    next_url = None
    prev_url = None
    return render_template('index.html', title='Home', next_url=next_url,
                           business=business, prev_url=prev_url)
