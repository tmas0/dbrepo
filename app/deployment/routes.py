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
from app.models import Deployment, Cluster, Database, Environment
from app.deployment import bp
import re
from app.deployment.forms import DeploymentForm


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/deployment', methods=['GET'])
@login_required
def index():
    form = DeploymentForm()
    deployments = Deployment.query.order_by(Deployment.id.desc()).all()

    deployment = Deployment()
    columns = deployment.serialize_columns()

    depls = []
    for c in deployments:
        depls.append(c.as_dict())

    form.cluster.choices = [
        (b.id, b.name) for b in Cluster.query.order_by('name').all()
    ]
    form.database.choices = [
        (b.id, b.name) for b in Database.query.order_by('name').all()
    ]
    form.environment.choices = [
        (b.id, b.name) for b in Environment.query.order_by('name').all()
    ]

    base_url = url_for('deployment.index')
    action_url = url_for('deployment.add')
    return render_template('deployment.html', title='Deployment',
                           rows=depls, columns=columns,
                           base_url=base_url, action_url=action_url,
                           per_page=current_app.config['ROWS_PER_PAGE'],
                           form=form)


@bp.route('/deployment/update', methods=['POST'])
@login_required
def update():
    deployment_id = request.form['pk']
    deployment = Deployment.query.filter_by(id=deployment_id).first_or_404()
    if deployment is None:
        flash(
            'Deployment %(deployment_id)s not found',
            deployment_id=request.form['pk']
            )
    else:
        key = request.form['name']
        value = request.form['value']
        if key == 'active':
            if value == 'true' or value == '1':
                value = 1
            else:
                value = 0
        setattr(deployment, key, value)
        db.session.commit()
        return 'Row modified'

    return 'Row not modified'


@bp.route('/deployment/add', methods=['POST'])
@login_required
def add():
    form = DeploymentForm()
    form.cluster.choices = [
        (b.id, b.name) for b in Cluster.query.order_by('name').all()
    ]
    form.database.choices = [
        (b.id, b.name) for b in Database.query.order_by('name').all()
    ]
    form.environment.choices = [
        (b.id, b.name) for b in Environment.query.order_by('name').all()
    ]
    if form.validate_on_submit():
        deployment_active = form.active.data
        deployment_cluster_id = form.cluster.data
        deployment_database_id = form.database.data
        deployment_environment_id = form.environment.data

        deployment = Deployment(
            active=deployment_active,
            cluster_id=deployment_cluster_id,
            database_id=deployment_database_id,
            environment_id=deployment_environment_id
        )

        db.add(deployment)

    return redirect(url_for('deployment.index'))
