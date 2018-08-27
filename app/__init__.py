from flask import Flask, Markup
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy

import flask_admin as admin

# Create application
app = Flask(__name__, static_url_path='')
app.debug = True
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

api = Api(app,
          version='0.1',
          title='GMBA connect',
          description='Hello, world')

admin = admin.Admin(app, name='GMBA Connect', template_mode='bootstrap3')

def init_app():
    db.create_all()

# https://medium.freecodecamp.org/structuring-a-flask-restplus-web-service-for-production-builds-c2ec676de563
# https://flask-restplus.readthedocs.io/en/stable/example.html
# https://flask-restplus.readthedocs.io/en/stable/marshalling.html
# http://michal.karzynski.pl/blog/2016/06/19/building-beautiful-restful-apis-using-flask-swagger-ui-flask-restplus/
# https://medium.com/@camillovisini/barebone-flask-rest-api-ac263db82e40

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()
