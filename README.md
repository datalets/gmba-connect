## GMBA Connect

A search engine and members directory for the Global Mountain Biodiversity Assessment (GMBA) research network.

## Usage

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

    $ FLASK_ENV="dev" FLASK_DEBUG=1 python run.py

The frontend interface will now be available.

Check the log for the port and URL to the admin interface, which will be newly generated on every app start.

Note: for development purposes an `offline.html` file loads un-minified JavaScript packages from the local server, not CDNs. 
To use this, first install the packages using `yarn` from the root folder.

## Deployment

Use a WSGI server like Gunicorn to host the app in production mode, e.g.:

`gunicorn app:app`

The `Procfile` in this project folder makes it ready for deployment to Heroku.

## License

MIT - details in [LICENSE](LICENSE) file.
