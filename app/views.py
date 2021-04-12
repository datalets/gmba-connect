#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, admin
from .models import *
from .formats import *
from .convert import reindex_data, refresh_data

from flask_admin.contrib.sqla import ModelView, filters
from flask_admin.form import FileUploadField
from flask_admin import (
    BaseView, expose
)
from flask import (
    url_for, redirect, Response,
    request, flash,
    render_template,
    send_from_directory,
)

from werkzeug.utils import secure_filename
from sqlalchemy import or_

import csv, json, time, traceback
import os.path as ospath
from os import makedirs
from shutil import move
from tempfile import gettempdir

# Get temporary file storage
UPLOAD_PATH = gettempdir()
DATA_PATH = ospath.join(ospath.dirname(__file__), '..')
if not ospath.exists(DATA_PATH): makedirs(DATA_PATH)
def get_datafile(fmt):
    return ospath.join(
        DATA_PATH,
        fmt['folder'],
        fmt['filename'] + '.' + fmt['extension']
    )

# Administrative views
class PersonView(ModelView):
    column_list = ('first_name', 'last_name', 'organisation')
admin.add_view(PersonView(Person, db.session))

class ResourceView(ModelView):
    column_list = ('title', 'url')
admin.add_view(ResourceView(Resource, db.session))

class RangeView(ModelView):
    column_list = ('name', 'countries')
admin.add_view(RangeView(Range, db.session))

admin.add_view(ModelView(Method, db.session))
admin.add_view(ModelView(Scale, db.session))
admin.add_view(ModelView(Taxon, db.session))
admin.add_view(ModelView(Field, db.session))

# Custom view
class ConfigurationView(BaseView):
    @expose('/')
    def index(self):
        fmts = DATAFORMATS
        for f in fmts: f['ready'] = ospath.isfile(get_datafile(f))
        return self.render('admin/config.html', dataformats=fmts)

admin.add_view(ConfigurationView(name='Configuration', endpoint='config'))


def get_paginated(query):
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    ppp = query.paginate(page, per_page, error_out=False)
    filters = {
       'country': [],
       'range': [],
       'field': [],
       'taxon': [],
    }
    for p in ppp.items:
        filters['country'].append(p.country)
        for r in p.ranges:
            filters['range'].append(r.name)
        for r in p.research_fields:
            filters['field'].append(r.name)
        for r in p.research_taxa:
            filters['taxon'].append(r.name)
    filters = {
       'country': sorted(set(filters['country'])),
       'range': sorted(set(filters['range'])),
       'field': sorted(set(filters['field'])),
       'taxon': sorted(set(filters['taxon'])),
    }
    if len(query.all()) > len(ppp.items) and ppp.pages == 1:
        ppp.items = query.all()
        ppp.total = len(ppp.items)
    return {
        'items': [p.dict() for p in ppp.items],
        'filters': filters,
        'page': page, 'pages': ppp.pages, 'total': ppp.total,
        'has_next': ppp.has_next, 'has_prev': ppp.has_prev
    }

# API views
FILTER_QUERIES = [ 'country', 'range', 'field', 'taxon' ]

@app.route("/api/search", methods=['GET'])
def search_list():
    ra = request.args
    q = ra.get('q').strip()
    if not q or len(q) < 3:
        query = Person.query
    else:
        query = Person.query
        clauses = [Person._indexer.ilike('%{0}%'.format(k)) for k in q.split(" ")]
        query = query.filter(*clauses)

    if ra.get('country') and len(ra.get('country')) > 2:
        query = query.filter(
            Person.country.ilike("%" + ra.get('country').strip().lower() + "%")
        )
    if ra.get('range') and len(ra.get('range')) > 2:
        query = query.join(Person.ranges).filter(
            Range.name.ilike("%" + ra.get('range').strip().lower() + "%")
        )
    if ra.get('field') and len(ra.get('field')) > 2:
        query = query.join(Person.research_fields).filter(
            Field.name.ilike("%" + ra.get('field').strip().lower() + "%")
        )
    if ra.get('taxon') and len(ra.get('taxon')) > 2:
        query = query.join(Person.research_taxa).filter(
            Taxon.name.ilike("%" + ra.get('taxon').strip().lower() + "%")
        )

    query = query.order_by(Person.last_name.asc())
    return get_paginated(query)

@app.route("/api/people/<int:people_id>", methods=['GET'])
def people_detail(people_id):
    person = Person.query.filter_by(id=people_id).first_or_404()
    return {
        'data': person.dict(),
        'resources': [r.dict() for r in person.resources],
        'ranges': [r.dict() for r in person.ranges],
        'fields': [r.name for r in person.research_fields],
        'methods': [r.name for r in person.research_methods],
        'scales': [r.name for r in person.research_scales],
        'taxa': [r.name for r in person.research_taxa],
    }

@app.route("/api/people", methods=['GET'])
def people_list():
    return get_paginated(Person.query.order_by(Person.last_name.asc()))

@app.route("/api/resources", methods=['GET'])
def resources_list():
    return get_paginated(Resource.query.order_by(Resource.title.asc()))

MAX_FILTER_RESULTS = 50

@app.route("/api/ranges", methods=['GET'])
def ranges_list():
    q = request.args.get('q')
    if not q or len(q) < 3:
        return [r.dict() for r in Range.query.order_by(Range.name.asc()).limit(MAX_FILTER_RESULTS).all()]
    else:
        return [r.dict() for r in Range.query.filter(Range.name.ilike("%" + q.strip().lower() + "%")).all()]

@app.route("/api/fields", methods=['GET'])
def fields_list():
    q = request.args.get('q')
    if not q or len(q) < 3:
        return [r.dict() for r in Field.query.order_by(Field.name.asc()).limit(MAX_FILTER_RESULTS).all()]
    else:
        return [r.dict() for r in Field.query.filter(Field.name.ilike("%" + q.strip().lower() + "%")).all()]

@app.route("/api/taxa", methods=['GET'])
def taxa_list():
    q = request.args.get('q')
    if not q or len(q) < 3:
        return [r.dict() for r in Taxon.query.order_by(Taxon.name.asc()).limit(MAX_FILTER_RESULTS).all()]
    else:
        return [r.dict() for r in Taxon.query.filter(Taxon.name.ilike("%" + q.strip().lower() + "%")).all()]


#@app.errorhandler(Exception)
#def handle_exception(error):
#    response = json.dumps(error.to_dict())
#    response.status_code = error.status_code
#    return response

# Data upload
@app.route('/upload', methods=['GET', 'POST'])
def upload_data():
    if request.method == 'POST' and 'datafile' in request.files:
        fs = request.files['datafile']
        fs_name = secure_filename(fs.filename)
        fs_path = ospath.join(UPLOAD_PATH, fs_name)
        fs.save(fs_path)
        app.logger.info('Uploading: %s' % fs_name)

        # Validation
        fmt = None
        if fs_name.endswith('.csv'):
            with open(fs_path, 'rt', encoding='utf-8', errors='ignore') as csvfile:
                datareader = csv.DictReader(csvfile)
                datalist = list(datareader)
                fmt = detect_dataformat(datalist[0])

        elif fs_name.endswith('.geojson'):
            with open(fs_path, 'rt', encoding='utf-8', errors='ignore') as jsonfile:
                jsondata = json.load(jsonfile)
                fmt = detect_dataformat(jsondata['features'][0]['properties'])

        # Loading
        if fmt is not None:
            fs_target = get_datafile(fmt)
            move(fs_path, fs_target)
            flash("Uploaded new data file %s" % fmt['filename'], 'success')
        else:
            flash("Could not validate data format!", 'error')
    else:
        flash("Please select a valid file", 'error')
    return redirect(url_for('config.index'))

# Data update tracking
c_progress = 0
c_filename = ""

@app.route('/refresh', methods=["POST"])
def refresh_all():
    global c_progress
    c_progress = 0
    def generate():
        stats = []
        total = 0
        for fmt in DATAFORMATS:
            global c_filename
            c_filename = fmt['filename']
            filename = get_datafile(fmt)
            c = 1
            c_counter = 0
            rd = refresh_data(filename, fmt)
            while c is not None:
                try:
                    c, p = next(rd)
                except Exception as e:
                    yield 'error: %s' % str(e)
                    traceback.print_exc()
                    return
                if isinstance(c, (int, float)):
                    global c_progress
                    c_counter = c
                    if isinstance(p, (int, float)):
                        c_progress = p
                    yield str(c) + "\n\n"
                elif isinstance(p, str) and isinstance(c, str):
                    # Error condition
                    yield p + ": " + c + "\n\n"
                    return

            stats.append({ 'format': fmt['dataformat'], 'count': c_counter })
            app.logger.info("Refresh: %d counted at %s" % (c_counter, fmt['dataformat']))
            total = total + c_counter

        yield "done: %d objects updated" % total
        app.logger.info("Refresh: %d objects updated" % total)

        c_progress = 0
        c_filename = ""
    return Response(generate(), mimetype='text/html')

# EventStream for progress bar
@app.route('/progress')
def get_progress():
    global c_progress
    global c_filename
    def generate():
        while 1:
            p = str(100*c_progress)
            yield 'data: { "p":'+p+',"f":"'+c_filename+'"}\n\n'
            time.sleep(1.0)
    return Response(generate(), mimetype='text/event-stream', headers={'X-Accel-Buffering': 'no'})

# Refresh search index
@app.route('/reindex', methods=['POST'])
def reindex():
    global c_progress
    c_progress = 0
    global c_filename
    c_filename = ""
    reindex_data()
    flash("Search engine refresh complete")
    app.logger.info("Search engine reindexed")
    return redirect(url_for('config.index'))

# Additional paths

@app.route('/data/<path:path>')
def send_data(path):
    return send_from_directory('../data', path)

@app.route('/geodata/<path:path>')
def send_geodata(path):
    return send_from_directory('../geodata', path)

# Home paths

@app.route('/demo')
def home_demo():
    return render_template('demo.html')

@app.route('/offline')
def home_offline():
    return render_template('offline.html')

@app.route('/')
def home_page():
    return render_template('index.html')
