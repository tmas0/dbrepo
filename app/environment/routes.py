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
from app.models import Environment
from app.environment import bp
import re
from app.environment.forms import EnvironmentForm


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/environment', methods=['GET'])
@login_required
def index():
    form = EnvironmentForm()
    environments = Environment.query.order_by(Environment.id.desc()).all()

    env = Environment()
    columns = env.serialize_columns()

    envs = []
    for e in environments:
        envs.append(e.as_dict())

    base_url = url_for('environment.index')
    action_url = url_for('environment.add')
    return render_template('environment.html', title='Environments',
                           rows=envs, columns=columns,
                           base_url=base_url, action_url=action_url,
                           per_page=current_app.config['ROWS_PER_PAGE'],
                           form=form)


@bp.route('/environment/update', methods=['POST'])
@login_required
def update():
    environment_id = request.form['pk']
    environment = Environment.query.filter_by(id=environment_id).first_or_404()
    if environment is None:
        flash(
            'Environment %(environment_id)s not found',
            environment_id=request.form['pk']
            )
    else:
        key = request.form['name']
        value = request.form['value']
        if key == 'active':
            if value == 'true' or value == '1':
                value = 1
            else:
                value = 0
        setattr(environment, key, value)
        db.session.commit()
        return 'Row modified'

    return 'Row not modified'


@bp.route('/environment/add', methods=['POST'])
@login_required
def add():
    form = EnvironmentForm()
    if form.validate_on_submit():
        environment_active = form.active.data
        environment_name = re.sub('[^A-Za-z0-9_]+', '', form.envname.data)

        environment = Environment(
            name=environment_name,
            active=environment_active
        )

        db.session.add(environment)
        db.session.commit()

    return redirect(url_for('environment.index'))
