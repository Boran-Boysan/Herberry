"""
Management command to manage IP blacklist

Usage:
    python manage.py manage_blacklist --list
    python manage.py manage_blacklist --clear
    python manage.py manage_blacklist --add 192.168.1.1
    python manage.py manage_blacklist --remove 192.168.1.1
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Manage IP blacklist for security'

    def add_arguments(self, parser):
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all blacklisted IPs',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all blacklisted IPs',
        )
        parser.add_argument(
            '--add',
            type=str,
            help='Add IP to blacklist',
        )
        parser.add_argument(
            '--remove',
            type=str,
            help='Remove IP from blacklist',
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_blacklist()
        elif options['clear']:
            self.clear_blacklist()
        elif options['add']:
            self.add_to_blacklist(options['add'])
        elif options['remove']:
            self.remove_from_blacklist(options['remove'])
        else:
            self.stdout.write(
                self.style.WARNING('Please specify an action: --list, --clear, --add, or --remove')
            )

    def list_blacklist(self):
        """List all blacklisted IPs"""
        self.stdout.write(self.style.SUCCESS('📋 Blacklisted IPs:'))
        # Note: Django's cache doesn't have a built-in way to list all keys
        # For production, consider using Redis with pattern matching
        self.stdout.write('Note: Use Redis for production to enable listing all IPs')

    def clear_blacklist(self):
        """Clear all blacklisted IPs"""
        cache.clear()
        self.stdout.write(self.style.SUCCESS('✅ All blacklist entries cleared'))

    def add_to_blacklist(self, ip):
        """Add IP to blacklist"""
        blacklist_key = f'ip_blacklist:{ip}'
        cache.set(blacklist_key, True, 86400)  # 24 hours
        self.stdout.write(
            self.style.SUCCESS(f'✅ IP {ip} added to blacklist for 24 hours')
        )

    def remove_from_blacklist(self, ip):
        """Remove IP from blacklist"""
        blacklist_key = f'ip_blacklist:{ip}'
        cache.delete(blacklist_key)
        self.stdout.write(
            self.style.SUCCESS(f'✅ IP {ip} removed from blacklist')
        )