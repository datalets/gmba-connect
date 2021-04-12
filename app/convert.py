import csv, json, re
from app import app
from os.path import isfile
from .models import *
from .formats import *

# Correct commas inside of a linked field
def fix_bracketed_lists(data):
    for fix in re.findall(r'\([^\s]*,[ ]*[^\s]*\)', data):
        data = data.replace(fix, fix.replace(',', ' /'))
    return data

# Check for valid link
def fix_url(link):
    if len(link) > 3 and not link.startswith('http'):
        link = 'http://' + link
    # link = link.split(';')[0]
    return link

# Create linked objects
def add_linked(person, field, obj, data):
    # TODO: fuzzy matching instead of lower()
    items = fix_bracketed_lists(data).lower()
    items = items.replace(';',',').split(',')
    for i in items:
        n = i.strip()
        if len(n)<3: continue
        tgt = obj.query.filter_by(name=n).first()
        if not tgt:
            tgt = obj()
            tgt.name = n
        db.session.add(tgt)
        field.append(tgt)

# Fetch an object by source_id (numeric identifier used in source DB)
def get_by_id(rowid, obj, first=True):
    if type(rowid) is str and rowid.isdigit():
        rowid = int(rowid)
    if type(rowid) is int:
        l = obj.query.filter_by(source_id=rowid)
        if first: return l.first(), rowid
        else: return l, rowid
    return None, None

# Quick check of the number of lines
def get_total_rows_csv(filename):
    with open(filename) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

# Search index routine
def reindex_data():
    for i, p in enumerate(Person.query.all()):
        p.index()
        db.session.add(p)
        if i % 10 == 0: db.session.commit()
    db.session.commit()

# Data update routine
def refresh_data(filename, fmt=None):
    count = 0
    rowcount = 0
    if not isfile(filename):
        msg = "Missing data: %s  - refresh aborted." % fmt['filename']
        app.logger.warn(msg)
        yield(msg, "error")
        return None
    if fmt['extension'] == 'csv':
        totalrows = get_total_rows_csv(filename)
        with open(filename, 'rt', encoding='utf-8', errors='ignore') as csvfile:

            datareader = csv.DictReader(csvfile)
            for row in datareader:
                rowcount += 1
                if row is None: continue
                yield rowcount, rowcount/totalrows

                # Ensure any new data is flushed from time to time
                if count % 25 == 0:
                    db.session.commit()

                for r in fmt['required']:
                    if not r in row:
                        msg = "Missing attribute in %s (%s)" % (r, fmt['filename'])
                        app.logger.warn(msg)
                        yield(msg, "error")
                        return None

                if fmt['dataformat'] is DataFormat.PERSON_DETAIL:
                    person, source_id = get_by_id(row['ID'], Person)
                    if not person:
                        person = Person.query.filter_by(first_name=row['First name'], last_name=row['Last name']).first()
                    if not person:
                        person = Person(first_name=row['First name'], last_name=row['Last name'], source_id=row['ID'])

                    # Update data fields
                    person.source_id = source_id
                    person.title = row['Title']
                    person.organisation = row['Organisation English']
                    person.country = row['Country']
                    person.position = row['Position']
                    person.biography = row['Biography']
                    person.contact_email = row['e-mail 1']
                    person.personal_url = fix_url(row['URL'])

                    with db.session.no_autoflush:
                        add_linked(person, person.research_methods, Method, row['Methods'])
                        add_linked(person, person.research_scales,  Scale,  row['Scale'])
                        add_linked(person, person.research_taxa,    Taxon,  row['Taxa'])
                        add_linked(person, person.research_fields,  Field,  row['Field of expertise'])

                    person.index()
                    db.session.add(person)
                    count = count + 1

                elif fmt['dataformat'] is DataFormat.RESOURCE_DETAIL:
                    res, source_id = get_by_id(row['ID'], Resource)
                    if not res: res = Resource(source_id=source_id)
                    res.title = row['Title']
                    res.citation = row['Citation']
                    res.url = fix_url(row['URL'].strip('#')) # remove weird #formatting#
                    res.abstract = row['Abstract']
                    db.session.add(res)
                    count = count + 1

                elif fmt['dataformat'] is DataFormat.RANGE_DETAIL:
                    rng, source_id = get_by_id(row['Range_ID'], Range)
                    if not rng: rng = Range(source_id=source_id)
                    rng.gmba_id = row['GMBA_ID']
                    rng.name = row['RangeName']
                    rng.countries = row['Countries']
                    db.session.add(rng)
                    count = count + 1

                elif fmt['dataformat'] is DataFormat.PERSON_RESOURCE:
                    rzs, source_id = get_by_id(row['Resource'], Resource, first=False)
                    if not rzs or not rzs.first(): continue
                    ppl, source_id = get_by_id(row['Person'], Person, first=False)
                    if not ppl or not ppl.first(): continue
                    for person in ppl:
                        for r in rzs: person.resources.append(r)
                        db.session.add(person)
                        count = count + 1

                elif fmt['dataformat'] is DataFormat.PERSON_RANGE:
                    rzs, source_id = get_by_id(row['MountainRange'], Range, first=False)
                    if not rzs or not rzs.first(): continue
                    ppl, source_id = get_by_id(row['Person'], Person, first=False)
                    if not ppl or not ppl.first(): continue
                    for person in ppl:
                        for r in rzs: person.ranges.append(r)
                        db.session.add(person)
                        count = count + 1

    elif fmt['extension'] == 'geojson':
        ranges_missing = []
        with open(filename, 'rt', encoding='utf-8', errors='ignore') as jsonfile:
            jsondata = json.load(jsonfile)
            if fmt['dataformat'] is DataFormat.RANGE_SHAPES:
                totalrows = len(jsondata['features'])
                for f in jsondata['features']:
                    yield count, count/totalrows
                    count = count + 1

                    p = f['properties']
                    rge = Range.query.filter_by(gmba_id=p['GMBA_ID']).first()
                    if not rge:
                        ranges_missing.append(p['GMBA_ID'])
                        continue
                    rge.name = p['Name']
                    for c in ['Country_1', 'Country_2_']:
                        if c in p: rge.countries = p[c]
                    db.session.add(rge)
                app.logger.info("Warning: %d ranges not found" % len(ranges_missing))
                app.logger.debug("[%s]" % ', '.join(ranges_missing))

    db.session.commit()
    yield None, None
    return count
