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


from flask import jsonify, request
from app.models import Cluster, Database, BackupHistory
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
from app import db
import app
import datetime


@bp.route('/backup/logging', methods=['POST'])
@token_auth.login_required
def new_backup_event():
    data = request.get_json() or {}
    if ('cluster_id' not in data or
            'database_id' not in data or
            'scheduled' not in data):
        return bad_request(
            'must include cluster_id, database_id and scheduled fields'
        )
    if 'timecreated' not in data:
        data['timecreated'] = datetime.datetime.utcnow
    if not Cluster.query.filter_by(id=data['cluster_id']).first():
        return bad_request('please use a valid cluster identifier')
    if not Database.query.filter_by(id=data['database_id']).first():
        return bad_request('please use a valid database identifier')

    app.logger.info('Logging: %s' % data)
    bh = BackupHistory()
    bh.from_dict(data)
    db.session.add(bh)
    db.session.commit()
    return jsonify(bh.to_dict())
