from django.utils import timezone
from datetime import timedelta

def get_week_date_range():
    """Get the start and end dates for the current week (Monday-Sunday)."""
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

def get_month_date_range():
    """Get the start and end dates for the current month."""
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    # Find the last day of the month
    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    return start_of_month, end_of_month

def format_datetime(datetime_obj, format_str='%d %b %Y, %H:%M'):
    """Format a datetime object to a string."""
    if not datetime_obj:
        return ''
    return datetime_obj.strftime(format_str)

def calculate_date_difference(start_date, end_date):
    """Calculate the difference between two dates in days."""
    if not start_date or not end_date:
        return 0
    delta = end_date - start_date
    return delta.days

def is_past_due(date):
    """Check if a date is in the past."""
    today = timezone.now().date()
    return date < today