import os
import csv
import codecs
from django.core.management.base import BaseCommand
from django.db import transaction
from accounting.models import (
    FiscalYear
)
from django.utils.text import slugify
from datetime import datetime, date

class Command(BaseCommand):
    help = 'Import fiscal years from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File does not exist: {file_path}'))
            return
        
        try:
            with transaction.atomic():
                count = self._import_fiscal_years(file_path)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully imported {count} fiscal years')
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
    
    def _import_fiscal_years(self, file_path):
        """Import fiscal years from CSV file."""
        count = 0
        current_year = datetime.now().year
        
        with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            
            for row in reader:
                year_str = row.get('NO_EXERCICE', '').strip()
                if not year_str or not year_str.isdigit():
                    continue
                
                year = int(year_str)
                name = row.get('LIB_EXERCICE_', '').strip() or f'EXERCICE {year}'
                
                # Set start and end dates (typically January 1 to December 31)
                start_date = date(year, 1, 1)
                end_date = date(year, 12, 31)
                
                # Check if this is the current year
                is_current = (year == current_year)
                
                # Assume years before current are closed
                is_closed = (year < current_year)
                
                FiscalYear.objects.update_or_create(
                    year=year,
                    defaults={
                        'name': name,
                        'start_date': start_date,
                        'end_date': end_date,
                        'is_current': is_current,
                        'is_closed': is_closed
                    }
                )
                count += 1
        
        return count
