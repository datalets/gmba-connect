#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import api

from flask_restplus import Resource, fields
from .models import *

person_api = api.namespace('person')
api.add_namespace(person_api)

@person_api.route('/')
class PersonList(Resource):

    # @person_api.response(PersonSchema(many=True))
    # def get(self):
    #     return Person.query.all()

    model = api.model('Model', {
        'id': fields.Integer,
        'fullname': fields.String,
        'organisation': fields.String,
    })
    @api.marshal_with(model, envelope='resource')
    def get(self, **kwargs):
        return Person.query.all()
