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

import datetime
from app import db, login
from sqlalchemy import DateTime, Sequence, text
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config as config

##########################################################################
#
# The schema version is used to track when upgrades are needed to the
# configuration database. Increment this whenever changes are made to the
# model or data, AND ensure the upgrade code is added to setup.py
#
##########################################################################

SCHEMA_VERSION = 0

db.metadata.schema = config.DATABASE_SCHEMA


class Business(db.Model):
    """
    Business table
    """
    __tablename__ = 'business'

    # Fields.
    id = db.Column(
        db.Integer,
        Sequence('bussiness_id_seq', start=1, increment=1),
        primary_key=True,
        nullable=False
    )
    name = db.Column(
        db.String(length=255),
        nullable=False,
        unique=True
    )
    domain = db.Column(
        db.String(),
        nullable=False
    )
    active = db.Column(
        db.Boolean(),
        default=True,
        server_default=text('true'),
        nullable=False
    )

    def as_dict(self):
        data = {}
        for c in self.__table__.columns:
            if c.name == 'active' and getattr(self, c.name) is True:
                data[c.name] = str(1)
            elif c.name == 'active' and getattr(self, c.name) is False:
                data[c.name] = str(0)
            else:
                data[c.name] = getattr(self, c.name)
        return data
        #return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def serialize_columns(self):
        meta = []
        for c in self.__table__.columns:
            if c.name != 'id' and c.name != 'active':
                title = ''
                if c.name == 'name':
                    title = 'Business name:'
                elif c.name == 'domain':
                    title = 'Domain:'
                meta.append({
                    'field': c.name,
                    'title': c.name.capitalize(),
                    'sortable': True, 'editable': {
                        'type': 'text',
                        'title': title,
                        'ajaxOptions': {
                            'type': 'POST',
                            'success': 'function (data) { }',
                            'error': 'function (xhr, status, error) { var err = eval("(" + xhr.responseText + ")"); alert(err.Message); }'}, 'validate': 'function (value) { value = $.trim(value); if (!value) { return \'This field is required\'; } if (!/^\$/.test(value)) { return \'This field needs to start width $.\'} var data = $table.bootstrapTable(\'getData\'), index = $(this).parents(\'tr\').data(\'index\'); console.log(data[index]); return \'\';'}})
            elif c.name == 'active':
                meta.append({'field': c.name, 'title': c.name.capitalize(), 'sortable': True, 'editable': {'type': 'select', 'title': 'Active:', 'source': '[{value: "1", text: "Yes"}, {value: "0", text: "No"}]', 'ajaxOptions': { 'type': 'POST', 'success': 'function (data) { }', 'error': 'function (xhr, status, error) { var err = eval("(" + xhr.responseText + ")"); alert(err.Message); }'}}})
            else:
                meta.append({'field': c.name, 'title': c.name.capitalize(), 'sortable': True})

        return meta


class Cluster(db.Model):
    """
    Cluster table
    """
    __tablename__ = 'cluster'

    # Fields.
    id = db.Column(
        db.Integer,
        Sequence('cluster_id_seq', start=1, increment=1),
        primary_key=True,
        nullable=False
    )
    business_id = db.Column(
        db.Integer,
        db.ForeignKey('business.id'),
        nullable=False
    )
    business = db.relationship('Business', backref='businesses')
    name = db.Column(
        db.String(length=255),
        nullable=False,
        unique=True
    )
    active = db.Column(
        db.Boolean(),
        default=True,
        server_default=text('true'),
        nullable=False
    )
    domainprefix = db.Column(
        db.String(),
        default='pgc',
        server_default="pgc",
        nullable=False
    )

    def as_dict(self):
        data = {}
        for c in self.__table__.columns:
            if c.name == 'active' and getattr(self, c.name) is True:
                data[c.name] = str(1)
            elif c.name == 'active' and getattr(self, c.name) is False:
                data[c.name] = str(0)
            elif c.name == 'business_id':
                b = Business.query.get(int(getattr(self, c.name)))
                data[c.name] = b.name
            else:
                data[c.name] = getattr(self, c.name)
        return data

    def serialize_columns(self):
        meta = []
        for c in self.__table__.columns:
            if c.name != 'id' and c.name != 'active':
                title = ''
                if c.name == 'name':
                    title = 'Cluster name'
                elif c.name == 'domainprefix':
                    title = 'Domain Prefix'
                elif c.name == 'business_id':
                    title = 'Business'
                meta.append({
                    'field': c.name,
                    'title': title,
                    'sortable': True, 'editable': {
                        'type': 'text',
                        'title': title + ':',
                        'ajaxOptions': {
                            'type': 'POST',
                            'success': 'function (data) { }',
                            'error': 'function (xhr, status, error) { var err = eval("(" + xhr.responseText + ")"); alert(err.Message); }'}, 'validate': 'function (value) { value = $.trim(value); if (!value) { return \'This field is required\'; } if (!/^\$/.test(value)) { return \'This field needs to start width $.\'} var data = $table.bootstrapTable(\'getData\'), index = $(this).parents(\'tr\').data(\'index\'); console.log(data[index]); return \'\';'}})
            elif c.name == 'active':
                meta.append({'field': c.name, 'title': c.name.capitalize(), 'sortable': True, 'editable': {'type': 'select', 'title': 'Active:', 'source': '[{value: "1", text: "Yes"}, {value: "0", text: "No"}]', 'ajaxOptions': { 'type': 'POST', 'success': 'function (data) { }', 'error': 'function (xhr, status, error) { var err = eval("(" + xhr.responseText + ")"); alert(err.Message); }'}}})
            else:
                meta.append({'field': c.name, 'title': c.name.capitalize(), 'sortable': True})

        return meta


class Rule(db.Model):
    """
    Rule table
    """
    __tablename__ = 'rule'

    # Fields.
    id = db.Column(
        db.Integer,
        Sequence('backup_config_id_seq', start=1, increment=1),
        primary_key=True,
        nullable=False
    )
    name = db.Column(
        db.String(length=128),
        nullable=False
    )
    value = db.Column(
        db.String(length=128),
        nullable=True
    )
    business_id = db.Column(
        db.Integer,
        db.ForeignKey('business.id'),
        nullable=False
    )
    active = db.Column(
        db.Boolean(),
        default=True,
        server_default=text('true'),
        nullable=False
    )


class Node(db.Model):
    """
    Node table
    """
    __tablename__ = 'node'

    # Fields.
    id = db.Column(
        db.Integer,
        Sequence('nodes_id_seq', start=1, increment=1),
        primary_key=True,
        nullable=False
    )
    cluster_id = db.Column(
        db.Integer,
        db.ForeignKey('cluster.id'),
        nullable=False
    )
    name = db.Column(
        db.String(length=255),
        nullable=False,
        unique=True
    )
    active = db.Column(
        db.Boolean(),
        default=True,
        server_default=text('true'),
        nullable=False
    )


class Database(db.Model):
    """
    Database table
    """
    __tablename__ = 'database'

    # Fields.
    id = db.Column(
        db.Integer,
        Sequence('database_id_seq', start=1, increment=1),
        primary_key=True,
        nullable=False
    )
    name = db.Column(
        db.String(length=255),
        nullable=False,
        unique=True
    )
    active = db.Column(
        db.Boolean(),
        default=True,
        server_default=text('true'),
        nullable=False
    )

    def as_dict(self):
        data = {}
        for c in self.__table__.columns:
            if c.name == 'active' and getattr(self, c.name) is True:
                data[c.name] = str(1)
            elif c.name == 'active' and getattr(self, c.name) is False:
                data[c.name] = str(0)
            else:
                data[c.name] = getattr(self, c.name)
        return data
        #return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def serialize_columns(self):
        meta = []
        for c in self.__table__.columns:
            if c.name != 'id' and c.name != 'active':
                meta.append({
                    'field': c.name,
                    'title': c.name.capitalize(),
                    'sortable': True, 'editable': {
                        'type': 'text',
                        'title': 'Database name:',
                        'ajaxOptions': {
                            'type': 'POST',
                            'success': 'function (data) { }',
                            'error': 'function (xhr, status, error) { var err = eval("(" + xhr.responseText + ")"); alert(err.Message); }'}, 'validate': 'function (value) { value = $.trim(value); if (!value) { return \'This field is required\'; } if (!/^\$/.test(value)) { return \'This field needs to start width $.\'} var data = $table.bootstrapTable(\'getData\'), index = $(this).parents(\'tr\').data(\'index\'); console.log(data[index]); return \'\';'}})
            elif c.name == 'active':
                meta.append({'field': c.name, 'title': c.name.capitalize(), 'sortable': True, 'editable': {'type': 'select', 'title': 'Active:', 'source': '[{value: "1", text: "Yes"}, {value: "0", text: "No"}]', 'ajaxOptions': { 'type': 'POST', 'success': 'function (data) { }', 'error': 'function (xhr, status, error) { var err = eval("(" + xhr.responseText + ")"); alert(err.Message); }'}}})
            else:
                meta.append({'field': c.name, 'title': c.name.capitalize(), 'sortable': True})

        return meta


class Environment(db.Model):
    """
    Environment table
    """
    __tablename__ = 'environment'

    # Fields.
    id = db.Column(
        db.Integer,
        Sequence('environment_id_seq', start=1, increment=1),
        primary_key=True,
        nullable=False
    )
    name = db.Column(
        db.String(length=32),
        nullable=False,
        unique=True
    )
    active = db.Column(
        db.Boolean(),
        default=True,
        server_default=text('true'),
        nullable=False
    )
    domainprefix = db.Column(
        db.String(length=12),
        nullable=True
    )


class Deployment(db.Model):
    """
    Deployment table
    """
    __tablename__ = 'deployment'

    # Fields.
    id = db.Column(
        db.Integer,
        Sequence('deployment_id_seq', start=1, increment=1),
        primary_key=True,
        nullable=False
    )
    environment_id = db.Column(
        db.Integer,
        db.ForeignKey('environment.id'),
        nullable=False
    )
    cluster_id = db.Column(
        db.Integer,
        db.ForeignKey('cluster.id'),
        nullable=False
    )
    database_id = db.Column(
        db.Integer,
        db.ForeignKey('database.id'),
        nullable=False
    )
    name = db.Column(
        db.String(length=255),
        nullable=False,
        unique=True
    )
    active = db.Column(
        db.Boolean(),
        default=True,
        server_default=text('true'),
        nullable=False
    )


class BackupHistory(db.Model):
    """
    Backup history table
    """
    __tablename__ = 'backup_history'

    # Fields.
    id = db.Column(
        db.Integer,
        Sequence('backup_history_id_seq', start=1, increment=1),
        primary_key=True,
        nullable=False
    )
    timecreated = db.Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        server_default=text('NOW()')
    )
    cluster_id = db.Column(
        db.Integer,
        db.ForeignKey('cluster.id'),
        nullable=False
    )
    database_id = db.Column(
        db.Integer,
        db.ForeignKey('database.id'),
        nullable=False
    )
    scheduled = db.Column(
        db.String(length=12),
        nullable=False
    )
    state = db.Column(
        db.Boolean(),
        default=True,
        server_default=text('false'),
        nullable=False
    )
    size = db.Column(
        db.Integer,
        nullable=False,
        default=0,
        server_default=text('0')
    )
    duration = db.Column(
        db.Integer,
        nullable=False,
        default=0,
        server_default=text('0')
    )
    info = db.Column(
        db.Text(),
        nullable=True
    )

    def get_backup_history(self, diffdays=0, page=1, per_page=20):
        
        query(
            Cluster.name,
            Database.name,
            BackupHistory.timecreated,
            BackupHistory.state,
            BackupHistory.info).\
                join(
                    Deployment.database_id
                    ).\
                join(Cluster, Deployment.cluster_id==Cluster.id).\
                outerjoin(BackupHistory, and_(Database.id==BackupHistory.database_id, Cluster.id==BackupHistory.cluster_id)).\
                filter(BackupHistory.id==None)


class RecoveryHistory(db.Model):
    """
    Recovery history table
    """
    __tablename__ = 'recovery_history'

    # Fields.
    id = db.Column(
        db.Integer,
        Sequence('recovery_history_id_seq', start=1, increment=1),
        primary_key=True,
        nullable=False
    )
    timecreated = db.Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        server_default=text('NOW()')
    )
    cluster_id = db.Column(
        db.Integer,
        db.ForeignKey('cluster.id'),
        nullable=False
    )
    database_id = db.Column(
        db.Integer,
        db.ForeignKey('database.id'),
        nullable=False
    )
    scheduled = db.Column(
        db.String(length=12),
        nullable=False
    )
    state = db.Column(
        db.Boolean(),
        default=True,
        server_default=text('true'),
        nullable=False
    )
    info = db.Column(
        db.Text(),
        nullable=True
    )


class User(UserMixin, db.Model):
    id = db.Column(
        db.Integer,
        Sequence('user_id_seq', start=1, increment=1),
        primary_key=True,
        nullable=False
    )
    username = db.Column(
        db.String(64),
        index=True,
        unique=True
    )
    email = db.Column(
        db.String(120),
        index=True,
        unique=True
    )
    password_hash = db.Column(
        db.String(128)
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    #@staticmethod
    #def try_login(username, password):
        #conn = get_ldap_connection()
        #conn.simple_bind_s(
        #    'cn=%s,ou=Users,dc=testathon,dc=net' % username,
        #    password
        #)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
