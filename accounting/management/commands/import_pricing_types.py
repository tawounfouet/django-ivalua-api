import csv
import os
import logging
from django.core.management.base import BaseCommand
from accounting.models.reference_data import PricingType
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import pricing types from CSV file'

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
            path = os.path.join(settings.BASE_DIR, 'accounting', 'data', 'type_tarification.csv')
        
        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f'File not found: {path}'))
            return

        self.stdout.write(self.style.NOTICE(f'Importing pricing types from {path}'))
        
        try:
            with open(path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                
                # Clear existing data if any
                PricingType.objects.all().delete()
                self.stdout.write(self.style.WARNING('All existing pricing types cleared from database.'))
                  # Import data
                count = 0
                for row in reader:
                    # Extract data from CSV
                    code = row.get('CODE', '').strip()
                    name = row.get('NAME', '').strip()
                    
                    if not code or not name:
                        logger.warning(f"Skipping row with missing required fields: {row}")
                        continue
                    
                    # Create PricingType object
                    PricingType.objects.create(
                        code=code,
                        name=name
                    )
                    count += 1
                    
                self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} pricing types'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing pricing types: {str(e)}'))
            logger.exception("Error importing pricing types")
