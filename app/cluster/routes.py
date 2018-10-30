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
from app.models import Cluster, Business
from app.cluster import bp
import re
from app.cluster.forms import ClusterForm


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/cluster', methods=['GET'])
@login_required
def index():
    form = ClusterForm()
    clusters = Cluster.query.order_by(Cluster.id.desc()).all()

    cluster = Cluster()
    columns = cluster.serialize_columns()

    clus = []
    for c in clusters:
        clus.append(c.as_dict())

    form.business.choices = [
        (b.id, b.name) for b in Business.query.order_by('name').all()
    ]

    base_url = url_for('cluster.index')
    action_url = url_for('cluster.add')
    return render_template('cluster.html', title='Cluster',
                           rows=clus, columns=columns,
                           base_url=base_url, action_url=action_url,
                           per_page=current_app.config['ROWS_PER_PAGE'],
                           form=form)


@bp.route('/cluster/update', methods=['POST'])
@login_required
def update():
    cluster_id = request.form['pk']
    cluster = Cluster.query.filter_by(id=cluster_id).first_or_404()
    if cluster is None:
        flash(
            'Cluster %(cluster_id)s not found',
            cluster_id=request.form['pk']
            )
    else:
        key = request.form['name']
        value = request.form['value']
        if key == 'active':
            if value == 'true' or value == '1':
                value = 1
            else:
                value = 0
        setattr(cluster, key, value)
        db.session.commit()
        return 'Row modified'

    return 'Row not modified'


@bp.route('/cluster/add', methods=['POST'])
@login_required
def add():
    form = ClusterForm()
    form.business.choices = [
        (b.id, b.name) for b in Business.query.order_by('name').all()
    ]
    if form.validate_on_submit():
        cluster_active = form.active.data
        cluster_name = re.sub('[^A-Za-z0-9_]+', '', form.cluname.data)
        cluster_domainprefix = re.sub('[^A-Za-z0-9_]+', '', form.domainprefix.data)
        cluster_business_id = form.business.data

        cluster = Cluster(
            name=cluster_name,
            active=cluster_active,
            domainprefix=cluster_domainprefix,
            business_id=cluster_business_id)

        db.session.add(cluster)
        db.session.commit()

    return redirect(url_for('cluster.index'))
