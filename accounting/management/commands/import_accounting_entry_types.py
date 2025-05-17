import csv
import os
import logging
from django.core.management.base import BaseCommand
from accounting.models.reference_data import AccountingEntryType
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import accounting entry types from CSV file'

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
            path = os.path.join(settings.BASE_DIR, 'accounting', 'data', 'type_d_ecrirture_comptable.csv')
        
        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f'File not found: {path}'))
            return

        self.stdout.write(self.style.NOTICE(f'Importing accounting entry types from {path}'))
        
        try:
            with open(path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                
                # Clear existing data if any
                AccountingEntryType.objects.all().delete()
                self.stdout.write(self.style.WARNING('All existing accounting entry types cleared from database.'))
                  # Import data
                count = 0
                for row in reader:
                    # Extract data from CSV
                    code = row.get('CODE', '').strip()
                    name = row.get('NAME', '').strip()
                    indicator_code = row.get('INDICATOR_CODE', '').strip()
                    indicator_name = row.get('INDICATOR_NAME', '').strip()
                    
                    if not code or not name:
                        logger.warning(f"Skipping row with missing required fields: {row}")
                        continue
                    
                    # Create AccountingEntryType object
                    AccountingEntryType.objects.create(
                        code=code,
                        name=name,
                        indicator_code=indicator_code,
                        indicator_name=indicator_name
                    )
                    count += 1
                    
                self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} accounting entry types'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing accounting entry types: {str(e)}'))
            logger.exception("Error importing accounting entry types")
