from django.core.management.base import BaseCommand
from analytics.services import UtilizationTrackingService
from datetime import datetime, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Update utilization tracking data for resources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days back to update (default: 7)'
        )
        parser.add_argument(
            '--today-only',
            action='store_true',
            help='Update only today\'s utilization data'
        )

    def handle(self, *args, **options):
        utilization_service = UtilizationTrackingService()
        
        if options['today_only']:
            # Update only today
            utilization_service.record_daily_utilization()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated utilization data for {timezone.now().date()}'
                )
            )
        else:
            # Update for the specified number of days
            days = options['days']
            today = timezone.now().date()
            
            for i in range(days):
                date = today - timedelta(days=i)
                utilization_service.record_daily_utilization(date)
                self.stdout.write(f'Updated utilization data for {date}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated utilization data for the last {days} days'
                )
            )
