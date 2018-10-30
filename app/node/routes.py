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
from app.models import Node, Cluster
from app.node import bp
import re
from app.node.forms import NodeForm


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/node', methods=['GET'])
@login_required
def index():
    form = NodeForm()
    nodes = Node.query.order_by(Node.id.desc()).all()

    node = Node()
    columns = node.serialize_columns()

    nod = []
    for c in nodes:
        nod.append(c.as_dict())

    form.cluster.choices = [
        (b.id, b.name) for b in Cluster.query.order_by('name').all()
    ]

    base_url = url_for('node.index')
    action_url = url_for('node.add')
    return render_template('node.html', title='Node',
                           rows=nod, columns=columns,
                           base_url=base_url, action_url=action_url,
                           per_page=current_app.config['ROWS_PER_PAGE'],
                           form=form)


@bp.route('/node/update', methods=['POST'])
@login_required
def update():
    node_id = request.form['pk']
    node = Node.query.filter_by(id=node_id).first_or_404()
    if node is None:
        flash(
            'Node %(node_id)s not found',
            node_id=request.form['pk']
            )
    else:
        key = request.form['name']
        value = request.form['value']
        if key == 'active':
            if value == 'true' or value == '1':
                value = 1
            else:
                value = 0
        setattr(node, key, value)
        db.session.commit()
        return 'Row modified'

    return 'Row not modified'


@bp.route('/node/add', methods=['POST'])
@login_required
def add():
    form = NodeForm()
    form.cluster.choices = [
        (b.id, b.name) for b in Cluster.query.order_by('name').all()
    ]
    if form.validate_on_submit():
        node_active = form.active.data
        node_name = re.sub('[^A-Za-z0-9_]+', '', form.nodename.data)
        node_business_id = form.business.data

        node = Node(
            name=node_name,
            active=node_active,
            business_id=node_business_id)

        db.session.add(node)
        db.session.commit()

    return redirect(url_for('node.index'))
