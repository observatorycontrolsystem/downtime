# Downtime Database

[![Build Status](https://travis-ci.com/observatorycontrolsystem/downtime.svg?branch=master)](https://travis-ci.com/observatorycontrolsystem/downtime)
[![Coverage Status](https://coveralls.io/repos/github/observatorycontrolsystem/downtime/badge.svg?branch=master)](https://coveralls.io/github/observatorycontrolsystem/downtime?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/7aa8dea066824e79bb7e681122598345)](https://www.codacy.com/gh/observatorycontrolsystem/downtime?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=observatorycontrolsystem/downtime&amp;utm_campaign=Badge_Grade)

An application with a database that stores periods of scheduled telescope downtime for an observatory with an
API to access those downtimes. Within an observatory control system, downtimes can be used to block out time
for things such as maintenance activites or education use on specific telescopes.

## Prerequisites

-  Python>=3.6
-  (Optional) PostgreSQL

By default, the application uses a SQLite database. This is suitable for development, but PostgreSQL is
recommended when running in production.

## Configuration

This project is configured using environment variables.

| Environment Variable | Description                                                                       | Default                      |
| -------------------- | --------------------------------------------------------------------------------- | ---------------------------- |
| `SECRET_KEY`         | Django Secret Key                                                                 | `### CHANGE ME ###`          |
| `DB_ENGINE`          | Database Engine. To use PostgreSQL, set `django.db.backends.postgresql_psycopg2`. | `django.db.backends.sqlite3` |
| `DB_NAME`            | Database Name                                                                     | `db.sqlite3`                 |
| `DB_HOST`            | Database Hostname when using PostgreSQL. Not required when using SQLite.          | _empty string_               |
| `DB_USER`            | Database Username when using PostgreSQL. Not required when using SQLite.          | _empty string_               |
| `DB_PASS`            | Database Password when using PostgreSQL. Not required when using SQLite.          | _empty string_               |
| `DB_PORT`            | Database Port when using PostgreSQL. Not required when using SQLite.              | `5432`                       |

## Local Development

### **Set up a virtual environment**

Using a virtual environment is highly recommended. Run the following commands from the base of this project. `(env)`
is used to denote commands that should be run using your virtual environment.

    python3 -m venv env
    source env/bin/activate
    (env) pip install -r requirements.txt

### **Set up the database**

You may use the default SQLite for development, or you can set up a PostgreSQL. If using SQLite, you can skip directly
to running database migrations. If using PostgreSQL, the following command uses the [PostgreSQL Docker image](https://hub.docker.com/_/postgres) to
create a PostgreSQL database. Make sure that the options that you use to set up your database correspond with your configured database settings.

    docker run --name downtime-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=downtime -v/var/lib/postgresql/data -p5432:5432 -d postgres:11.1

Run database migrations to set up the tables in the database.

    (env) python manage.py migrate

### Run the tests

    (env) python manage.py test

### Run the downtime database

    (env) python manage.py runserver

The application should now be accessible from <http://127.0.0.1:8000>!

### Managing downtime entries

Downtimes are added and deleted manually via the admin interface. In order to manage downtimes, you must
first create a superuser. Run the following and fill out all of the questions:

    (env) python manage.py createsuperuser
    
You can then log in as the newly created superuser at <http://127.0.0.1:8000/admin/> to manage downtimes.

## Example queries

A downtime entry in the database is returned in JSON and has the following format:

    {
        "start": "2017-08-21T08:45:00Z",
        "end": "2017-08-21T09:45:00Z",
        "site": "coj",
        "observatory": "clma",
        "telescope": "0m4a",
        "reason": "Maintenance"
    }

Return all downtimes

    GET /

Return the downtimes past a specific date:

    GET /?start__gte=2017-11-27%2014:45:00

Return the downtimes before a specific date:

    GET /?end__lte=2017-08-24%2015:15:00

Filter downtimes by reason:

    GET /?reason=Maintenance

Filter downtimes by site, observatory and telescope:

    GET /?site=ogg&observatory=clma&telescope=0m4a
