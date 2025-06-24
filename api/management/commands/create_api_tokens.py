"""
Management command to create API tokens for users
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Create API tokens for users'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to create token for',
        )
        parser.add_argument(
            '--all-users',
            action='store_true',
            help='Create tokens for all users',
        )
        parser.add_argument(
            '--show-existing',
            action='store_true',
            help='Show existing tokens',
        )
    
    def handle(self, *args, **options):
        if options['show_existing']:
            self.show_existing_tokens()
            return
        
        if options['all_users']:
            self.create_tokens_for_all_users()
        elif options['username']:
            self.create_token_for_user(options['username'])
        else:
            raise CommandError('Please specify --username or --all-users')
    
    def create_token_for_user(self, username):
        """Create token for a specific user"""
        try:
            user = User.objects.get(username=username)
            token, created = Token.objects.get_or_create(user=user)
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created new token for user "{username}": {token.key}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Token already exists for user "{username}": {token.key}'
                    )
                )
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist')
    
    def create_tokens_for_all_users(self):
        """Create tokens for all users"""
        users = User.objects.all()
        created_count = 0
        existing_count = 0
        
        for user in users:
            token, created = Token.objects.get_or_create(user=user)
            if created:
                created_count += 1
                self.stdout.write(
                    f'Created token for {user.username}: {token.key}'
                )
            else:
                existing_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Summary: {created_count} new tokens created, '
                f'{existing_count} tokens already existed'
            )
        )
    
    def show_existing_tokens(self):
        """Show all existing tokens"""
        tokens = Token.objects.select_related('user').all()
        
        if not tokens:
            self.stdout.write(
                self.style.WARNING('No API tokens found')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS('Existing API tokens:')
        )
        self.stdout.write('-' * 60)
        
        for token in tokens:
            self.stdout.write(
                f'{token.user.username:<20} {token.key}'
            )
        
        self.stdout.write('-' * 60)
        self.stdout.write(f'Total tokens: {tokens.count()}')
