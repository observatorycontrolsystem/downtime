import csv
import datetime
from schedule.models import Downtime


def _get_year(filename, month):
    return {
        'rti_slots_2018a.csv': '2017' if month == 'Dec' else '2018',
        'rti_slots_2018b.csv': '2018',
        'rti_slots_2019a.csv': '2018' if month == 'Dec' else '2019',
        'rti_slots_2019b.csv': '2019',
     }[filename]


def submit_slots(filename, submit):
    with open(filename) as csvfile:
        rtireader = csv.DictReader(csvfile)
        for i, row in enumerate(rtireader):
            if not row['Day']:
                continue

            observatory = 'clma'
            site = row['Site'].lower()
            telescope = row['Tel']

            # Figure out the dates
            day, month = row['Date'].split('-')
            year = _get_year(filename, month)
            start_time = row['UT Start']
            end_time = row['UT End']

            formatter = '%Y-%b-%dT%H:%M:%S'
            start = datetime.datetime.strptime(f'{year}-{month}-{day}T{start_time}', formatter)
            end = datetime.datetime.strptime(f'{year}-{month}-{day}T{end_time}', formatter)

            print('Will submit:', start, end, site, observatory, telescope, 'where downtime is', (end-start).seconds/60, 'minutes long.')
            if submit:
                print('Submitting downtimes')
                Downtime.objects.create(start=start, end=end, site=site, observatory=observatory, telescope=telescope, reason='RTI')


if __name__ == '__main__':
    # Submit RTI downtimes. Input file must be formatted like rti_slots_2018a.csv.
    # Update the filename and set submit to True to submit downtimes.
    filename = 'rti_slots_2019b.csv'
    submit = False
    submit_slots(filename, submit)
