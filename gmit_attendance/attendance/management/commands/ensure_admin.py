import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Creates (or updates) the Admin superuser from environment variables.

    Safe to run on every deploy — if the user already exists, it does
    nothing (except make sure it's still marked as an admin/superuser).
    This lets you set your Admin login without needing Shell access,
    which isn't available on Render's free tier.

    Reads these environment variables:
        ADMIN_USERNAME  (required to actually do anything)
        ADMIN_EMAIL     (optional, defaults to admin@example.com)
        ADMIN_PASSWORD  (required to actually do anything)
    """

    help = "Creates the Admin superuser from ADMIN_USERNAME / ADMIN_EMAIL / ADMIN_PASSWORD env vars."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get('ADMIN_USERNAME')
        password = os.environ.get('ADMIN_PASSWORD')
        email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                "ADMIN_USERNAME / ADMIN_PASSWORD not set — skipping admin creation."
            ))
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email},
        )
        user.email = email
        user.role = 'ADMIN'
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created admin user '{username}'."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Admin user '{username}' already existed — password/role refreshed."))
