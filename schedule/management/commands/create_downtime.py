from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
import logging
import sys
from schedule.models import Downtime


logger = logging.getLogger()


class Command(BaseCommand):
    help = 'Creates a downtime entry using the given parameters'

    def add_arguments(self, parser):
        parser.add_argument('-s', '--site', default='cit', type=str,
                            help='Site code (3 characters)')
        parser.add_argument('-e', '--enclosure', default='doma', type=str,
                            help='Enclosure code (4 characters)')
        parser.add_argument('-t', '--telescope', default='1m0a', type=str,
                            help='Telescope code (4 characters)')
        parser.add_argument('-r', '--reason', default='Scheduled Maintenance', type=str,
                            help='Reason for downtime')
        parser.add_argument('--start', default=datetime.now(), type=datetime.fromisoformat,
                            help='Start of downtime (datetime in isoformat)')
        parser.add_argument('--end', default=datetime.now() + timedelta(days=1), type=datetime.fromisoformat,
                            help='End of downtime (datetime in isoformat)')
        parser.add_argument('--offset-hours', dest='offset_hours', default=0, type=float,
                            help='Offset hours from current time for the start of your downtime')
        parser.add_argument('--duration-hours', dest='duration_hours', default=0, type=float,
                            help='Duration in hours for the downtime')                    

    def handle(self, *args, **options):
        if len(options['site']) != 3:
            logger.error(f"Site code {options['site']} is not 3 characters. Please provide a 3 character site code")
            sys.exit(1)
        if len(options['enclosure']) != 4:
            logger.error(f"Enclosure code {options['enclosure']} is not 4 characters. Please provide a 4 character enclosure code")
            sys.exit(1)
        if len(options['telescope']) != 4:
            logger.error(f"Telescope code {options['telescope']} is not 4 characters. Please provide a 4 character telescope code")
            sys.exit(1)

        start = options['start']
        end = options['end']
        if options['offset_hours'] != 0:
            start += timedelta(hours=options['offset_hours'])
        if options['duration_hours'] != 0:
            end = start + timedelta(hours=options['duration_hours'])

        downtime = Downtime.objects.create(
            site=options['site'],
            observatory=options['enclosure'],
            telescope=options['telescope'],
            reason=options['reason'],
            start=start,
            end=end
        )
        logger.info(f"Created downtime on {options['site']}.{options['enclosure']}.{options['telescope']} at {start}")
        sys.exit(0)