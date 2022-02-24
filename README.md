# Downtime Database

![Build](https://github.com/observatorycontrolsystem/downtime/workflows/Build/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/observatorycontrolsystem/downtime/badge.svg?branch=master)](https://coveralls.io/github/observatorycontrolsystem/downtime?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/7aa8dea066824e79bb7e681122598345)](https://www.codacy.com/gh/observatorycontrolsystem/downtime?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=observatorycontrolsystem/downtime&amp;utm_campaign=Badge_Grade)

An application with a database that stores periods of scheduled telescope downtime for an observatory with an
API to access those downtimes. Within an observatory control system, downtimes can be used to block out time
for things such as maintenance activites or education use on specific telescopes.


## Prerequisites

-   Python>=3.7
-   (Optional) PostgreSQL
-   Configuration database to connect to
-   (Optional) Observation Portal for Oauth2 authentication

By default, the application uses a SQLite database. This is suitable for development, but PostgreSQL is
recommended when running in production.

## Configuration

This project is configured using environment variables.

| Variable             | Description                                                                        | Default                      |
| -------------------- | ---------------------------------------------------------------------------------- | ---------------------------- |
| `SECRET_KEY`         | Django Secret Key                                                                  | `### CHANGE ME ###`          |
| `DEBUG`              | Django Debug mode                                                                  | False                        |
| `DB_ENGINE`          | Database Engine, set to `django.db.backends.postgresql_psycopg2` to use PostgreSQL | `django.db.backends.sqlite3` |
| `DB_NAME`            | Database Name                                                                      | `db.sqlite3`                 |
| `DB_HOST`            | Database Hostname, set this when using PostgreSQL                                  | _empty string_               |
| `DB_USER`            | Database Username, set this when using PostgreSQL                                  | _empty string_               |
| `DB_PASS`            | Database Password, set this when using PostgreSQL                                  | _empty string_               |
| `DB_PORT`            | Database Port, set this when using PostgreSQL                                      | `5432`                       |
| `OAUTH_CLIENT_ID`    | OAuth authentication client id (found in observation portal admin for the app)     | ``                           |
| `OAUTH_CLIENT_SECRET`| OAuth authentication client secret (found in observation portal admin for the app) | ``                           |
| `OAUTH_TOKEN_URL`    | OAuth authentication token endpoint (observation-portal-base-url/o/token)          | ``                           |
| `OAUTH_PROFILE_URL`  | Observation portal profile api endpoint (observation-portal-base-url/api/profile)  | ``                           |
| `CONFIGDB_URL`       | Configuration database base url                                                    | ``                           |
| `LOGO_URL`           | URL to a hosted logo to display in the navbar of the web frontend                  | ``                           |

## Local Development

### **Set up a virtual environment**

Using a virtual environment is highly recommended. Run the following commands from the base of this project. `(env)`
is used to denote commands that should be run using your virtual environment.

    python3 -m venv env
    source env/bin/activate
    (env) pip install -r requirements.txt

### **Set up the database**

You may use the default SQLite for development, or you can set up using PostgreSQL. If using SQLite, you can skip directly
to running database migrations. If using PostgreSQL, the following command uses the [PostgreSQL Docker image](https://hub.docker.com/_/postgres) to
create a PostgreSQL database. Make sure that the options that you use to set up your database correspond with your configured database settings.

    docker run --name downtime-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=downtime -v/var/lib/postgresql/data -p5432:5432 -d postgres:11.1

Run database migrations to set up the tables in the database.

    (env) python manage.py migrate

### Run the tests

First collect the staticfiles since some of the tests check the admin page functionality

    (env) python manage.py collectstatic

    (env) python manage.py test --settings=test_settings

### Run the application

    (env) python manage.py runserver

The application should now be accessible from <http://127.0.0.1:8000>!

This application serves an api to read/write downtimes at /api/, and a filterable web frontend to view
downtimes at /.

### Managing downtime entries

Downtimes are added and deleted manually via the admin interface, or through the API via a POST to the /api/ endpoint.
In both cases, you must authenticate as a valid staff/admin User via the Observation Portal to get write access.
This is done with a user/pass form submission via the admin interface, or using HTTPBasicAuth with the user/pass
as part of an API POST.

There is also a django management command to create downtimes:

    (env) python manage.py create_downtime help

## Example API queries

A downtime entry in the database is returned in JSON and has the following format:

    {
        "start": "2017-08-21T08:45:00Z",
        "end": "2017-08-21T09:45:00Z",
        "site": "coj",
        "enclosure": "clma",
        "telescope": "0m4a",
        "reason": "Maintenance"
    }

Return all downtimes

    GET /api/

Return the downtimes past a specific date:

    GET /api/?starts_after=2017-11-27%2014:45:00

Return the downtimes before a specific date:

    GET /api/?ends_before=2017-08-24%2015:15:00

Filter downtimes by reason:

    GET /api/?reason=Maintenance

Filter downtimes by site, enclosure and telescope:

    GET /api/?site=ogg&enclosure=clma&telescope=0m4a
