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
from flask import render_template, redirect, url_for, request, \
    current_app, flash
from flask_login import current_user, login_required
from app import db
from app.models import User
from app.user import bp
import re
from app.user.forms import UserForm


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/user', methods=['GET'])
@login_required
def index():
    form = UserForm()
    users = User.query.order_by(User.id.desc()).all()

    user = User()
    columns = user.serialize_columns()

    u = []
    for us in users:
        u.append(us.as_dict())

    base_url = url_for('user.index')
    action_url = url_for('user.register')
    return render_template('user.html', title='User administration',
                           rows=u, columns=columns,
                           base_url=base_url, action_url=action_url,
                           per_page=current_app.config['ROWS_PER_PAGE'],
                           form=form)


@bp.route('/register', methods=['POST'])
@login_required
def register():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        # Workarround.
        lastid = User.query.order_by(User.id.desc()).first()
        user = User(
            id=lastid.id+1,
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
    return redirect(url_for('user.index'))
