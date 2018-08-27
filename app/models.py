#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db

resources_people = db.Table(
    'resources_people',
    db.Column('person_id', db.Integer(), db.ForeignKey('person.id')),
    db.Column('resource_id', db.Integer(), db.ForeignKey('resource.id'))
)

# Country	Biography	Field of expertise	Taxa	Methods	Geographic area of expertise	Scale	ProfileOnWeb

RESEARCH_SCALES = (
    '', '', '', ''
)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer)
    title = db.Column(db.Unicode(16))
    first_name = db.Column(db.Unicode(128))
    last_name = db.Column(db.Unicode(128))

    organisation = db.Column(db.Unicode(128))
    position = db.Column(db.Unicode(128))
    country = db.Column(db.Unicode(128))
    biography = db.Column(db.UnicodeText)

    contact_email = db.Column(db.Unicode(255))
    personal_url = db.Column(db.Unicode(255))

    # research_scale = db.Column(db.Enum(*RESEARCH_SCALES, name="researchscale"))
    # expertise_field = db.Column(db.Unicode(255))
    # expertise_geo = db.Column(db.Unicode(255))
    resources = db.relationship('Resource', secondary=resources_people,
        backref=db.backref('people', lazy='dynamic'))

    def fullname(self):
        return " ".join([ self.title, self.first_name, self.last_name ])
    def __repr__(self):
        return self.fullname()
    def dict(self):
        return {
            'fullname': self.fullname(),
            'organisation': self.organisation,
            'position': self.position,
            'country': self.country,
            'personal_url': self.personal_url,
            'biography': self.biography,
        }

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer)
    title = db.Column(db.String(255), unique=True)
    citation = db.Column(db.String(255))
    url = db.Column(db.String(255))
    abstract = db.Column(db.UnicodeText)
    def __repr__(self):
        return self.title
    def dict(self):
        r = {
            'id': self.id,
            'title': self.title,
            'citation': self.citation,
            'url': self.url,
            'abstract': self.abstract,
        }

class Range(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer)
    name = db.Column(db.String(255), unique=True)
    countries = db.Column(db.String(255))
    def __repr__(self):
        return self.name
    def dict(self):
        r = {
            'id': self.id,
            'name': self.name,
            'countries': self.countries,
        }
