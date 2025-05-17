import os
import shutil
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Copy data files from project root data directory to accounting app data directory'

    def handle(self, *args, **options):
        # Chemin vers le dossier data au niveau du projet
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        project_data_dir = os.path.join(project_root, 'data')
        
        # Chemin vers le dossier data de l'application accounting
        accounting_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
        
        self.stdout.write(self.style.NOTICE(f'Recherche des données dans: {project_data_dir}'))
        self.stdout.write(self.style.NOTICE(f'Destination des données: {accounting_data_dir}'))
        
        # Vérifier si les dossiers existent
        if not os.path.exists(project_data_dir) or not os.path.isdir(project_data_dir):
            self.stdout.write(self.style.ERROR(f'Le dossier data du projet n\'existe pas: {project_data_dir}'))
            return
        
        # Créer le dossier de destination s'il n'existe pas
        os.makedirs(accounting_data_dir, exist_ok=True)
        
        files_to_copy = [
            'exercice_comptable.csv',
            'export_comptes_pcg.csv',
            'journal_comptable.csv',
            'type-de-comptabilite.csv'
        ]
        
        for filename in files_to_copy:
            src_path = os.path.join(project_data_dir, filename)
            dst_path = os.path.join(accounting_data_dir, filename)
            
            if os.path.exists(src_path):
                try:
                    shutil.copy2(src_path, dst_path)
                    self.stdout.write(self.style.SUCCESS(f'Fichier copié: {filename}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Erreur lors de la copie de {filename}: {str(e)}'))
            else:
                self.stdout.write(self.style.WARNING(f'Fichier non trouvé: {src_path}'))
        
        self.stdout.write(self.style.SUCCESS('Copie des fichiers terminée.'))
        self.stdout.write(self.style.NOTICE('Vous pouvez maintenant exécuter la commande "python manage.py import_local_accounting_data" pour importer les données.'))
