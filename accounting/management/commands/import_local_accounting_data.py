import os
from django.core.management.base import BaseCommand
from accounting.management.commands.import_pcg import Command as ImportPCGCommand
from accounting.management.commands.import_fiscal_years import Command as ImportFiscalYearsCommand
from accounting.management.commands.import_journals import Command as ImportJournalsCommand
from accounting.management.commands.import_accounting_types import Command as ImportAccountingTypesCommand


class Command(BaseCommand):
    help = 'Import all accounting data from local folder'

    def handle(self, *args, **options):
        # Utiliser directement le dossier data de l'application accounting
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
        
        self.stdout.write(self.style.NOTICE(f'Utilisation du répertoire de données local: {data_dir}'))
        
        if not os.path.exists(data_dir) or not os.path.isdir(data_dir):
            self.stdout.write(self.style.ERROR(f'Le répertoire de données local n\'existe pas: {data_dir}'))
            return
        
        pcg_file = os.path.join(data_dir, 'export_comptes_pcg.csv')
        fiscal_years_file = os.path.join(data_dir, 'exercice_comptable.csv')
        journals_file = os.path.join(data_dir, 'journal_comptable.csv')
        accounting_types_file = os.path.join(data_dir, 'type-de-comptabilite.csv')        # Vérifier l'existence des fichiers
        self.stdout.write(self.style.NOTICE(f'Vérification des fichiers:'))
        self.stdout.write(f'  - PCG: {pcg_file} {"(existe)" if os.path.exists(pcg_file) else "(non existant)"}')
        self.stdout.write(f'  - Exercices: {fiscal_years_file} {"(existe)" if os.path.exists(fiscal_years_file) else "(non existant)"}')
        self.stdout.write(f'  - Journaux: {journals_file} {"(existe)" if os.path.exists(journals_file) else "(non existant)"}')
        self.stdout.write(f'  - Types: {accounting_types_file} {"(existe)" if os.path.exists(accounting_types_file) else "(non existant)"}')
        
        # Import accounting types
        if os.path.exists(accounting_types_file):
            self.stdout.write(self.style.NOTICE('Importing accounting types...'))
            cmd = ImportAccountingTypesCommand()
            cmd.handle(file_path=accounting_types_file)
        else:
            self.stdout.write(self.style.WARNING(f'File not found: {accounting_types_file}'))
        
        # Import fiscal years
        if os.path.exists(fiscal_years_file):
            self.stdout.write(self.style.NOTICE('Importing fiscal years...'))
            cmd = ImportFiscalYearsCommand()
            cmd.handle(file_path=fiscal_years_file)
        else:
            self.stdout.write(self.style.WARNING(f'File not found: {fiscal_years_file}'))
        
        # Import journals
        if os.path.exists(journals_file):
            self.stdout.write(self.style.NOTICE('Importing accounting journals...'))
            cmd = ImportJournalsCommand()
            cmd.handle(file_path=journals_file)
        else:
            self.stdout.write(self.style.WARNING(f'File not found: {journals_file}'))
        
        # Import PCG (chart of accounts)
        if os.path.exists(pcg_file):
            self.stdout.write(self.style.NOTICE('Importing chart of accounts...'))
            cmd = ImportPCGCommand()
            cmd.handle(file_path=pcg_file)
        else:
            self.stdout.write(self.style.WARNING(f'File not found: {pcg_file}'))
        
        self.stdout.write(self.style.SUCCESS('All accounting data imported successfully'))
