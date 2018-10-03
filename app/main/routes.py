from datetime import datetime
from flask import render_template, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models import BackupHistory
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
    # Per database, show backup status.
    bh = BackupHistory()

    history = bh.get_backup_history(1)
    columns = bh.serialize_columns()

    base_url = url_for('database.index')
    action_url = url_for('database.add')
    return render_template('index.html', title='Backup status',
                           rows=history, columns=columns,
                           base_url=base_url, action_url=action_url,
                           per_page=current_app.config['ROWS_PER_PAGE'])
