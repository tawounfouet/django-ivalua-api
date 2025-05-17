import csv
import os
import logging
from django.core.management.base import BaseCommand
from accounting.models.reference_data import Municipality
from django.conf import settings
from django.db import transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import municipalities from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the CSV file'
        )

    def handle(self, *args, **options):
        # Get the path to the CSV file
        path = options['file_path']
        
        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f'File not found: {path}'))
            return

        self.stdout.write(self.style.NOTICE(f'Importing municipalities from {path}'))
        
        # Try different encodings until one works
        encodings_to_try = ['latin1', 'cp1252', 'iso-8859-1', 'utf-8-sig', 'utf-8']
        
        for encoding in encodings_to_try:
            try:
                self.stdout.write(f"Trying with encoding: {encoding}")
                
                # Use transaction to ensure atomicity
                with transaction.atomic():
                    # Batch import to handle "too many SQL variables" error
                    self._import_municipalities_with_batching(path, encoding)
                
                self.stdout.write(self.style.SUCCESS(f'Successfully imported municipalities using {encoding} encoding'))
                return  # Exit the function if successful
                
            except UnicodeDecodeError as e:
                self.stdout.write(self.style.WARNING(f'Encoding {encoding} failed: {str(e)}'))
                continue  # Try the next encoding
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error importing municipalities: {str(e)}'))
                logger.exception("Error importing municipalities")
                return  # Exit the function on other errors
        
        # If we get here, all encodings failed
        self.stdout.write(self.style.ERROR(f'Failed to import municipalities with any of the tried encodings'))

    def _import_municipalities_with_batching(self, path, encoding, batch_size=500):
        """Import municipalities with batching to avoid SQLite limitations."""
        # Clear existing data if any
        Municipality.objects.all().delete()
        self.stdout.write(self.style.WARNING('All existing municipalities cleared from database.'))
        
        count = 0
        batch = []
        
        with open(path, mode='r', encoding=encoding) as file:
            reader = csv.DictReader(file, delimiter=';')
            
            for row in reader:
                # Extract data from CSV
                insee_code = row.get('CODE_COMMUNE_INSEE', '').strip()
                name = row.get('LIB_COMMUNE_INSEE', '').strip()
                postal_code = row.get('CODE_POSTAL', '').strip()
                department_code = row.get('CODE_DEPT_COMMUNE_INSEE', '').strip()
                region_code = row.get('INDIC_EPCI', '').strip()
                
                if not insee_code or not name:
                    logger.warning(f"Skipping row with missing required fields: {row}")
                    continue
                
                # Create Municipality object (but don't save yet)
                municipality = Municipality(
                    insee_code=insee_code,
                    name=name,
                    postal_code=postal_code,
                    department_code=department_code,
                    region_code=region_code
                )
                
                batch.append(municipality)
                count += 1
                
                # Save in batches to avoid SQLite limitations
                if len(batch) >= batch_size:
                    Municipality.objects.bulk_create(batch)
                    self.stdout.write(f"Imported {count} municipalities so far...")
                    batch = []
            
            # Save any remaining municipalities
            if batch:
                Municipality.objects.bulk_create(batch)
                
        self.stdout.write(f"Total municipalities imported: {count}")
