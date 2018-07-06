from datetime import datetime
from flask import render_template, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models import User, Business, Cluster
from app.database import bp
from sqlalchemy import text


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/database', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    sql = text("SELECT b.name"
        " FROM dba.database b")
    print(sql)
    backups = db.engine.execute(sql)
    next_url = None
    prev_url = None
    return render_template('database.html', title='Business', next_url=next_url,
                           backups=backups, prev_url=prev_url)
