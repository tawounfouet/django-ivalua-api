import os
import csv
import codecs
from django.core.management.base import BaseCommand
from django.db import transaction
from accounting.models import (
    AccountingClass,
    AccountingChapter,
    AccountingSection,
    GeneralLedgerAccount
)
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Import accounting chart data from PCG CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File does not exist: {file_path}'))
            return
        
        try:
            with transaction.atomic():
                # Create default classes, chapters, and sections first
                self._create_chart_structure()
                
                # Then import accounts
                count = self._import_accounts(file_path)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully imported {count} general ledger accounts')
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
    
    def _create_chart_structure(self):
        """Create the basic structure of accounting classes, chapters and sections."""
        
        # Define accounting classes (1-9)
        classes = [
            {'code': '1', 'name': 'Comptes de capitaux'},
            {'code': '2', 'name': 'Comptes d\'immobilisations'},
            {'code': '3', 'name': 'Comptes de stocks et en-cours'},
            {'code': '4', 'name': 'Comptes de tiers'},
            {'code': '5', 'name': 'Comptes financiers'},
            {'code': '6', 'name': 'Comptes de charges'},
            {'code': '7', 'name': 'Comptes de produits'},
            {'code': '8', 'name': 'Comptes spéciaux'},
            {'code': '9', 'name': 'Comptabilité analytique'},
        ]
        
        for class_data in classes:
            AccountingClass.objects.get_or_create(
                code=class_data['code'],
                defaults={'name': class_data['name']}
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created accounting classes'))
      def _import_accounts(self, file_path):
        """Import general ledger accounts from CSV file."""
        count = 0
        
        # Try different encodings, preferring latin1 which is common for French CSV files
        encodings_to_try = ['latin1', 'cp1252', 'iso-8859-1', 'utf-8-sig', 'utf-8']
        
        for encoding in encodings_to_try:
            try:
                self.stdout.write(f"Trying with encoding: {encoding}")
                with codecs.open(file_path, 'r', encoding=encoding) as csvfile:
                    reader = csv.DictReader(csvfile, delimiter=';')
                    
                    for row in reader:
                account_number = row.get('NO_CPT_COMPTABLE_GENERAL', '').strip()
                if not account_number:
                    continue
                
                # Extract class, chapter, and section codes
                class_code = account_number[0] if len(account_number) > 0 else None
                chapter_code = account_number[:2] if len(account_number) > 1 else None
                section_code = account_number[:3] if len(account_number) > 2 else None
                
                # Get or create accounting class
                if class_code:
                    accounting_class, _ = AccountingClass.objects.get_or_create(
                        code=class_code
                    )
                else:
                    continue  # Skip if no class code
                
                # Get or create accounting chapter
                if chapter_code:
                    chapter_name = row.get('LIB_CHAPITRE_COMPTABLE', '').strip()
                    if chapter_name:
                        accounting_chapter, _ = AccountingChapter.objects.get_or_create(
                            code=chapter_code,
                            defaults={
                                'name': chapter_name,
                                'accounting_class': accounting_class
                            }
                        )
                    else:
                        accounting_chapter, _ = AccountingChapter.objects.get_or_create(
                            code=chapter_code,
                            accounting_class=accounting_class
                        )
                else:
                    accounting_chapter = None
                
                # Get or create accounting section
                if section_code and accounting_chapter:
                    section_name = row.get('LIB_SECTION_COMPTABLE', '').strip()
                    if section_name:
                        accounting_section, _ = AccountingSection.objects.get_or_create(
                            code=section_code,
                            defaults={
                                'name': section_name,
                                'chapter': accounting_chapter
                            }
                        )
                    else:
                        accounting_section, _ = AccountingSection.objects.get_or_create(
                            code=section_code,
                            chapter=accounting_chapter
                        )
                else:
                    accounting_section = None
                
                # Create general ledger account
                short_name = row.get('LIB_RED_CPT_COMPTABLE_GENERAL', '').strip()
                full_name = row.get('LIB_CPT_COMPTABLE_GENERAL', '').strip()
                
                # Determine if account is balance sheet or income statement
                is_balance_sheet = True  # Default to balance sheet
                indic_bilan_resultat = row.get('INDIC_BILAN_RESULTAT', '').strip()
                if indic_bilan_resultat == 'RESULTAT' or class_code in ['6', '7']:
                    is_balance_sheet = False
                
                budget_account_code = row.get('CODE_CPT_BUDG_THEO', '').strip()
                recovery_status = row.get('STATUT_RECUP_CPT', '').strip()
                financial_statement_group = row.get('CODE_REGRP_ETATS_FINANC_CPT', '').strip()
                
                # Create or update account
                GeneralLedgerAccount.objects.update_or_create(
                    account_number=account_number,
                    defaults={
                        'short_name': short_name or full_name[:50],
                        'full_name': full_name or short_name,
                        'section': accounting_section,
                        'is_balance_sheet': is_balance_sheet,
                        'budget_account_code': budget_account_code or None,
                        'recovery_status': recovery_status or None,
                        'financial_statement_group': financial_statement_group or None
                    }
                )
                count += 1
                
                if count % 1000 == 0:
                    self.stdout.write(f'Imported {count} accounts so far...')
        
        return count
