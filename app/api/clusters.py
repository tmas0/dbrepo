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


from flask import jsonify
from app.models import Cluster, Business
from app.api import bp
from app.api.auth import token_auth


@bp.route("/cluster/<int:business_id>", methods=['GET'])
@token_auth.login_required
def get_clusters(business_id=None):
    b = Business.query.get_or_404(business_id)

    clusters = Cluster.query.with_entities(
        Cluster.id,
        Cluster.name
    ).filter_by(
        business_id=business_id,
        active=True
    ).all()

    return jsonify({'data': clusters})
