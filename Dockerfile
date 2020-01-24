FROM python:3.6-alpine

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN apk --no-cache add postgresql-libs \
        && apk --no-cache add --virtual .build-deps gcc postgresql-dev musl-dev \
        && pip --no-cache-dir install -r requirements.txt \
        && apk --no-cache del .build-deps

# Install this application
COPY . .

# Collect static files ahead of time
RUN python manage.py collectstatic --noinput

# Default command
CMD [ "gunicorn", "--workers=2", "--bind=0.0.0.0:80", "--user=daemon", "--group=daemon", "--access-logfile=-", "--error-logfile=-", "downtime.wsgi" ]
