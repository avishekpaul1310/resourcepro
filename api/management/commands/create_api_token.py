from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Create or get API token for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to create/get token for')
        parser.add_argument(
            '--create-user',
            action='store_true',
            help='Create user if it does not exist',
        )

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"Found user: {username}")
        except User.DoesNotExist:
            if options['create_user']:
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='temppass123'
                )
                self.stdout.write(f"Created user: {username}")
            else:
                self.stderr.write(f"User '{username}' does not exist. Use --create-user to create.")
                return
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        if created:
            self.stdout.write(f"Created new token for {username}")
        else:
            self.stdout.write(f"Retrieved existing token for {username}")
        
        self.stdout.write(f"API Token: {token.key}")
        self.stdout.write(f"Authorization Header: Token {token.key}")
