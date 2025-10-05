import os
import re
from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key


class Command(BaseCommand):
    help = 'Generate a Django secret key and write it to the .env file if SECRET_KEY is empty'

    def handle(self, *args, **options):
        # Generate a new secret key
        new_key = get_random_secret_key()

        # Path to .env file
        env_path = '.env'

        if os.path.exists(env_path):
            # Read the current .env file
            with open(env_path, 'r') as f:
                content = f.read()

            # Check if SECRET_KEY is empty or not defined
            if 'SECRET_KEY=' not in content:
                # Add SECRET_KEY if it doesn't exist
                with open(env_path, 'a') as f:
                    f.write(f'\nSECRET_KEY={new_key}\n')
                self.stdout.write(self.style.SUCCESS(f'Added SECRET_KEY={new_key} to .env file'))
            else:
                # If SECRET_KEY exists but is empty
                pattern = r'SECRET_KEY=([^\n]*)'
                match = re.search(pattern, content)
                if match and not match.group(1).strip():
                    # Replace empty SECRET_KEY with new key
                    new_content = re.sub(pattern, f'SECRET_KEY={new_key}', content)
                    with open(env_path, 'w') as f:
                        f.write(new_content)
                    self.stdout.write(self.style.SUCCESS(f'Updated SECRET_KEY={new_key} in .env file'))
                else:
                    # SECRET_KEY already has a value
                    self.stdout.write(self.style.WARNING('SECRET_KEY already exists in .env file. No changes made.'))
                    self.stdout.write(f'For reference, generated key: {new_key}')
        else:
            # Create .env file with SECRET_KEY if it doesn't exist
            with open(env_path, 'w') as f:
                f.write(f'SECRET_KEY={new_key}\n')
            self.stdout.write(self.style.SUCCESS(f'Created .env file with SECRET_KEY={new_key}'))
