## GMBA Connect

A search engine and members directory for the Global Mountain Biodiversity Assessment (GMBA) research network.

## Installation

Get a hold of **Python 3** and [Pipenv](https://github.com/pypa/pipenv) on your machine.

    $ git clone https://gitlab.com/datalets/gmba-connect.git

To install and start the backend using Pipenv (Pip and Virtualenv should work fine too):

    $ pipenv --three
    $ pipenv install

To create a blank database or upgrade the configured one:

    $ flask db upgrade

To initialize and/or migrate the database, if necessary:

    $ flask db init
    $ flask db migrate

To start the backend:

    $ export FLASK_ENV="development"
    $ export FLASK_DEBUG=1
    $ python run.py

The app will now be available, and you can access the backend administration at http://0.0.0.0:5000/admin/

## Administration

In the backend you can manage all the data, as well as importing data exports in CSV format which are uploaded in the `data` subfolder.

Check the log for the port and URL to the admin interface, which will by default in production be randomly generated on every app start. You can override this by setting the `ADMIN_PATH` environment variable.

To update the mountain shapes, replace the `geodata/gmba.geojson` file.

## Deployment

Use a WSGI server like Gunicorn to host the app in production mode, e.g.:

`gunicorn app:app`

The `Procfile` in this project folder makes it ready for deployment to Heroku.

## License

MIT - details in [LICENSE](LICENSE) file.
