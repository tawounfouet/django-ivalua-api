import csv
import os
import logging
from django.core.management.base import BaseCommand
from accounting.models.reference_data import ServiceType
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import service types from CSV file'

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
            path = os.path.join(settings.BASE_DIR, 'accounting', 'data', 'type_prestation.csv')
        
        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f'File not found: {path}'))
            return

        self.stdout.write(self.style.NOTICE(f'Importing service types from {path}'))
        
        try:
            with open(path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                
                # Clear existing data if any
                ServiceType.objects.all().delete()
                self.stdout.write(self.style.WARNING('All existing service types cleared from database.'))
                  # Import data
                count = 0
                for row in reader:
                    # Extract data from CSV
                    id_service_type = row.get('ID_SERVICE_TYPE', '').strip()
                    code = row.get('CODE', '').strip()
                    name = row.get('NAME', '').strip()
                    category_code = row.get('CATEGORY_CODE', '').strip()
                    category_name = row.get('CATEGORY_NAME', '').strip()
                    
                    if not id_service_type or not code or not name:
                        logger.warning(f"Skipping row with missing required fields: {row}")
                        continue
                    
                    # Create ServiceType object
                    ServiceType.objects.create(
                        id_service_type=id_service_type,
                        code=code,
                        name=name,
                        category_code=category_code,
                        category_name=category_name
                    )
                    count += 1
                    
                self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} service types'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing service types: {str(e)}'))
            logger.exception("Error importing service types")
