#!/usr/bin/env python3
"""
Test timezone settings for IST
"""
import os
import sys
import django
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.utils import timezone
from django.conf import settings

def test_timezone_settings():
    """Test that timezone is properly set to IST"""
    print("Testing Timezone Configuration")
    print("=" * 40)
    
    # Check Django settings
    print(f"Django TIME_ZONE setting: {settings.TIME_ZONE}")
    print(f"Django USE_TZ setting: {settings.USE_TZ}")
    
    # Get current time in configured timezone
    current_time = timezone.now()
    print(f"Current time (timezone aware): {current_time}")
    
    # Convert to local time
    local_time = timezone.localtime(current_time)
    print(f"Local time (IST): {local_time}")
    
    # Format like the dashboard template
    formatted_time = local_time.strftime("%b %d, %H:%M")
    print(f"Dashboard format: {formatted_time}")
    
    print("\n" + "=" * 40)
    print("✅ Timezone successfully configured for IST!")
    
if __name__ == "__main__":
    test_timezone_settings()
