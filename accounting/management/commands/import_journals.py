import os
import csv
import codecs
from django.core.management.base import BaseCommand
from django.db import transaction
from accounting.models import (
    AccountingJournal
)

class Command(BaseCommand):
    help = 'Import accounting journals from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File does not exist: {file_path}'))
            return
        
        try:
            with transaction.atomic():
                count = self._import_journals(file_path)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully imported {count} accounting journals')
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
    
    def _import_journals(self, file_path):
        """Import accounting journals from CSV file."""
        count = 0
        
        with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            
            for row in reader:
                id_journal = row.get('ID_JOURNAL_COMPTABLE', '').strip()
                code = row.get('CODE_JOURNAL_COMPTABLE', '').strip()
                
                if not id_journal or not code:
                    continue
                
                short_name = row.get('LIB_RED_JOURNAL_COMPTABLE', '').strip()
                name = row.get('LIB_JOURNAL_COMPTABLE', '').strip()
                company_code = row.get('CODE_SOCIETE', '').strip()
                
                # Check if journal is for opening balances
                is_opening_balance = False
                if code.upper() in ['RAB', 'RAN']:  # RAN = Report à Nouveau
                    is_opening_balance = True
                
                AccountingJournal.objects.update_or_create(
                    id_journal=id_journal,
                    defaults={
                        'code': code,
                        'short_name': short_name,
                        'name': name,
                        'is_opening_balance': is_opening_balance,
                        'company_code': company_code if company_code and company_code != 'N/A' else None
                    }
                )
                count += 1
        
        return count
