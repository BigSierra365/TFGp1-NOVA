from django.core.management.base import BaseCommand
from django.core.management import call_command
import os

class Command(BaseCommand):
    help = 'Create or update message files for all supported languages'

    def handle(self, *args, **options):
        # Create locale directory if it doesn't exist
        locale_dir = os.path.join(os.getcwd(), 'locale')
        if not os.path.exists(locale_dir):
            os.makedirs(locale_dir)
        
        # Create message files for each language
        languages = ['es', 'en']
        
        for lang in languages:
            self.stdout.write(f'Creating/updating message files for {lang}...')
            call_command('makemessages', '-l', lang, '--ignore=venv/*', '--no-location', '--no-obsolete')
            
        self.stdout.write(self.style.SUCCESS('Successfully created/updated message files'))
