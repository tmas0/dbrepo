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
from app.models import Rule, Business
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request


@bp.route("/rule/<int:business_id>/<key>", methods=['GET'])
@token_auth.login_required
def get_config(business_id=None, key=None):
    b = Business.get_or_404(business_id)

    if key is None:
        return bad_request('Please, set your key')

    rule = Rule.query.with_entities(Rule.value).filter_by(
        business_id=business_id,
        name=key,
        active=True
    ).first()

    return jsonify({'data': rule})
