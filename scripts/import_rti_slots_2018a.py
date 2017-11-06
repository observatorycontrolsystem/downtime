import csv
import datetime
from schedule.models import Downtime


with open('rti_slots_2018a.csv') as csvfile:
    rtireader = csv.DictReader(csvfile)
    for i, row in enumerate(rtireader):
        if not row['Day']:
            continue

        observatory = 'clma'
        site = row['Site'].lower()
        telescope = row['Tel']

        # Figure out the dates
        day, month = row['Date'].split('-')
        year = '2017' if month == 'Dec' else '2018'
        start_time = row['UT Start']
        end_time = row['UT End']

        formatter = '%Y-%b-%dT%H:%M:%S'
        start = datetime.datetime.strptime(f'{year}-{month}-{day}T{start_time}', formatter)
        end = datetime.datetime.strptime(f'{year}-{month}-{day}T{end_time}', formatter)

        print('Submitting:', start, end, site, observatory, telescope, 'where downtime is', (end-start).seconds/60, 'minutes long.')

        Downtime.objects.create(start=start, end=end, site=site, observatory=observatory, telescope=telescope, reason='RTI')
