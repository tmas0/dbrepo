# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright (C) 2018 Toni Mas <antoni.mas@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from datetime import datetime
from flask import render_template, redirect, url_for, request, current_app, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import BackupHistory
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET'])
@login_required
def index():
    date = request.form.get('date')
    if date is not None:
        date = datetime.strptime(date, '%m/%d/%Y')
    else:
        date = datetime.now()

    # Per database, show backup status.
    bh = BackupHistory()

    history = bh.get_backup_history(date)
    columns = bh.serialize_columns()

    base_url = url_for('main.index')
    action_url = url_for('database.add')
    return render_template('index.html', title='Backup status',
                           rows=history, columns=columns,
                           base_url=base_url, action_url=action_url,
                           per_page=current_app.config['ROWS_PER_PAGE'])


@bp.route('/index', methods=['POST'])
@login_required
def index_refresh():
    date = request.form.get('date')
    if date is not None:
        date = datetime.strptime(date, '%m/%d/%Y')
    else:
        date = datetime.now()

    # Per database, show backup status.
    bh = BackupHistory()

    return jsonify(bh.get_backup_history(date))
