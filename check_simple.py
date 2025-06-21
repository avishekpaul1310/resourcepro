import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from resources.models import Resource, ResourceAvailability
from accounts.models import User

print("=== Resources Check ===")
all_resources = Resource.objects.all()
print(f"Total resources: {all_resources.count()}")

resources_with_users = Resource.objects.filter(user__isnull=False)
print(f"Resources with users: {resources_with_users.count()}")

for resource in resources_with_users:
    print(f"- {resource.name} (User: {resource.user.username})")

print("\n=== Availability Records ===")
availability_records = ResourceAvailability.objects.all()
print(f"Total availability records: {availability_records.count()}")

for record in availability_records[:5]:  # Show first 5
    resource_name = record.resource.name if record.resource else "No resource"
    print(f"- {resource_name}: {record.start_date} to {record.end_date} ({record.availability_type})")

print("\n=== Users Check ===")
users = User.objects.all()
print(f"Total users: {users.count()}")
for user in users:
    print(f"- {user.username} ({user.first_name} {user.last_name})")
