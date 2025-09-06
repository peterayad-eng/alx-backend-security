from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from ip_tracking.models import BlockedIP
import ipaddress

class Command(BaseCommand):
    help = 'Add IP addresses to the blocklist'

    def add_arguments(self, parser):
        parser.add_argument(
            'ip_addresses',
            nargs='+',
            type=str,
            help='IP addresses to block'
        )
        parser.add_argument(
            '--reason',
            type=str,
            default='No reason provided',
            help='Reason for blocking the IP address'
        )
        parser.add_argument(
            '--created-by',
            type=str,
            default='system',
            help='Who is blocking this IP (default: system)'
        )
        parser.add_argument(
            '--inactive',
            action='store_true',
            help='Add the IP as inactive (not actually blocked)'
        )

    def handle(self, *args, **options):
        ip_addresses = options['ip_addresses']
        reason = options['reason']
        created_by = options['created_by']
        is_active = not options['inactive']

        success_count = 0
        error_count = 0

        for ip in ip_addresses:
            try:
                # Validate IP format
                ipaddress.ip_address(ip)

                # Create or update blocked IP
                blocked_ip, created = BlockedIP.objects.update_or_create(
                    ip_address=ip,
                    defaults={
                        'reason': reason,
                        'created_by': created_by,
                        'is_active': is_active
                    }
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Successfully blocked IP: {ip}')
                    )
                    success_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'🔄 Updated existing block for IP: {ip}')
                    )
                    success_count += 1

            except ValueError:
                self.stdout.write(self.style.ERROR(f"❌ Invalid IP format: {ip}"))
                error_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error blocking IP {ip}: {e}"))
                error_count += 1

        # Summary
        self.stdout.write(self.style.SUCCESS(f"\n📊 Completed: {success_count} success, {error_count} errors"))

