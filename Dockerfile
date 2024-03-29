FROM python:3.9-alpine

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml poetry.toml poetry.lock .poetry-version ./
RUN  apk update && apk upgrade \
        && apk --no-cache add bash git openssh \
        && apk --no-cache add postgresql-libs \
        && apk --no-cache add --virtual .build-deps gcc postgresql-dev musl-dev \
        && pip --no-cache-dir install -U pip setuptools \
        && pip --no-cache-dir install -r .poetry-version \
        && poetry export > requirements.txt \
        && pip --no-cache-dir install -r requirements.txt \
        && apk --no-cache del .build-deps

# Install this application
COPY . .

# Collect static files ahead of time
RUN python manage.py collectstatic --noinput

# Default command
CMD [ "gunicorn", "--workers=2", "--bind=0.0.0.0:80", "--user=daemon", "--group=daemon", "--access-logfile=-", "--error-logfile=-", "downtime.wsgi" ]
