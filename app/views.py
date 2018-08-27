#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, admin

from .models import *
from .formats import *
from .convert import refresh_data

from flask_admin.contrib.sqla import ModelView, filters
from flask_admin.form import FileUploadField
from flask_admin import (
    BaseView, expose
)
from flask import (
    url_for, redirect,
    request, flash,
    render_template,
    send_from_directory,
)
from werkzeug import secure_filename

import csv, json
import os.path as ospath
from shutil import move
from tempfile import gettempdir

# Get temporary file storage
UPLOAD_PATH = gettempdir()
DATA_PATH = ospath.join(ospath.dirname(__file__), '..', 'data')

# Administrative views
class PersonView(ModelView):
    column_list = ('first_name', 'last_name', 'organisation')
admin.add_view(PersonView(Person, db.session))

class ResourceView(ModelView):
    column_list = ('title', 'citation', 'url')
admin.add_view(ResourceView(Resource, db.session))

class RangeView(ModelView):
    column_list = ('name', 'countries')
admin.add_view(RangeView(Range, db.session))

# Custom view
class ConfigurationView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/config.html', DATAFORMATS=DATAFORMATS)

admin.add_view(ConfigurationView(name='Configuration', endpoint='config'))

# Data upload endpoint
@app.route('/upload', methods=['GET', 'POST'])
def upload_data():
    if request.method == 'POST' and 'datafile' in request.files:
        fs = request.files['datafile']
        fs_name = secure_filename(fs.filename)
        fs_path = ospath.join(UPLOAD_PATH, fs_name)
        fs.save(fs_path)

        # Validation
        count = 0
        fmt = None
        if fs_name.endswith('.csv'):
            with open(fs_path, 'rt') as csvfile:
                datareader = csv.DictReader(csvfile)
                fmt = detect_dataformat(datareader)
                if fmt is not None:
                    count = length(datareader)

        elif fs_name.endswith('.geojson'):
            with open(fs_path, 'rt') as jsonfile:
                jsondata = json.load(jsonfile)
                fmt = detect_dataformat(jsondata['features'][0]['properties'])
                if fmt is not None:
                    count = length(jsondata['features'])

        # Loading
        if count > 0 and fmt is not None:
            fs_target = ospath.join(DATA_PATH, fmt['filename'] + '.' + fmt['extension'])
            move(fs_path, fs_target)
            flash("Uploaded, validated and imported %d objects for " %
                (count, fmt['filename']))
            return refresh_data(fs_target, fmt)
        else:
            flash("Could not detect data format!")
    else:
        flash("Please select a valid file")
    return redirect(url_for('config.index'))

# Data update endpoint
@app.route('/refresh', methods=["POST"])
def refresh_all():
    stats = []
    count_total = 0
    for fmt in DATAFORMATS:
        filename = ospath.join(DATA_PATH, fmt['filename'] + '.' + fmt['extension'])
        count = refresh_data(filename, fmt)
        if count is None:
            return redirect(url_for('config.index'))
        stats.append({ 'format': fmt['dataformat'], 'count': count })
        count_total = count_total + count
    flash("%d objects updated" % (count_total))
    print(stats)
    return redirect(url_for('config.index'))

# Static paths
@app.route('/data/<path:path>')
def send_data(path):
    return send_from_directory('../data', path)
@app.route('/client/<path:path>')
def send_client(path):
    return send_from_directory('../client', path)
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('../static', path)
