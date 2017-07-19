import csv
import datetime

with open('rtischedule.txt') as csvfile:
    rtireader = csv.reader(csvfile)
    for row in rtireader:
        print(', '.join(row))
        start = datetime.datetime.strptime(row[0], '%d-%m-%YT%H:%M:%SZ')
        end = datetime.datetime.strptime(row[1], '%d-%m-%YT%H:%M:%SZ')
        site = row[2].lower()
        observatory = row[3]
        telescope = row[4]
        Downtime.objects.create(start=start, end=end, site=site, observatory=observatory, telescope=telescope, reason='RTI')

