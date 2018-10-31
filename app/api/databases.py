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


from flask import jsonify, request, url_for
from app import db
from app.models import Database
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request


@bp.route("/host/<environment>/<database>", methods=['GET'])
@token_auth.login_required
def get_host_from_db(environment=None, database=None):
    d = Database()

    host = d.get_host(environment, database)

    return jsonify({'host': host})


@bp.route("/database/<int:cluster_id>/<environment>", methods=['GET'])
@token_auth.login_required
def get_databases(cluster_id, environment=None):
    d = Database()

    dbs = d.get_databases(cluster_id, environment)

    return jsonify({'data': dbs})
