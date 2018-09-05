# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright (C) 2018 Toni Mas <toni.mas@bluekiri.com>
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
from flask import render_template, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models import Database
from app.database import bp
from math import ceil


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/database', methods=['GET'])
@login_required
def index():
    databases = Database.query.order_by(Database.id.desc()).all()

    db = Database()
    columns = db.serialize_columns()

    dbs = []
    for db in databases:
        dbs.append(db.as_dict())

    base_url = url_for('database.index')
    return render_template('database.html', title='Databases',
                           databases=dbs, columns=columns,
                           base_url=base_url,
                           per_page=current_app.config['ROWS_PER_PAGE'])


@bp.route('/database/update', methods=['POST'])
@login_required
def update():
    print(request.form)
    database_id = request.form['pk']
    database = Database.query.filter_by(id=database_id).first_or_404()
    print(database)
    return
