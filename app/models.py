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

import copy
import base64
from datetime import timedelta
from datetime import datetime
import os
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

    @property
    def serialize(self):
        return {
            'business_id': self.id,
            'business_name': self.name
        }

    def get_business(self):
        return Business.query.with_entities(Business.id, Business.name).\
            filter_by(active=True).all()

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
                data[c.name] = str(getattr(self, c.name))
            else:
                data[c.name] = getattr(self, c.name)
        return data

    def serialize_columns(self):
        meta = []
        for c in self.__table__.columns:
            if c.name != 'id' and c.name != 'active' and c.name != 'business_id':
                title = ''
                if c.name == 'name':
                    title = 'Cluster name'
                elif c.name == 'domainprefix':
                    title = 'Domain Prefix'
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
            elif c.name == 'business_id':
                source = []
                for b in Business.query.order_by('name').all():
                    bu = {}
                    bu[b.id] = b.name
                    source.append(bu)
                meta.append({
                    'field': c.name,
                    'title': 'Business',
                    'sortable': True, 'editable': {
                        'type': 'select',
                        'title': 'Business:',
                        'source': source,
                        'ajaxOptions': {
                            'type': 'POST',
                            'success': 'function (data) { }',
                            'error': 'function (xhr, status, error) { var err = eval("(" + xhr.responseText + ")"); alert(err.Message); }'},
                            'validate': 'function (value) { value = $.trim(value); if (!value) { return \'This field is required\'; } if (!/^\$/.test(value)) { return \'This field needs to start width $.\'} var data = $table.bootstrapTable(\'getData\'), index = $(this).parents(\'tr\').data(\'index\'); console.log(data[index]); return \'\';'
                        }
                    }
                )
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
        Sequence('node_id_seq', start=1, increment=1),
        primary_key=True,
        nullable=False
    )
    cluster_id = db.Column(
        db.Integer,
        db.ForeignKey('cluster.id'),
        nullable=False
    )
    cluster = db.relationship('Cluster', backref='cluster')
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
            elif c.name == 'cluster_id':
                data[c.name] = str(getattr(self, c.name))
            else:
                data[c.name] = getattr(self, c.name)
        return data

    def serialize_columns(self):
        meta = []
        for c in self.__table__.columns:
            if c.name != 'id' and c.name != 'active' and c.name != 'cluster_id':
                title = ''
                if c.name == 'name':
                    title = 'Cluster name'
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
            elif c.name == 'cluster_id':
                source = []
                for b in Cluster.query.order_by('name').all():
                    bu = {}
                    bu[b.id] = b.name
                    source.append(bu)
                meta.append({
                    'field': c.name,
                    'title': 'Cluster',
                    'sortable': True, 'editable': {
                        'type': 'select',
                        'title': 'Cluster:',
                        'source': source,
                        'ajaxOptions': {
                            'type': 'POST',
                            'success': 'function (data) { }',
                            'error': 'function (xhr, status, error) { var err = eval("(" + xhr.responseText + ")"); alert(err.Message); }'},
                            'validate': 'function (value) { value = $.trim(value); if (!value) { return \'This field is required\'; } if (!/^\$/.test(value)) { return \'This field needs to start width $.\'} var data = $table.bootstrapTable(\'getData\'), index = $(this).parents(\'tr\').data(\'index\'); console.log(data[index]); return \'\';'
                        }
                    }
                )
            elif c.name == 'active':
                meta.append({'field': c.name, 'title': c.name.capitalize(), 'sortable': True, 'editable': {'type': 'select', 'title': 'Active:', 'source': '[{value: "1", text: "Yes"}, {value: "0", text: "No"}]', 'ajaxOptions': { 'type': 'POST', 'success': 'function (data) { }', 'error': 'function (xhr, status, error) { var err = eval("(" + xhr.responseText + ")"); alert(err.Message); }'}}})
            else:
                meta.append({'field': c.name, 'title': c.name.capitalize(), 'sortable': True})

        return meta


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

    def get_host(self, environment, database):
        sql = text("SELECT "
                    " c.domainprefix || '.' || coalesce(e.domainprefix, '') || c.name || '.' || b.domain AS domain"
                    " FROM dba.database bd"
                    " INNER JOIN dba.deployment d ON bd.id = d.database_id AND d.active IS TRUE"
                    " INNER JOIN dba.environment e ON d.environment_id = e.id AND e.name = :environment AND e.active IS TRUE"
                    " INNER JOIN dba.cluster c ON c.id = d.cluster_id AND c.active IS TRUE"
                    " INNER JOIN dba.business b ON b.id = c.business_id and b.active IS TRUE"
                    " WHERE bd.name = :database"
                    " AND bd.active IS TRUE")

        result = db.session.execute(
            sql,
            {
                'environment': environment,
                'database': database
            }
        )

        data = []
        for r in result:
            bh = {}
            bh['domain'] = r[0]
            data.append(bh)

        return data

    def get_databases(self, cluster, environment):
        sql = text("SELECT "
                    " d.id AS database_id, d.name AS database"
                    " FROM dba.database d"
                    " INNER JOIN dba.environment e ON e.name = :environment AND e.active IS TRUE"
                    " INNER JOIN dba.deployment de ON d.id = de.database_id AND de.active IS TRUE AND e.id = de.environment_id"
                    " INNER JOIN dba.cluster c ON c.id = de.cluster_id AND c.id = :cluster AND c.active IS TRUE"
                    " WHERE d.active IS TRUE")

        result = db.session.execute(
            sql,
            {
                'environment': environment,
                'cluster': cluster
            }
        )

        data = []
        for r in result:
            bh = {}
            bh['database_id'] = r[0]
            bh['dbname'] = r[1]
            data.append(bh)

        return data


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

    def serialize_columns(self):
        meta = []
        for c in self.__table__.columns:
            title = ''
            if c.name == 'name':
                title = 'Environment name:'
            elif c.name == 'domainprefix':
                title = 'Domain Prefix:'
            if c.name != 'id' and c.name != 'active':
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
    environment = db.relationship('Environment', backref='environments')
    cluster_id = db.Column(
        db.Integer,
        db.ForeignKey('cluster.id'),
        nullable=False
    )
    cluster = db.relationship('Cluster', backref='clusters')
    database_id = db.Column(
        db.Integer,
        db.ForeignKey('database.id'),
        nullable=False
    )
    database = db.relationship('Database', backref='databases')
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
            elif c.name in ['cluster_id', 'database_id', 'environment_id']:
                data[c.name] = str(getattr(self, c.name))
            else:
                data[c.name] = getattr(self, c.name)
        return data
        #return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def serialize_columns(self):
        meta = []
        for c in self.__table__.columns:
            if c.name == 'cluster_id':
                source = []
                for b in Cluster.query.order_by('name').all():
                    bu = {}
                    bu[b.id] = b.name
                    source.append(bu)
                meta.append({
                    'field': c.name,
                    'title': 'Cluster',
                    'sortable': True, 'editable': {
                        'type': 'select',
                        'title': 'Cluster:',
                        'source': source,
                        'ajaxOptions': {
                            'type': 'POST',
                            'success': 'function (data) { }',
                            'error': 'function (xhr, status, error) { var err = eval("(" + xhr.responseText + ")"); alert(err.Message); }'},
                            'validate': 'function (value) { value = $.trim(value); if (!value) { return \'This field is required\'; } if (!/^\$/.test(value)) { return \'This field needs to start width $.\'} var data = $table.bootstrapTable(\'getData\'), index = $(this).parents(\'tr\').data(\'index\'); console.log(data[index]); return \'\';'
                        }
                    }
                )
            elif c.name == 'environment_id':
                source = []
                for b in Environment.query.order_by('name').all():
                    bu = {}
                    bu[b.id] = b.name
                    source.append(bu)
                meta.append({
                    'field': c.name,
                    'title': 'Environment',
                    'sortable': True, 'editable': {
                        'type': 'select',
                        'title': 'Environment:',
                        'source': source,
                        'ajaxOptions': {
                            'type': 'POST',
                            'success': 'function (data) { }',
                            'error': 'function (xhr, status, error) { var err = eval("(" + xhr.responseText + ")"); alert(err.Message); }'},
                            'validate': 'function (value) { value = $.trim(value); if (!value) { return \'This field is required\'; } if (!/^\$/.test(value)) { return \'This field needs to start width $.\'} var data = $table.bootstrapTable(\'getData\'), index = $(this).parents(\'tr\').data(\'index\'); console.log(data[index]); return \'\';'
                        }
                    }
                )
            elif c.name == 'database_id':
                source = []
                for b in Database.query.order_by('name').all():
                    bu = {}
                    bu[b.id] = b.name
                    source.append(bu)
                meta.append({
                    'field': c.name,
                    'title': 'Database',
                    'sortable': True, 'editable': {
                        'type': 'select',
                        'title': 'Database:',
                        'source': source,
                        'ajaxOptions': {
                            'type': 'POST',
                            'success': 'function (data) { }',
                            'error': 'function (xhr, status, error) { var err = eval("(" + xhr.responseText + ")"); alert(err.Message); }'},
                            'validate': 'function (value) { value = $.trim(value); if (!value) { return \'This field is required\'; } if (!/^\$/.test(value)) { return \'This field needs to start width $.\'} var data = $table.bootstrapTable(\'getData\'), index = $(this).parents(\'tr\').data(\'index\'); console.log(data[index]); return \'\';'
                        }
                    }
                )
            elif c.name == 'active':
                meta.append({'field': c.name, 'title': c.name.capitalize(), 'sortable': True, 'editable': {'type': 'select', 'title': 'Active:', 'source': '[{value: "1", text: "Yes"}, {value: "0", text: "No"}]', 'ajaxOptions': { 'type': 'POST', 'success': 'function (data) { }', 'error': 'function (xhr, status, error) { var err = eval("(" + xhr.responseText + ")"); alert(err.Message); }'}}})
            else:
                meta.append({'field': c.name, 'title': c.name.capitalize(), 'sortable': True})

        return meta


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
        default=datetime.utcnow(),
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
        db.BigInteger,
        nullable=False,
        default=0,
        server_default=text('0')
    )
    info = db.Column(
        db.Text(),
        nullable=True
    )

    def __repr__(self):
        return '<BackupHistory:(id=%s,'
        ' timecreated=%s, cluster_id=%s,'
        ' database_id=%s, scheduled=%s,'
        ' state=%s, size=%s, duration=%s,'
        ' info=%s)>' % (
            self.id,
            self.timecreated,
            self.cluster_id,
            self.database_id,
            self.scheduled,
            self.state,
            self.size,
            self.duration,
            self.info
        )

    def get_backup_history(self, date=datetime.now()):
        sql = text(
            "SELECT"
            " c.name as cluster"
            ", d.name as database"
            ", bh.timecreated"
            ", bh.state"
            ", bh.info"
            ", bh.size"
            ", bh.duration"
            ", bh.scheduled"
            " FROM dba.database d"
            " INNER JOIN dba.deployment dp"
            "   ON dp.database_id = d.id"
            "   AND dp.environment_id = 1"
            "   AND dp.active is true"
            " INNER JOIN dba.cluster c"
            "   ON dp.cluster_id = c.id"
            "   AND c.active IS true"
            " LEFT JOIN dba.backup_history bh"
            "   ON d.id = bh.database_id"
            "   AND c.id = bh.cluster_id"
            "   AND bh.timecreated::date = to_date(:thedate, 'YYYY-MM-DD')"
            " WHERE d.active is true"
            " ORDER BY c.name, d.name, bh.timecreated DESC")

        result = db.session.execute(
            sql,
            {'thedate': date.strftime('%Y-%m-%d')}
        )
        data = []
        for r in result:
            bh = {}
            bh['cluster'] = r[0]
            bh['database'] = r[1]
            bh['timecreated'] = r[2]
            bh['state'] = r[3]
            bh['info'] = r[4]
            bh['size'] = sizeof_fmt(r[5])
            bh['duration'] = r[6]
            bh['scheduled'] = r[7]
            data.append(bh)

        return data

    def serialize_columns(self):
        meta = []
        for c in self.__table__.columns:
            if c.name == 'cluster_id':
                meta.append({'field': 'cluster', 'title': 'Cluster', 'sortable': True})
            elif c.name == 'database_id':
                meta.append({'field': 'database', 'title': 'Database', 'sortable': True})
            elif c.name == 'timecreated':
                meta.append({'field': c.name, 'title': 'Backup Date', 'sortable': True})
            elif c.name == 'id':
                pass
            else:
                meta.append({'field': c.name, 'title': c.name.capitalize(), 'sortable': True})

        return meta


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
        default=datetime.utcnow(),
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
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    #@staticmethod
    #def try_login(username, password):
        #conn = get_ldap_connection()
        #conn.simple_bind_s(
        #    'cn=%s,ou=Users,dc=testathon,dc=net' % username,
        #    password
        #)
    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


def sizeof_fmt(num, suffix='B'):
    if num is None:
        return None
    else:
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(int(num)) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Y', suffix)
