import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from faker import Faker

from authentication.models import UserProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Génère des données utilisateurs fictives pour l\'application d\'authentification'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Nombre d\'utilisateurs à générer (défaut: 20)'
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Supprimer tous les utilisateurs existants sauf superuser avant de générer de nouvelles données'
        )
        parser.add_argument(
            '--locale',
            type=str,
            default='fr_FR',
            help='Locale à utiliser pour les données fake (défaut: fr_FR)'
        )
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Créer un superutilisateur admin@example.com (mot de passe: adminpass)'
        )
        parser.add_argument(
            '--supplier-ratio',
            type=float,
            default=0.3,
            help='Pourcentage d\'utilisateurs à marquer comme fournisseurs (défaut: 0.3 soit 30%)'
        )

    def handle(self, *args, **options):
        count = options['count']
        clean = options['clean']
        locale = options['locale']
        create_superuser = options['create_superuser']
        supplier_ratio = options['supplier_ratio']
        
        # Initialiser Faker avec la locale spécifiée
        self.fake = Faker([locale])
        
        # Nettoyer la base de données si demandé
        if clean:
            self.stdout.write(self.style.WARNING('Suppression des utilisateurs existants (sauf superusers)...'))
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Utilisateurs supprimés avec succès'))
        
        # Créer un superutilisateur si demandé
        if create_superuser:
            self.create_admin_superuser()
        
        # Générer les utilisateurs
        with transaction.atomic():
            self.stdout.write(self.style.NOTICE(f'Génération de {count} utilisateurs...'))
            users = self.generate_users(count, supplier_ratio)
            
        # Afficher un résumé
        suppliers_count = User.objects.filter(is_supplier=True).count()
        staff_count = User.objects.filter(is_staff=True).count()
        superuser_count = User.objects.filter(is_superuser=True).count()
        locked_count = sum(1 for user in User.objects.all() if user.is_locked)
        
        self.stdout.write(self.style.SUCCESS(f'Génération terminée! {len(users)} utilisateurs créés.'))
        self.stdout.write(
            f'Total utilisateurs: {User.objects.count()}, '
            f'Fournisseurs: {suppliers_count}, '
            f'Staff: {staff_count}, '
            f'Superutilisateurs: {superuser_count}, '
            f'Comptes verrouillés: {locked_count}'
        )

    def create_admin_superuser(self):
        """Créer un superutilisateur admin pour les tests."""
        email = 'admin@example.com'
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Le superutilisateur {email} existe déjà'))
            return
            
        admin = User.objects.create_superuser(
            email=email,
            password='adminpass',
            first_name='Admin',
            last_name='User',
            is_active=True
        )
        
        # Mise à jour du profil
        admin.profile.organization = 'Ivalua'
        admin.profile.city = 'Paris'
        admin.profile.country = 'France'
        admin.profile.social_linkedin = 'https://linkedin.com/in/admin-user'
        admin.profile.bio = 'Superutilisateur administrateur du système'
        admin.profile.save()
        
        self.stdout.write(self.style.SUCCESS(f'Superutilisateur créé: {email} (mot de passe: adminpass)'))

    def generate_users(self, count, supplier_ratio):
        """Générer des utilisateurs avec leurs profils."""
        users = []
        departments = ['IT', 'Finance', 'HR', 'Operations', 'Sales', 'Marketing', 'Legal', 'R&D']
        positions = ['Manager', 'Director', 'Analyst', 'Specialist', 'Coordinator', 'Assistant', 'Supervisor', 'Officer']
        organizations = ['Ivalua', 'Acme Corp', 'TechCorp', 'Global Services', 'Consulting Partners', 'Supply Solutions', 'Industrial Tech']
        
        for i in range(1, count + 1):
            # Déterminer si c'est un fournisseur
            is_supplier = random.random() < supplier_ratio
            
            # Information de base
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            email = f"{self.slugify(first_name)}.{self.slugify(last_name)}@{self.fake.domain_name()}"
            
            # S'assurer que l'email est unique
            suffix = 1
            original_email = email
            while User.objects.filter(email=email).exists():
                email = f"{original_email.split('@')[0]}{suffix}@{original_email.split('@')[1]}"
                suffix += 1
            
            # Information professionnelle
            if is_supplier:
                department = random.choice(['Ventes', 'Service client', 'Livraison', 'Production'])
                position = random.choice(['Commercial', 'Représentant', 'Directeur', 'Agent'])
                organization = self.fake.company()
            else:
                department = random.choice(departments)
                position = random.choice(positions)
                organization = random.choice(organizations)
            
            # Statut staff/admin (jamais pour les fournisseurs)
            is_staff = False if is_supplier else random.random() < 0.2
            is_superuser = False if is_supplier else (is_staff and random.random() < 0.2)
            
            # État du compte
            is_active = random.random() < 0.9  # 90% des comptes sont actifs
            
            # Créer l'utilisateur avec un mot de passe aléatoire
            user = User.objects.create_user(
                email=email,
                password=self.fake.password(length=12),
                first_name=first_name,
                last_name=last_name,
                is_supplier=is_supplier,
                is_staff=is_staff,
                is_superuser=is_superuser,
                is_active=is_active,
                department=department,
                position=position,
                phone_number=self.fake.phone_number() if random.random() < 0.7 else '',
                mobile_number=self.fake.phone_number() if random.random() < 0.5 else '',
                language=random.choice(['en', 'fr', 'es', 'de']),
                employee_id=f"EMP{str(i).zfill(5)}" if not is_supplier else ''
            )
            
            # Simuler des tentatives de connexion échouées pour certains utilisateurs
            if random.random() < 0.1:  # 10% des utilisateurs ont des tentatives échouées
                failed_attempts = random.randint(1, 7)
                user.failed_login_attempts = failed_attempts
                
                # Verrouiller le compte si plus de 5 tentatives
                if failed_attempts >= 5:
                    # Durée aléatoire de verrouillage entre 5 minutes et 2 heures
                    lock_duration = random.randint(5, 120)
                    user.account_locked_until = timezone.now() + timezone.timedelta(minutes=lock_duration)
                
                user.save()
            
            # Enregistrer une connexion pour certains utilisateurs
            if random.random() < 0.7 and not user.is_locked:  # 70% des utilisateurs déverrouillés ont une connexion récente
                user.last_login = timezone.now() - timezone.timedelta(hours=random.randint(1, 72))
                user.last_login_ip = f"192.168.1.{random.randint(1, 254)}"
                user.save()
            
            # Mise à jour du profil utilisateur
            date_of_birth = None
            if random.random() < 0.6:  # 60% des utilisateurs ont une date de naissance
                date_of_birth = self.fake.date_of_birth(minimum_age=18, maximum_age=65)
                
            user.profile.bio = self.fake.paragraph(nb_sentences=3) if random.random() < 0.4 else ''
            user.profile.date_of_birth = date_of_birth
            user.profile.address = self.fake.street_address() if random.random() < 0.5 else ''
            user.profile.city = self.fake.city() if random.random() < 0.6 else ''
            user.profile.country = self.fake.country() if random.random() < 0.7 else ''
            user.profile.organization = organization
            user.profile.social_linkedin = f"https://linkedin.com/in/{self.slugify(first_name)}-{self.slugify(last_name)}" if random.random() < 0.3 else ''
            user.profile.notification_email = random.random() < 0.8  # 80% activent les notifications email
            user.profile.notification_sms = random.random() < 0.4   # 40% activent les notifications SMS
            user.profile.save()
            
            users.append(user)
            self.stdout.write(f"  Créé utilisateur: {user.email} ({'Fournisseur' if is_supplier else 'Interne'}) - {first_name} {last_name}")
            
        return users

    def slugify(self, text):
        """Version simplifiée de slugify pour les emails et URLs."""
        text = text.lower()
        import re
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')