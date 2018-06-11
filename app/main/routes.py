from datetime import datetime
from flask import render_template, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models import User, Business, Cluster
from app.main import bp
from sqlalchemy import text


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
    sql = text("SELECT c.name as cluster, d.name as database, bh.timecreated, bh.state, bh.info"
    " FROM dba.database d"
    " LEFT JOIN dba.deployment dp ON dp.database_id = d.id AND dp.environment_id = 1"
    " LEFT JOIN dba.cluster c ON dp.cluster_id = c.id"
    " LEFT JOIN dba.backup_history bh ON d.id = bh.database_id AND c.id = bh.cluster_id AND bh.timecreated > current_date - interval '3' day"
    " ORDER BY bh.timecreated DESC")
    print(sql)
    backups = db.engine.execute(sql)
    next_url = None
    prev_url = None
    return render_template('index.html', title='Home', next_url=next_url,
                           backups=backups, prev_url=prev_url)
