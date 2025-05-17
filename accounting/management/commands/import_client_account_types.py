import csv
import os
import logging
from django.core.management.base import BaseCommand
from accounting.models.reference_data import ClientAccountType
from django.conf import settings
from .utils import open_csv_with_different_encodings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import client account types from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='Path to the CSV file',
            default=None
        )

    def handle(self, *args, **options):
        # Determine the path to the CSV file
        path = options.get('path')
        if not path:
            path = os.path.join(settings.BASE_DIR, 'accounting', 'data', 'type-de-compte-client.csv')
        
        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f'File not found: {path}'))
            return

        self.stdout.write(self.style.NOTICE(f'Importing client account types from {path}'))
        
        try:
            reader, file, encoding = open_csv_with_different_encodings(path)
            self.stdout.write(f"Successfully opened file with encoding: {encoding}")
            
            # Clear existing data if any
            ClientAccountType.objects.all().delete()
            self.stdout.write(self.style.WARNING('All existing client account types cleared from database.'))
              
            # Import data
            count = 0
            for row in reader:
                # Extract data from CSV
                code = row.get('CODE', '').strip()
                name = row.get('NAME', '').strip()
                
                if not code or not name:
                    logger.warning(f"Skipping row with missing required fields: {row}")
                    continue
                
                # Create ClientAccountType object
                ClientAccountType.objects.create(
                    code=code,
                    name=name
                )
                count += 1
                
            file.close()
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} client account types'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing client account types: {str(e)}'))
            logger.exception("Error importing client account types")
