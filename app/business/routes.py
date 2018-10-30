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
from app.models import Business
from app.business import bp
import re
from app.business.forms import BusinessForm


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/business', methods=['GET'])
@login_required
def index():
    form = BusinessForm()
    business = Business.query.order_by(Business.id.desc()).all()

    bu = Business()
    columns = bu.serialize_columns()

    bus = []
    for b in business:
        bus.append(b.as_dict())

    base_url = url_for('business.index')
    action_url = url_for('business.add')
    return render_template('business.html', title='Business',
                           rows=bus, columns=columns,
                           base_url=base_url, action_url=action_url,
                           per_page=current_app.config['ROWS_PER_PAGE'],
                           form=form)


@bp.route('/business/update', methods=['POST'])
@login_required
def update():
    business_id = request.form['pk']
    business = Business.query.filter_by(id=business_id).first_or_404()
    if business is None:
        flash(
            'Business %(business_id)s not found',
            business_id=request.form['pk']
            )
    else:
        key = request.form['name']
        value = request.form['value']
        if key == 'active':
            if value == 'true' or value == '1':
                value = 1
            else:
                value = 0
        setattr(business, key, value)
        db.session.commit()
        return 'Row modified'

    return 'Row not modified'


@bp.route('/business/add', methods=['POST'])
@login_required
def add():
    form = BusinessForm()
    if form.validate_on_submit():
        business_active = form.active.data
        business_name = re.sub('[^A-Za-z0-9_]+', '', form.buname.data)
        business_domain = re.sub('[^A-Za-z0-9_]+', '', form.domain.data)

        business = Business(
            name=business_name,
            active=business_active,
            domain=business_domain
        )

        db.session.add(business)
        db.session.commit()

    return redirect(url_for('business.index'))
