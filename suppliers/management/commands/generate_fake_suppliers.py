import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from faker import Faker

from suppliers.models import (
    Supplier, SupplierAddress, BankingInformation,
    Contact, ContactRole, SupplierPartner, SupplierRole,
    SupplierType, NationalIdType, StatusChoices
)


class Command(BaseCommand):
    help = 'Génère des données fictives pour les fournisseurs et modèles associés'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Nombre de fournisseurs à générer (défaut: 50)'
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Supprimer toutes les données existantes avant de générer de nouvelles'
        )
        parser.add_argument(
            '--locale',
            type=str,
            default='fr_FR',
            help='Locale à utiliser pour les données fake (défaut: fr_FR)'
        )

    def handle(self, *args, **options):
        count = options['count']
        clean = options['clean']
        locale = options['locale']
        
        # Initialiser Faker avec la locale spécifiée
        self.fake = Faker([locale])
        
        # Définir les constantes pour la génération de données
        self.init_constants()
        
        # Nettoyer la base de données si demandé
        if clean:
            self.stdout.write(self.style.WARNING('Suppression des données existantes...'))
            self.clean_database()
        
        # Générer les fournisseurs
        with transaction.atomic():
            self.stdout.write(self.style.NOTICE(f'Génération de {count} fournisseurs...'))
            suppliers = self.generate_suppliers(count)
            
        # Afficher un résumé
        self.stdout.write(self.style.SUCCESS(f'Génération terminée! {len(suppliers)} fournisseurs créés.'))
        self.stdout.write(
            f'Adresses: {SupplierAddress.objects.count()}, '
            f'Infos bancaires: {BankingInformation.objects.count()}, '
            f'Contacts: {Contact.objects.count()}, '
            f'Rôles de contacts: {ContactRole.objects.count()}, '
            f'Partenaires: {SupplierPartner.objects.count()}, '
            f'Rôles de fournisseurs: {SupplierRole.objects.count()}'
        )

    def init_constants(self):
        """Initialiser les constantes utilisées pour la génération de données."""
        # Fonctions pour générer des nombres aléatoires d'éléments
        self.NUM_CONTACTS_PER_SUPPLIER = lambda: random.randint(1, 5)
        self.NUM_ROLES_PER_CONTACT = lambda: random.randint(1, 3)
        self.NUM_PARTNERS_PER_SUPPLIER = lambda: random.randint(0, 3)
        self.NUM_ROLES_PER_SUPPLIER = lambda: random.randint(1, 4)
        self.NUM_BANKING_INFO_PER_SUPPLIER = lambda: random.randint(1, 3)

        # Codes et étiquettes de rôle pour les contacts
        self.ROLE_CODES = ['COM', 'TEC', 'ADM', 'FIN', 'LOG', 'DIR', 'RH', 'AUT']
        self.ROLE_LABELS = {
            'COM': 'Commercial Contact',
            'TEC': 'Technical Contact',
            'ADM': 'Administrative Contact',
            'FIN': 'Financial Contact',
            'LOG': 'Logistics Contact',
            'DIR': 'Director',
            'RH': 'HR Contact',
            'AUT': 'Other Contact'
        }
        
        # Codes pour l'organisation
        self.ORGA_LEVELS = ['DIV', 'REG', 'BU', 'DEP', 'SER']
        self.ORGA_NODES = [f"{level}{str(i).zfill(3)}" for level in self.ORGA_LEVELS for i in range(1, 6)]
        
        # Codes et étiquettes de rôle pour les fournisseurs
        self.SUPPLIER_ROLE_CODES = ['PREF', 'APPR', 'STRA', 'CONS', 'BACK', 'REST']
        self.SUPPLIER_ROLE_LABELS = {
            'PREF': 'Preferred Supplier',
            'APPR': 'Approved Supplier',
            'STRA': 'Strategic Partner',
            'CONS': 'Consultant',
            'BACK': 'Backup Supplier',
            'REST': 'Restricted Supplier'
        }
        
        # Formes juridiques
        self.LEGAL_CODES = ['SA', 'SARL', 'SAS', 'SASU', 'SC', 'SCI', 'EI', 'EIRL', 'EURL', 'LTD']
        self.LEGAL_STRUCTURES = {
            'SA': 'Société Anonyme',
            'SARL': 'Société à Responsabilité Limitée',
            'SAS': 'Société par Actions Simplifiée',
            'SASU': 'Société par Actions Simplifiée Unipersonnelle',
            'SC': 'Société Civile',
            'SCI': 'Société Civile Immobilière',
            'EI': 'Entreprise Individuelle',
            'EIRL': 'Entreprise Individuelle à Responsabilité Limitée',
            'EURL': 'Entreprise Unipersonnelle à Responsabilité Limitée',
            'LTD': 'Limited Company'
        }
        
        # Pays
        self.COUNTRY_CODES = ['FR', 'BE', 'CH', 'DE', 'GB', 'ES', 'IT']

    def clean_database(self):
        """Nettoyer la base de données avant de générer de nouvelles données."""
        SupplierRole.objects.all().delete()
        SupplierPartner.objects.all().delete()
        ContactRole.objects.all().delete()
        Contact.objects.all().delete()
        BankingInformation.objects.all().delete()
        SupplierAddress.objects.all().delete()
        Supplier.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Base de données nettoyée avec succès'))
        
    def generate_suppliers(self, count):
        """Générer des fournisseurs avec toutes les données associées."""
        suppliers = []
        
        for i in range(1, count + 1):
            # Déterminer si c'est une personne physique
            is_physical_person = random.choice([True, False])
            
            # Générer le nom du fournisseur
            if is_physical_person:
                first_name = self.fake.first_name()
                last_name = self.fake.last_name()
                supplier_name = f"{first_name} {last_name}"
                title = random.choice(['M.', 'Mme', 'Dr.'])
                legal_name = f"{first_name} {last_name} {self.fake.word().capitalize()}"
            else:
                supplier_name = self.fake.company()
                first_name = ""
                last_name = ""
                title = ""
                legal_name = f"{supplier_name} {random.choice(['International', 'France', 'Europe', 'Group', ''])}"
            
            # Générer les codes et identifiants
            object_id = 1000 + i
            code = f"SUP{str(i).zfill(6)}"
            erp_code = f"FRS{str(random.randint(1, 999)).zfill(3)}"
            type_ikos_code = random.choice([t[0] for t in SupplierType.choices])
            
            # Générer les identifiants nationaux
            nat_id_type = random.choice([t[0] for t in NationalIdType.choices])
            if nat_id_type == '01':  # SIRET
                siret = ''.join(str(random.randint(0, 9)) for _ in range(14))
                siren = siret[:9]
                nat_id = siret
            else:
                siret = ''
                siren = ''
                nat_id = ''.join(str(random.randint(0, 9)) for _ in range(random.randint(8, 15)))
            
            # Générer les autres informations
            duns = ''.join(str(random.randint(0, 9)) for _ in range(9)) if random.choice([True, False]) else ''
            tva_intracom = f"FR{''.join(str(random.randint(0, 9)) for _ in range(11))}" if random.choice([True, False]) else ''
            ape_naf = f"{str(random.randint(10, 99))}.{str(random.randint(10, 99))}{'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[random.randint(0, 25)]}" if random.choice([True, False]) else ''
            
            # Générer les dates
            creation_year = str(random.randint(1980, 2022))
            creation_system_date = self.fake.date_between(start_date='-5y', end_date='today')
            modification_system_date = self.fake.date_between(start_date=creation_system_date, end_date='today') if random.choice([True, False]) else None
            deleted_system_date = None  # Généralement, on ne génère pas de données supprimées
            latest_modification_date = modification_system_date or creation_system_date
            
            # Déterminer le statut

            """
            # Code original avec erreur:
            status = random.choices(
                [s[0] for s in StatusChoices.choices],
                weights=[70, 20, 10],  # Pondération pour favoriser les statuts valides
                k=1
            )[0]
            """
            # Code corrigé:
            # Correction:

            """
            # D'abord, vérifions le nombre d'éléments dans StatusChoices
            status_choices = [s[0] for s in StatusChoices.choices]
            if len(status_choices) == 3:  # Si nous avons bien 3 choix comme prévu
                status = random.choices(
                    status_choices,
                    weights=[70, 20, 10],  # Pour 3 choix: ini, val, arc
                    k=1
                )[0]
            else:
                # Générer des poids adaptés au nombre de choix
                # Premier élément (probablement 'val') a un poids plus élevé
                weights = [10] * len(status_choices)
                if weights:  # Assure-toi qu'il y a au moins un choix
                    weights[0] = 70  # Favorise le premier choix (souvent 'valide')
                status = random.choices(status_choices, weights=weights, k=1)[0]
            """

            """
            Pour corriger rapidement le fichier, remplacez le bloc de code problématique par celui-ci :
            """
            # Déterminer le statut
            status_choices = [s[0] for s in StatusChoices.choices]
            # Créer une liste de poids de même longueur que status_choices
            weights = [10] * len(status_choices)
            if weights:  # S'assurer qu'il y a au moins un choix
                weights[0] = 70  # Favoriser le premier choix (probablement 'valid')
            status = random.choices(status_choices, weights=weights, k=1)[0]
            
            # Générer la forme juridique
            legal_code = random.choice(self.LEGAL_CODES)
            legal_structure = self.LEGAL_STRUCTURES.get(legal_code, "")
            
            # Créer le fournisseur
            supplier = Supplier.objects.create(
                object_id=object_id,
                code=code,
                erp_code=erp_code,
                supplier_name=supplier_name,
                is_physical_person=is_physical_person,
                title=title,
                first_name=first_name,
                last_name=last_name,
                legal_name=legal_name,
                website=f"https://www.{self.slugify(supplier_name)}.com" if random.choice([True, False]) else "",
                nat_id_type=nat_id_type,
                nat_id=nat_id,
                type_ikos_code=type_ikos_code,
                siret=siret,
                siren=siren,
                duns=duns,
                tva_intracom=tva_intracom,
                ape_naf=ape_naf,
                creation_year=creation_year,
                creation_system_date=creation_system_date,
                modification_system_date=modification_system_date,
                deleted_system_date=deleted_system_date,
                latest_modification_date=latest_modification_date,
                status=status,
                legal_code=legal_code,
                legal_structure=legal_structure
            )
            
            suppliers.append(supplier)
            self.stdout.write(f"  Créé fournisseur: {supplier.code} - {supplier.supplier_name}")
            
            # Générer et associer tous les objets liés
            self.generate_supplier_address(supplier)
            self.generate_banking_information(supplier)
            self.generate_contacts(supplier)
            self.generate_supplier_partners(supplier)
            self.generate_supplier_roles(supplier)
        
        return suppliers
    
    def generate_supplier_address_v1(self, supplier):
        """Générer une adresse pour un fournisseur."""
        country_code = random.choice(self.COUNTRY_CODES)
        address = SupplierAddress.objects.create(
            supplier=supplier,
            adr1=country_code,
            adr2=self.fake.street_address(),
            adr3=self.fake.secondary_address() if random.choice([True, False]) else "",
            zip=self.fake.postcode(),
            city=self.fake.city()
        )
        self.stdout.write(f"    Ajouté adresse: {address}")
        return address
    
    def generate_supplier_address_v2(self, supplier):
        """Générer une adresse pour un fournisseur."""
        country_code = random.choice(self.COUNTRY_CODES)
        
        # Utiliser une alternative pour secondary_address qui est compatible avec toutes les locales
        # Au lieu de self.fake.secondary_address()
        secondary_address_options = [
            f"Bâtiment {random.choice('ABCDEFGH')}", 
            f"Étage {random.randint(1, 10)}", 
            f"Appartement {random.randint(1, 100)}",
            f"Boîte postale {random.randint(1000, 9999)}",
            f"ZI {self.fake.word().capitalize()}",
            f"ZA {self.fake.word().capitalize()}"
        ]
        
        address = SupplierAddress.objects.create(
            supplier=supplier,
            adr1=country_code,
            adr2=self.fake.street_address(),
            adr3=random.choice(secondary_address_options) if random.choice([True, False]) else "",
            zip=self.fake.postcode(),
            city=self.fake.city()
        )
        self.stdout.write(f"    Ajouté adresse: {address}")
        return address
    
    def generate_supplier_address(self, supplier):
        """Générer une adresse pour un fournisseur."""
        country_code = random.choice(self.COUNTRY_CODES)
        
        # Une version simplifiée, sans utiliser secondary_address
        address = SupplierAddress.objects.create(
            supplier=supplier,
            adr1=country_code,
            adr2=self.fake.street_address(),
            adr3=f"Bâtiment {random.choice('ABCDEFGH')}" if random.choice([True, False]) else "",
            zip=self.fake.postcode(),
            city=self.fake.city()
        )
        self.stdout.write(f"    Ajouté adresse: {address}")
        return address
    
    
    def generate_banking_information(self, supplier):
        """Générer des informations bancaires pour un fournisseur."""
        banking_infos = []
        num_banking_info = self.NUM_BANKING_INFO_PER_SUPPLIER()
        
        for j in range(num_banking_info):
            country_code = random.choice(self.COUNTRY_CODES)
            account_number = ''.join(str(random.randint(0, 9)) for _ in range(11))
            bank_code = str(random.randint(10000, 99999))
            counter_code = str(random.randint(10000, 99999))
            rib_key = str(random.randint(10, 99))
            bban = f"{bank_code}{counter_code}{account_number}{rib_key}"
            iban = self.generate_iban(country_code)
            bic = self.generate_bic()
            
            banking_info = BankingInformation.objects.create(
                supplier=supplier,
                international_pay_id=f"INTL{str(random.randint(1, 999)).zfill(3)}",
                account_number=account_number,
                bank_code=bank_code,
                counter_code=counter_code,
                rib_key=rib_key,
                bban=bban,
                iban=iban,
                bic=bic,
                country_code=country_code,
                bank_label=self.fake.company() + " Bank",
                creation_account_date=supplier.creation_system_date,
                modification_account_date=supplier.modification_system_date
            )
            
            banking_infos.append(banking_info)
            self.stdout.write(f"    Ajouté info bancaire: {banking_info}")
        
        return banking_infos
    
    def generate_contacts(self, supplier):
        """Générer des contacts pour un fournisseur."""
        contacts = []
        num_contacts = self.NUM_CONTACTS_PER_SUPPLIER()
        
        for j in range(num_contacts):
            is_internal = random.choice([True, False])
            contact_first_name = self.fake.first_name()
            contact_last_name = self.fake.last_name()
            
            contact = Contact.objects.create(
                supplier=supplier,
                is_internal=is_internal,
                first_name=contact_first_name,
                last_name=contact_last_name,
                email=self.fake.email(),
                login=f"{contact_first_name.lower()}.{contact_last_name.lower()}" if is_internal else ""
            )
            
            contacts.append(contact)
            self.stdout.write(f"    Ajouté contact: {contact}")
            
            # Générer les rôles pour ce contact
            self.generate_contact_roles(contact)
        
        return contacts
    
    def generate_contact_roles(self, contact):
        """Générer des rôles pour un contact."""
        roles = []
        num_roles = self.NUM_ROLES_PER_CONTACT()
        available_roles = list(self.ROLE_CODES)
        
        for _ in range(min(num_roles, len(available_roles))):
            role_code = random.choice(available_roles)
            available_roles.remove(role_code)  # Éviter les doublons
            
            contact_role = ContactRole.objects.create(
                contact=contact,
                code=role_code,
                label=self.ROLE_LABELS[role_code]
            )
            
            roles.append(contact_role)
            self.stdout.write(f"      Ajouté rôle: {contact_role}")
        
        return roles
    
    def generate_supplier_partners(self, supplier):
        """Générer des partenaires pour un fournisseur."""
        partners = []
        num_partners = self.NUM_PARTNERS_PER_SUPPLIER()
        used_nodes = set()
        
        for _ in range(num_partners):
            # Sélectionner un nœud qui n'a pas encore été utilisé pour ce fournisseur
            available_nodes = [node for node in self.ORGA_NODES if f"{supplier.id}-{node}" not in used_nodes]
            if not available_nodes:
                continue
                
            orga_node = random.choice(available_nodes)
            used_nodes.add(f"{supplier.id}-{orga_node}")
            orga_level = orga_node[:3]
            
            partner = SupplierPartner.objects.create(
                supplier=supplier,
                orga_level=orga_level,
                orga_node=orga_node,
                num_part=random.randint(1, 100),
                status=random.choice([s[0] for s in StatusChoices.choices])
            )
            
            partners.append(partner)
            self.stdout.write(f"    Ajouté partenaire: {partner}")
        
        return partners
    
    def generate_supplier_roles(self, supplier):
        """Générer des rôles pour un fournisseur."""
        roles = []
        num_roles = self.NUM_ROLES_PER_SUPPLIER()
        used_role_nodes = set()
        
        for _ in range(num_roles):
            # Sélectionner un nœud et un rôle qui n'ont pas encore été utilisés
            available_nodes = [node for node in self.ORGA_NODES if node not in used_role_nodes]
            if not available_nodes:
                continue
                
            orga_node = random.choice(available_nodes)
            orga_level = orga_node[:3]
            
            available_roles = list(self.SUPPLIER_ROLE_CODES)
            role_code = random.choice(available_roles)
            
            combo_key = f"{supplier.id}-{orga_node}-{role_code}"
            if combo_key in used_role_nodes:
                continue
                
            used_role_nodes.add(combo_key)
            
            # Définir les dates de début et de fin
            begin_date = self.fake.date_between(start_date='-3y', end_date='today')
            end_date = self.fake.date_between(start_date=begin_date, end_date='+2y') if random.choice([True, False]) else None
            
            supplier_role = SupplierRole.objects.create(
                supplier=supplier,
                orga_level=orga_level,
                orga_node=orga_node,
                role_code=role_code,
                role_label=self.SUPPLIER_ROLE_LABELS[role_code],
                begin_date=begin_date,
                end_date=end_date,
                status=random.choice([s[0] for s in StatusChoices.choices])
            )
            
            roles.append(supplier_role)
            self.stdout.write(f"    Ajouté rôle fournisseur: {supplier_role}")
        
        return roles

    def generate_iban(self, country_code='FR'):
        """Générer un IBAN pour un pays donné."""
        if country_code == 'FR':
            bank_code = str(random.randint(10000, 99999))
            counter_code = str(random.randint(10000, 99999))
            account_number = ''.join(str(random.randint(0, 9)) for _ in range(11))
            rib_key = str(random.randint(10, 99))
            bban = f"{bank_code}{counter_code}{account_number}{rib_key}"
            # Simplification pour l'exemple - ne génère pas un vrai IBAN valide
            return f"{country_code}76{bban[:30]}"
        else:
            # Format simplifié pour d'autres pays
            return f"{country_code}{''.join(str(random.randint(0, 9)) for _ in range(20))}"

    def generate_bic(self):
        """Générer un code BIC."""
        bank_code = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(4))
        country_code = random.choice(self.COUNTRY_CODES)
        location_code = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(2))
        branch_code = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(3)) if random.choice([True, False]) else ''
        return f"{bank_code}{country_code}{location_code}{branch_code}"

    def slugify(self, text):
        """Version simplifiée de slugify pour les URLs."""
        text = text.lower()
        import re
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')