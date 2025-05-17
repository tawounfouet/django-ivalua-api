import os
import csv
import codecs
from django.core.management.base import BaseCommand
from django.db import transaction
from accounting.models import (
    AccountingType
)

class Command(BaseCommand):
    help = 'Import accounting types from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File does not exist: {file_path}'))
            return
        
        try:
            with transaction.atomic():
                count = self._import_accounting_types(file_path)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully imported {count} accounting types')
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
    
    def _import_accounting_types(self, file_path):
        """Import accounting types from CSV file."""
        count = 0
        
        with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            
            for row in reader:
                code = row.get('CODE_TYPE_COMPTABILITE', '').strip()
                
                if not code or code == '???':
                    continue
                
                short_name = row.get('LIB_RED_DU_TYPE_COMPTABILITE', '').strip()
                full_name = row.get('LIB_TYPE_COMPTABILITE', '').strip()
                nature = row.get('NATURE_DE_COMPTABILITE', '').strip()
                
                if short_name == 'NULL':
                    short_name = code
                
                if full_name == 'NULL':
                    full_name = short_name or code
                
                AccountingType.objects.update_or_create(
                    code=code,
                    defaults={
                        'short_name': short_name,
                        'full_name': full_name,
                        'nature': nature if nature and nature != 'NULL' else None
                    }
                )
                count += 1
        
        return count
