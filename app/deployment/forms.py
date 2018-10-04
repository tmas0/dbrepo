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


from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField
from wtforms.validators import DataRequired


class DeploymentForm(FlaskForm):
    cluster = SelectField(
        label=u'Cluster',
        coerce=int,
        validators=[DataRequired()]
    )
    database = SelectField(
        label=u'Database',
        coerce=int,
        validators=[DataRequired()]
    )
    environment = SelectField(
        label=u'Environment',
        coerce=int,
        validators=[DataRequired()]
    )
    active = BooleanField(u'Active', validators=[DataRequired()])