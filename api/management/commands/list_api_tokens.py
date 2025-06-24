from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'List all API tokens'

    def handle(self, *args, **options):
        tokens = Token.objects.all()
        
        if not tokens:
            self.stdout.write("No API tokens found.")
            return
        
        self.stdout.write(f"Found {tokens.count()} API tokens:")
        self.stdout.write("-" * 80)
        
        for token in tokens:
            user = token.user
            self.stdout.write(f"User: {user.username} ({user.email})")
            self.stdout.write(f"Token: {token.key}")
            self.stdout.write(f"Created: {token.created}")
            self.stdout.write(f"Active: {user.is_active}")
            self.stdout.write("-" * 80)
