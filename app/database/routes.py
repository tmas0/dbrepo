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


@bp.route('/database', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    databases = Database.query.order_by("id").paginate(
        page, current_app.config['ROWS_PER_PAGE'], False)
    next_url = url_for('database.index', page=databases.next_num) \
        if databases.has_next else None
    prev_url = url_for('database.index', page=databases.prev_num) \
        if databases.has_prev else None
    base_url = url_for('database.index')
    return render_template('database.html', title='Databases',
                           next_url=next_url, databases=databases,
                           prev_url=prev_url, base_url=base_url,
                           page=page)
