from django import template
from django.utils import timezone
import pytz

register = template.Library()

@register.filter
def format_local_time(resource):
    """Format the current local time for a resource"""
    if not resource.timezone:
        return timezone.now().strftime("%I:%M %p")
    
    try:
        tz = pytz.timezone(resource.timezone)
        local_time = timezone.now().astimezone(tz)
        return local_time.strftime("%I:%M %p")
    except pytz.exceptions.UnknownTimeZoneError:
        return timezone.now().strftime("%I:%M %p")

@register.filter
def is_business_hours(resource):
    """Check if it's business hours for a resource"""
    if not resource.timezone:
        return True
    
    try:
        tz = pytz.timezone(resource.timezone)
        local_time = timezone.now().astimezone(tz)
        hour = local_time.hour
        is_weekday = local_time.weekday() < 5
        return is_weekday and 9 <= hour < 17
    except pytz.exceptions.UnknownTimeZoneError:
        return True

@register.inclusion_tag('resources/timezone_overlap.html')
def show_timezone_overlap(resources):
    """Show timezone overlap visualization for a list of resources"""
    if not resources or len(resources) < 2:
        return {'overlap_hours': [], 'resources': resources}
    
    # Get overlap hours for the team
    overlap_hours = []
    
    # Check each UTC hour to see if all resources are in business hours
    for utc_hour in range(24):
        all_in_business_hours = True
        
        for resource in resources:
            if not resource.timezone:
                continue
                
            try:
                tz = pytz.timezone(resource.timezone)
                # Create a datetime for this UTC hour today
                utc_time = timezone.now().replace(hour=utc_hour, minute=0, second=0, microsecond=0)
                local_time = utc_time.astimezone(tz)
                
                # Check if it's business hours (9 AM - 5 PM) and weekday
                local_hour = local_time.hour
                is_weekday = local_time.weekday() < 5
                
                if not (is_weekday and 9 <= local_hour < 17):
                    all_in_business_hours = False
                    break
            except pytz.exceptions.UnknownTimeZoneError:
                continue
                
        if all_in_business_hours and len([r for r in resources if r.timezone]) > 1:
            overlap_hours.append(utc_hour)
    
    return {
        'overlap_hours': overlap_hours,
        'resources': resources,
        'overlap_count': len(overlap_hours)
    }

@register.simple_tag
def format_utc_hour_for_resource(utc_hour, resource):
    """Format a UTC hour as local time for a specific resource"""
    if not resource.timezone:
        return f"{utc_hour:02d}:00"
    
    try:
        tz = pytz.timezone(resource.timezone)
        utc_time = timezone.now().replace(hour=utc_hour, minute=0, second=0, microsecond=0)
        local_time = utc_time.astimezone(tz)
        return local_time.strftime("%I:%M %p")
    except pytz.exceptions.UnknownTimeZoneError:
        return f"{utc_hour:02d}:00"
