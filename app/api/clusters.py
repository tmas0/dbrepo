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
from app.models import Cluster, Business, Node
from app.api import bp
from app.api.auth import token_auth
import psycopg2
import psycopg2.extras
import os


@bp.route("/cluster/<int:business_id>", methods=['GET'])
@token_auth.login_required
def get_clusters(business_id=None):
    b = Business.query.get_or_404(business_id)

    clusters = Cluster.query.with_entities(
        Cluster.id,
        Cluster.name
    ).filter_by(
        business_id=b.id,
        active=True
    ).all()

    return jsonify({'data': clusters})


@bp.route("/standby/<int:cluster_id>", methods=['GET'])
@token_auth.login_required
def get_standby_node(cluster_id=None):
    c = Cluster.query.get_or_404(cluster_id)
    b = Business.query.filter_by(id=c.business_id).first()

    nodes = Node.query.with_entities(
        Node.name
    ).filter_by(
        cluster_id=c.id,
        active=True
    ).all()

    # Get foreign connection settings.
    try:
        dbuser = os.getenv('PGMB_EDBUSER', 'postgres')
        dbpassword = os.getenv('PGMB_EDBPASSWORD', '')
        dbport = os.getenv('PGMB_EPORT', 5432)
    except os.error:
        print(
            """User or Password not set.
               Use export=PGMB_EDBUSER=your_username;
               export=PGMB_EDBPASSWORD=your_password
               for external node connection"""
        )

    # Search stanby node.
    for n in nodes:
        node = n[0] + '.' + b.domain
        # Determine if standby node.
        conn = psycopg2.connect(
            dbname='postgres',
            user=dbuser,
            password=dbpassword,
            host=node,
            port=dbport
        )
        cursor = conn.cursor()
        cursor.execute('SELECT pg_is_in_recovery()')
        is_slave = cursor.fetchall()
        cursor.close()
        conn.close()
        if is_slave[0][0]:
            return jsonify({'data': node})

    return jsonify({'data': ''})
