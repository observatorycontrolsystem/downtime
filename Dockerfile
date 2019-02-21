FROM python:3.6-alpine

EXPOSE 80
WORKDIR /downtime

# Install Python dependencies
COPY requirements.txt .
RUN apk --no-cache add mariadb-connector-c \
        && apk --no-cache add --virtual .build-deps gcc mariadb-connector-c-dev musl-dev \
        && pip --no-cache-dir --trusted-host=buildsba.lco.gtn install -r requirements.txt \
        && apk --no-cache del .build-deps

# Install this application
COPY . .

# Collect static files ahead of time
RUN python manage.py collectstatic --noinput

# Default command
CMD [ "gunicorn", "--workers=2", "--bind=0.0.0.0:80", "--user=daemon", "--group=daemon", "--access-logfile=-", "--error-logfile=-", "downtime.wsgi" ]
