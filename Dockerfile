FROM python:3.6
MAINTAINER Austin Riba <ariba@lco.global>

EXPOSE 80
CMD gunicorn downtime.wsgi -b 0.0.0.0:80
WORKDIR /downtime

COPY requirements.txt /downtime
RUN pip install gunicorn -r /downtime/requirements.txt --trusted-host=buildsba.lco.gtn && rm -rf /root/.cache/pip

COPY . /downtime
RUN python manage.py collectstatic --noinput
