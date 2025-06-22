from django.core.management.base import BaseCommand
from django.db import transaction
from django.db import models
from resources.models import Resource
import pytz

class Command(BaseCommand):
    help = 'Setup timezone and location data for resources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto',
            action='store_true',
            help='Automatically assign common timezones to resources without timezone data',
        )
        parser.add_argument(
            '--list-timezones',
            action='store_true',
            help='List all available timezones',
        )
        parser.add_argument(
            '--resource',
            type=str,
            help='Resource name to update',
        )
        parser.add_argument(
            '--timezone',
            type=str,
            help='Timezone to set for the resource',
        )
        parser.add_argument(
            '--location',
            type=str,
            help='Location to set for the resource',
        )

    def handle(self, *args, **options):
        if options['list_timezones']:
            self.list_timezones()
            return

        if options['auto']:
            self.auto_setup_timezones()
            return

        if options['resource'] and options['timezone']:
            self.update_resource_timezone(
                options['resource'], 
                options['timezone'], 
                options.get('location')
            )
            return

        self.interactive_setup()

    def list_timezones(self):
        """List common timezones"""
        self.stdout.write(
            self.style.SUCCESS('Common Timezones:')
        )
        
        common_timezones = [
            ('US/Eastern', 'New York, Toronto, Miami'),
            ('US/Central', 'Chicago, Dallas, Mexico City'),
            ('US/Mountain', 'Denver, Phoenix, Salt Lake City'),
            ('US/Pacific', 'Los Angeles, San Francisco, Seattle'),
            ('Europe/London', 'London, Dublin'),
            ('Europe/Paris', 'Paris, Berlin, Madrid, Rome'),
            ('Europe/Amsterdam', 'Amsterdam, Brussels'),
            ('Asia/Tokyo', 'Tokyo, Seoul'),
            ('Asia/Shanghai', 'Beijing, Singapore, Manila'),
            ('Asia/Kolkata', 'Mumbai, Delhi, Bangalore'),
            ('Australia/Sydney', 'Sydney, Melbourne'),
            ('Australia/Perth', 'Perth'),
            ('America/Sao_Paulo', 'São Paulo, Rio de Janeiro'),
            ('UTC', 'Coordinated Universal Time'),
        ]
        
        for tz, locations in common_timezones:
            self.stdout.write(f"  {tz:<20} - {locations}")

    def auto_setup_timezones(self):
        """Automatically assign common timezones to resources"""
        self.stdout.write('Auto-setting up timezone data...')
        
        # Common timezone assignments
        auto_assignments = [
            ('US/Eastern', 'New York, USA'),
            ('US/Pacific', 'San Francisco, USA'),
            ('Europe/London', 'London, UK'),
            ('Asia/Tokyo', 'Tokyo, Japan'),
            ('Australia/Sydney', 'Sydney, Australia'),
            ('US/Central', 'Chicago, USA'),
            ('Europe/Paris', 'Paris, France'),
            ('Asia/Shanghai', 'Shanghai, China'),
        ]
        
        resources_without_tz = Resource.objects.filter(
            models.Q(timezone__isnull=True) | 
            models.Q(timezone='') | 
            models.Q(timezone='UTC')
        )
        
        updated_count = 0
        
        with transaction.atomic():
            for i, resource in enumerate(resources_without_tz):
                if i < len(auto_assignments):
                    timezone_name, location = auto_assignments[i]
                    resource.timezone = timezone_name
                    resource.location = location
                    resource.save()
                    
                    self.stdout.write(
                        f"✓ Updated {resource.name}: {timezone_name} - {location}"
                    )
                    updated_count += 1
                else:
                    # Assign UTC for remaining resources
                    resource.timezone = 'UTC'
                    resource.save()
                    self.stdout.write(
                        f"✓ Updated {resource.name}: UTC (default)"
                    )
                    updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} resources.')
        )

    def update_resource_timezone(self, resource_name, timezone_name, location=None):
        """Update a specific resource's timezone"""
        try:
            # Validate timezone
            pytz.timezone(timezone_name)
            
            resource = Resource.objects.get(name__iexact=resource_name)
            resource.timezone = timezone_name
            if location:
                resource.location = location
            resource.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Updated {resource.name}: {timezone_name}'
                    + (f' - {location}' if location else '')
                )
            )
            
        except Resource.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Resource "{resource_name}" not found.')
            )
        except pytz.exceptions.UnknownTimeZoneError:
            self.stdout.write(
                self.style.ERROR(f'Invalid timezone: {timezone_name}')
            )

    def interactive_setup(self):
        """Interactive setup for timezone data"""
        self.stdout.write(
            self.style.SUCCESS('Remote Worker Setup - Interactive Mode')
        )
        self.stdout.write('=' * 50)
        
        resources = Resource.objects.all()
        if not resources.exists():
            self.stdout.write(
                self.style.WARNING('No resources found. Create some resources first.')
            )
            return
        
        self.stdout.write(f'Found {resources.count()} resources:')
        
        for resource in resources:
            tz_info = f" ({resource.timezone})" if resource.timezone and resource.timezone != 'UTC' else ""
            loc_info = f" - {resource.location}" if resource.location else ""
            self.stdout.write(f"  • {resource.name}{tz_info}{loc_info}")
        
        self.stdout.write('\nCommands:')
        self.stdout.write('  python manage.py setup_timezones --auto')
        self.stdout.write('    (Automatically assign common timezones)')
        self.stdout.write('')
        self.stdout.write('  python manage.py setup_timezones --resource "John Doe" --timezone "US/Eastern" --location "New York, USA"')
        self.stdout.write('    (Update specific resource)')
        self.stdout.write('')
        self.stdout.write('  python manage.py setup_timezones --list-timezones')
        self.stdout.write('    (Show available timezones)')
