"""Create a Studio editor: a user in the "Editors" group. No self-signup —
Direction A keeps the gate closed, so Jamie provisions editors with this
command. Idempotent: safe to re-run."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError

from app.auth import EDITORS_GROUP

User = get_user_model()


class Command(BaseCommand):
    help = "Create (or update) a user and add them to the Editors group."

    def add_arguments(self, parser):
        parser.add_argument("username", help="Username for the editor account.")
        parser.add_argument("email", help="Email address for the editor account.")
        parser.add_argument(
            "--password",
            default=None,
            help="Set this password. Omit to leave the account password-unusable "
            "(set one later with: manage.py changepassword <user>).",
        )

    def handle(self, *args, **options):
        username = options["username"].strip()
        email = options["email"].strip()
        password = options["password"]
        if not username:
            raise CommandError("username must not be empty.")

        # Create the group on first run so a fresh environment just works.
        group, group_created = Group.objects.get_or_create(name=EDITORS_GROUP)
        if group_created:
            self.stdout.write(self.style.SUCCESS(f'Created group "{EDITORS_GROUP}".'))

        user, user_created = User.objects.get_or_create(
            username=username,
            defaults={"email": email},
        )
        if user_created:
            self.stdout.write(self.style.SUCCESS(f'Created user "{username}".'))
        else:
            # Keep the email in sync on re-runs; don't clobber other fields.
            if email and user.email != email:
                user.email = email
                user.save(update_fields=["email"])
            self.stdout.write(f'User "{username}" already exists.')

        if password:
            user.set_password(password)
            user.save(update_fields=["password"])
            self.stdout.write(self.style.SUCCESS("Password set."))
        elif user_created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
            self.stdout.write(self.style.WARNING(f"No password set. Set one with: manage.py changepassword {username}"))

        if group in user.groups.all():
            self.stdout.write(f'"{username}" is already in the "{EDITORS_GROUP}" group.')
        else:
            user.groups.add(group)
            self.stdout.write(self.style.SUCCESS(f'Added "{username}" to the "{EDITORS_GROUP}" group.'))
