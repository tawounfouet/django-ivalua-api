from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampedModel(models.Model):
    """Modèle abstrait avec champs de date de création et de modification"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseIvaluaModel(TimestampedModel):
    """Modèle de base pour toutes les entités Ivalua"""
    object_id = models.IntegerField(null=True, blank=True, help_text="ID Ivalua de l'objet")
    status = models.CharField(max_length=10, choices=[
        ('val', 'Validé'),
        ('del', 'Supprimé'),
        ('ini', 'Initial'),
        ('end', 'Terminé'),
    ], default='val')
    
    # Dates provenant de l'API Ivalua
    creation_date = models.DateField(null=True, blank=True, help_text="Date de création dans Ivalua")
    modification_date = models.DateField(null=True, blank=True, help_text="Date de modification dans Ivalua")
    deleted_date = models.DateField(null=True, blank=True, help_text="Date de suppression dans Ivalua")
    latest_modification_date = models.DateField(null=True, blank=True, help_text="Date de dernière modification dans Ivalua")
    
    # Métadonnées de création et modification
    login_created = models.CharField(max_length=100, blank=True, null=True)
    login_modified = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        abstract = True


# Modèles Organisation
class Organization(BaseIvaluaModel):
    """Modèle pour les organisations"""
    orga_node = models.CharField(max_length=50, help_text="Identifiant du nœud organisationnel")
    orga_level = models.CharField(max_length=20, help_text="Niveau d'organisation")
    orga_label = models.CharField(max_length=200, help_text="Libellé de l'organisation")
    orga_id = models.IntegerField(help_text="ID de l'organisation dans Ivalua")
    
    class Meta:
        verbose_name = "Organisation"
        verbose_name_plural = "Organisations"
        unique_together = ('orga_node', 'orga_level')
        indexes = [
            models.Index(fields=['orga_node']),
            models.Index(fields=['orga_level']),
        ]
    
    def __str__(self):
        return f"{self.orga_label} ({self.orga_node})"


# Modèles Famille
class Commodity(BaseIvaluaModel):
    """Modèle pour les familles d'achats"""
    fam_node = models.CharField(max_length=50, help_text="Identifiant du nœud famille")
    fam_level = models.CharField(max_length=20, help_text="Niveau famille")
    fam_label = models.CharField(max_length=200, help_text="Libellé de la famille")
    fam_id = models.IntegerField(help_text="ID de la famille dans Ivalua")
    code = models.CharField(max_length=50, blank=True, null=True, help_text="Code famille SEQENS")
    
    class Meta:
        verbose_name = "Famille d'achat"
        verbose_name_plural = "Familles d'achat"
        unique_together = ('fam_node', 'fam_level')
        indexes = [
            models.Index(fields=['fam_node']),
            models.Index(fields=['fam_level']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.fam_label} ({self.code or self.fam_node})"


# Modèles Utilisateur
class User(BaseIvaluaModel):
    """Modèle pour les utilisateurs"""
    matricule = models.CharField(max_length=50, blank=True, null=True, help_text="Matricule de l'utilisateur")
    first_name = models.CharField(max_length=100, help_text="Prénom de l'utilisateur")
    last_name = models.CharField(max_length=100, help_text="Nom de famille de l'utilisateur")
    email = models.EmailField(help_text="Adresse email de l'utilisateur")
    login = models.CharField(max_length=100, unique=True, help_text="Nom de connexion de l'utilisateur")
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Téléphone professionnel")
    home_phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Téléphone personnel")
    cell_number = models.CharField(max_length=20, blank=True, null=True, help_text="Téléphone portable")
    language = models.CharField(max_length=10, default="fr", help_text="Langue du compte utilisateur")
    last_connexion_date = models.DateField(null=True, blank=True, help_text="Date de dernière connexion")
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        indexes = [
            models.Index(fields=['login']),
            models.Index(fields=['matricule']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.login})"


class UserProfile(models.Model):
    """Modèle pour les profils des utilisateurs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles')
    profil_code = models.CharField(max_length=50, help_text="Code du profil")
    profil_label = models.CharField(max_length=200, help_text="Libellé du profil")
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateur"
        unique_together = ('user', 'profil_code')
    
    def __str__(self):
        return f"{self.profil_label} ({self.user.login})"


class UserOrganization(models.Model):
    """Modèle pour les rattachements organisationnels des utilisateurs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organizations')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='users')
    status = models.CharField(max_length=10, choices=[
        ('val', 'Validé'),
        ('del', 'Supprimé'),
    ], default='val')
    
    class Meta:
        verbose_name = "Rattachement organisationnel"
        verbose_name_plural = "Rattachements organisationnels"
        unique_together = ('user', 'organization')
    
    def __str__(self):
        return f"{self.user.login} - {self.organization.orga_label}"


class UserFamily(models.Model):
    """Modèle pour les rattachements famille des utilisateurs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='families')
    family = models.ForeignKey(Commodity, on_delete=models.CASCADE, related_name='users')
    status = models.CharField(max_length=10, choices=[
        ('val', 'Validé'),
        ('del', 'Supprimé'),
    ], default='val')
    
    class Meta:
        verbose_name = "Rattachement famille"
        verbose_name_plural = "Rattachements famille"
        unique_together = ('user', 'family')
    
    def __str__(self):
        return f"{self.user.login} - {self.family.fam_label}"


# Modèles Fournisseur
class Supplier(BaseIvaluaModel):
    """Modèle pour les fournisseurs"""
    code = models.CharField(max_length=50, unique=True, help_text="Code interne Ivalua du fournisseur")
    erp_code = models.CharField(max_length=50, blank=True, null=True, help_text="Code externe IKOS du fournisseur")
    supplier_name = models.CharField(max_length=200, help_text="Nom du fournisseur")
    physical_person = models.BooleanField(default=False, help_text="Indique si le fournisseur est une personne physique")
    title = models.CharField(max_length=10, blank=True, null=True, help_text="Titre (renseigné uniquement si personne physique)")
    first_name = models.CharField(max_length=100, blank=True, null=True, help_text="Prénom (renseigné uniquement si personne physique)")
    last_name = models.CharField(max_length=100, blank=True, null=True, help_text="Nom (renseigné uniquement si personne physique)")
    legal_name = models.CharField(max_length=200, help_text="Dénomination sociale")
    website = models.URLField(blank=True, null=True, help_text="Site web du fournisseur")
    
    # Identifiants nationaux
    nat_id_type = models.CharField(max_length=2, choices=[
        ('01', 'SIRET'),
        ('05', 'TVA'),
        ('06', 'HORS UE'),
        ('07', 'TAHITI'),
        ('08', 'RIDET'),
        ('09', 'FOURNISSEUR FRANÇAIS SANS SIRET'),
        ('10', 'FRWF'),
        ('11', 'IREP'),
    ], blank=True, null=True, help_text="Type d'identifiant national")
    nat_id = models.CharField(max_length=50, blank=True, null=True, help_text="Identifiant national")
    
    # Type de tiers IKOS
    type_ikos_tiers_code = models.CharField(max_length=3, choices=[
        ('FRS', 'Fournisseur'),
        ('IBE', 'Syndicat de copropriété SEQENS'),
        ('SYN', 'Syndicat de copropriété'),
    ], blank=True, null=True, help_text="Code du type de tiers IKOS")
    type_ikos_tiers_label = models.CharField(max_length=100, blank=True, null=True, help_text="Libellé du type de tiers IKOS")
    
    # Détails d'identité
    siret = models.CharField(max_length=14, blank=True, null=True, help_text="Numéro SIRET")
    siren = models.CharField(max_length=9, blank=True, null=True, help_text="Numéro SIREN")
    duns = models.CharField(max_length=9, blank=True, null=True, help_text="Numéro DUNS")
    tva_intracom = models.CharField(max_length=50, blank=True, null=True, help_text="TVA intracommunautaire")
    ape_naf = models.CharField(max_length=10, blank=True, null=True, help_text="Code APE/NAF")
    creation_year = models.CharField(max_length=4, blank=True, null=True, help_text="Année de création")
    
    # Dates système
    creation_system_date = models.DateField(null=True, blank=True, help_text="Date de création dans le système")
    modification_system_date = models.DateField(null=True, blank=True, help_text="Date de modification dans le système")
    deleted_system_date = models.DateField(null=True, blank=True, help_text="Date de suppression dans le système")
    
    # Structure légale
    legal_code = models.CharField(max_length=50, blank=True, null=True, help_text="Code légal")
    legal_structure = models.CharField(max_length=100, blank=True, null=True, help_text="Structure légale")
    
    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['erp_code']),
            models.Index(fields=['siret']),
            models.Index(fields=['siren']),
            models.Index(fields=['nat_id']),
        ]
    
    def __str__(self):
        return f"{self.supplier_name} ({self.code})"


class SupplierAddress(models.Model):
    """Modèle pour les adresses des fournisseurs"""
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE, related_name='address')
    adr1 = models.CharField(max_length=200, blank=True, null=True, help_text="Pays")
    adr2 = models.CharField(max_length=200, blank=True, null=True, help_text="Adresse ligne 1")
    adr3 = models.CharField(max_length=200, blank=True, null=True, help_text="Adresse ligne 2")
    zip = models.CharField(max_length=20, blank=True, null=True, help_text="Code postal")
    city = models.CharField(max_length=100, blank=True, null=True, help_text="Ville")
    
    class Meta:
        verbose_name = "Adresse fournisseur"
        verbose_name_plural = "Adresses fournisseurs"
    
    def __str__(self):
        return f"Adresse de {self.supplier.supplier_name}"


class BankingInformation(models.Model):
    """Modèle pour les informations bancaires des fournisseurs"""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='banking_informations')
    international_pay_id = models.CharField(max_length=20, blank=True, null=True, help_text="Identifiant international de paiement")
    account_number = models.CharField(max_length=50, blank=True, null=True, help_text="Numéro de compte")
    bank_code = models.CharField(max_length=20, blank=True, null=True, help_text="Code banque")
    counter_code = models.CharField(max_length=20, blank=True, null=True, help_text="Code guichet")
    rib_key = models.CharField(max_length=10, blank=True, null=True, help_text="Clé RIB")
    bban = models.CharField(max_length=50, blank=True, null=True, help_text="BBAN (Basic Bank Account Number)")
    iban = models.CharField(max_length=34, help_text="IBAN (International Bank Account Number)")
    bic = models.CharField(max_length=11, blank=True, null=True, help_text="BIC (Bank Identifier Code)")
    country_code = models.CharField(max_length=2, help_text="Code pays de la banque")
    bank_label = models.CharField(max_length=200, help_text="Libellé de la banque")
    creation_account_date = models.DateField(null=True, blank=True, help_text="Date de création de l'information bancaire")
    modification_account_date = models.DateField(null=True, blank=True, help_text="Date de dernière modification")
    
    class Meta:
        verbose_name = "Information bancaire"
        verbose_name_plural = "Informations bancaires"
    
    def __str__(self):
        return f"IBAN: {self.iban[:6]}... - {self.supplier.supplier_name}"


class SupplierContact(models.Model):
    """Modèle pour les contacts des fournisseurs"""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='contacts')
    internal = models.BooleanField(default=False, help_text="Indique si le contact est interne (1) ou externe (0)")
    first_name = models.CharField(max_length=100, help_text="Prénom du contact")
    last_name = models.CharField(max_length=100, help_text="Nom du contact")
    email = models.EmailField(help_text="Email du contact")
    login = models.CharField(max_length=100, blank=True, null=True, help_text="Login du contact")
    
    class Meta:
        verbose_name = "Contact fournisseur"
        verbose_name_plural = "Contacts fournisseurs"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.supplier.supplier_name}"


class SupplierContactProfile(models.Model):
    """Modèle pour les profils des contacts fournisseurs"""
    contact = models.ForeignKey(SupplierContact, on_delete=models.CASCADE, related_name='profiles')
    code = models.CharField(max_length=50, help_text="Code du profil")
    label = models.CharField(max_length=200, help_text="Libellé du profil")
    
    class Meta:
        verbose_name = "Profil contact fournisseur"
        verbose_name_plural = "Profils contacts fournisseurs"
    
    def __str__(self):
        return f"{self.label} - {self.contact.last_name}"


class SupplierPartner(models.Model):
    """Modèle pour les rattachements organisationnels des fournisseurs"""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='partners')
    orga_level = models.CharField(max_length=20, help_text="Niveau d'organisation")
    orga_node = models.CharField(max_length=50, help_text="Code du nœud organisationnel")
    num_part = models.IntegerField(help_text="Nombre de rattachements")
    status = models.CharField(max_length=10, choices=[
        ('val', 'Validé'),
        ('del', 'Supprimé'),
    ], default='val')
    
    class Meta:
        verbose_name = "Rattachement organisationnel fournisseur"
        verbose_name_plural = "Rattachements organisationnels fournisseurs"
        unique_together = ('supplier', 'orga_level', 'orga_node')
    
    def __str__(self):
        return f"{self.supplier.supplier_name} - {self.orga_node}"


class SupplierRole(models.Model):
    """Modèle pour les rôles des fournisseurs"""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='roles')
    orga_level = models.CharField(max_length=20, help_text="Niveau d'organisation")
    orga_node = models.CharField(max_length=50, help_text="Identifiant du nœud d'organisation")
    role_code = models.CharField(max_length=50, help_text="Code du rôle")
    role_label = models.CharField(max_length=200, blank=True, null=True, help_text="Libellé du rôle")
    begin_date = models.DateField(null=True, blank=True, help_text="Date de début du rôle")
    end_date = models.DateField(null=True, blank=True, help_text="Date de fin du rôle")
    status = models.CharField(max_length=10, choices=[
        ('val', 'Validé'),
        ('del', 'Supprimé'),
    ], default='val')
    
    class Meta:
        verbose_name = "Rôle fournisseur"
        verbose_name_plural = "Rôles fournisseurs"
    
    def __str__(self):
        return f"{self.role_label or self.role_code} - {self.supplier.supplier_name}"


# Modèles Contrat
class Contract(BaseIvaluaModel):
    """Modèle pour les contrats"""
    ctr_id_origin = models.IntegerField(null=True, blank=True, help_text="Identifiant du contrat d'origine")
    ctr_code = models.CharField(max_length=50, unique=True, help_text="Code unique du contrat")
    ctr_id_frame = models.CharField(max_length=50, blank=True, null=True, help_text="Identifiant du contrat-cadre associé")
    ctr_id_parent = models.CharField(max_length=50, blank=True, null=True, help_text="Identifiant du contrat parent")
    ctr_label = models.CharField(max_length=200, help_text="Libellé du contrat")
    ctr_ref = models.CharField(max_length=100, blank=True, null=True, help_text="Référence interne du contrat")
    
    # Type de contrat
    ctr_type = models.CharField(max_length=20, choices=[
        ('das', 'Système d\'acquisition dynamique'),
        ('master_mix', 'Accord cadre avec marché subséquent ou mixte'),
        ('master_po', 'Accord-cadre à bons de commande'),
        ('master_res', 'Accord-cadre à marchés subséquents'),
        ('res', 'Marché subséquent'),
        ('spe', 'Marché spécifique'),
        ('umbrella', 'Marché Chapeau'),
        ('work', 'Contrat Marché de travaux'),
    ], help_text="Type du contrat")
    
    # Type de procédure
    type_procedure_code = models.CharField(max_length=10, choices=[
        ('AOO', 'Appel d\'offres ouvert'),
        ('AR', 'Appel d\'offres restreint'),
        ('AU', 'Autre'),
        ('CO', 'Concours'),
        ('DC', 'Dialogue compétitif'),
        ('GAG', 'Gré à Gré'),
        ('MAPA', 'Marché à procédure adaptée'),
        ('PCN', 'Procédure concurrentielle avec négociation'),
        ('PN', 'Procédure négociée'),
        ('SAD', 'Système d\'acquisition dynamique'),
    ], blank=True, null=True, help_text="Code du type de procédure")
    type_procedure_label = models.CharField(max_length=100, blank=True, null=True, help_text="Libellé du type de procédure")
    
    # Catégorie de contrat
    contract_category_code = models.CharField(max_length=10, choices=[
        ('bpu', 'BPU Frais généraux'),
        ('exp', 'Exploitation'),
        ('fe', 'Fluides / Énergie'),
        ('trav', 'Travaux'),
    ], blank=True, null=True, help_text="Code de catégorie de contrat")
    contract_category_label = models.CharField(max_length=100, blank=True, null=True, help_text="Libellé de la catégorie de contrat")
    
    # Fournisseur
    ctr_sup_id = models.CharField(max_length=50, blank=True, null=True, help_text="Identifiant du fournisseur")
    ctr_sup_code = models.CharField(max_length=50, blank=True, null=True, help_text="Code fournisseur interne")
    ctr_sup_name = models.CharField(max_length=200, blank=True, null=True, help_text="Nom du fournisseur")
    ctr_sup_nat_id = models.CharField(max_length=50, blank=True, null=True, help_text="Identifiant national du fournisseur")
    ctr_sup_nat_id_type = models.CharField(max_length=50, blank=True, null=True, help_text="Type d'identifiant national")
    
    # Informations bancaires
    iban = models.CharField(max_length=34, blank=True, null=True, help_text="IBAN du fournisseur")
    
    # Type de groupement
    grouping_type_code = models.CharField(max_length=2, choices=[
        ('GC', 'Groupement conjoint'),
        ('GS', 'Groupement solidaire'),
        ('NG', 'Aucun groupement'),
    ], blank=True, null=True, help_text="Code du type de regroupement")
    grouping_type = models.CharField(max_length=100, blank=True, null=True, help_text="Libellé du type de regroupement")
    
    # Type de paiement
    payment_type_code = models.CharField(max_length=3, choices=[
        ('BAO', 'Billet à ordre'),
        ('CB', 'Carte Bleue'),
        ('CHQ', 'Chèque'),
        ('CRE', 'Crédit'),
        ('LIQ', 'Liquide'),
        ('TA', 'Traite acceptée'),
        ('VIR', 'Virement bancaire'),
    ], blank=True, null=True, help_text="Code du type de paiement")
    payment_type = models.CharField(max_length=100, blank=True, null=True, help_text="Type de paiement")
    
    # Informations complémentaires
    num_ao = models.CharField(max_length=50, blank=True, null=True, help_text="Numéro de l'appel d'offre lié")
    buyer_sign = models.CharField(max_length=200, blank=True, null=True, help_text="Nom de l'acheteur signataire du contrat")
    
    # Famille principale
    fam_id = models.IntegerField(null=True, blank=True, help_text="ID Famille")
    fam_code = models.CharField(max_length=50, blank=True, null=True, help_text="Code famille SEQENS")
    fam_label = models.CharField(max_length=200, blank=True, null=True, help_text="Libellé de la famille")
    fam_level = models.CharField(max_length=20, blank=True, null=True, help_text="Niveau de famille")
    fam_node = models.IntegerField(null=True, blank=True, help_text="Identifiant du noeud de famille")
    
    # Organisation principale
    orga_id = models.IntegerField(null=True, blank=True, help_text="ID Organisation")
    orga_label = models.CharField(max_length=200, blank=True, null=True, help_text="Libellé de l'organisation")
    orga_level = models.CharField(max_length=20, blank=True, null=True, help_text="Niveau organisationnel")
    orga_node = models.CharField(max_length=50, blank=True, null=True, help_text="Identifiant du nœud organisationnel")
    
    # Caractéristiques
    ctr_lang = models.CharField(max_length=50, blank=True, null=True, help_text="Langue du contrat")
    ctr_confidential = models.CharField(max_length=3, choices=[
        ('Yes', 'Oui'),
        ('No', 'Non'),
    ], blank=True, null=True, help_text="Indique si le contrat est confidentiel")
    ctr_bpm_id = models.CharField(max_length=50, blank=True, null=True, help_text="ID associé à la consultation")
    ctr_risk_required = models.CharField(max_length=3, choices=[
        ('Yes', 'Oui'),
        ('No', 'Non'),
    ], blank=True, null=True, help_text="Indique si une analyse de risques est requise")
    
    # Statut
    status_code = models.CharField(max_length=10, blank=True, null=True, help_text="Code de statut du contrat")
    status_label = models.CharField(max_length=100, blank=True, null=True, help_text="Libellé du statut")
    
    # Renouvellement
    renewal_type_code = models.CharField(max_length=20, blank=True, null=True, help_text="Code du type de renouvellement")
    renewal_type = models.CharField(max_length=100, blank=True, null=True, help_text="Type de renouvellement")
    renewal_period = models.CharField(max_length=10, blank=True, null=True, help_text="Durée du renouvellement (mois)")
    renegociation_date = models.DateField(null=True, blank=True, help_text="Date d'étude de renouvellement")
    renegociation_period = models.CharField(max_length=10, blank=True, null=True, help_text="Durée d'étude de renouvellement (mois)")
    notification_date = models.DateField(null=True, blank=True, help_text="Date de notification")
    notification_period = models.CharField(max_length=10, blank=True, null=True, help_text="Période de préavis (mois)")
    max_renewal = models.CharField(max_length=10, blank=True, null=True, help_text="Nombre maximal de renouvellements")
    duration = models.CharField(max_length=10, blank=True, null=True, help_text="Durée initiale du contrat (mois)")
    
    # Validité
    ctr_validity_code = models.CharField(max_length=10, blank=True, null=True, help_text="Code de validité du contrat")
    ctr_validity = models.CharField(max_length=100, blank=True, null=True, help_text="Statut de validité du contrat")
    notify_date = models.DateField(null=True, blank=True, help_text="Date de notification automatique")
    signature_date = models.DateField(null=True, blank=True, help_text="Date de signature")
    effective_date = models.DateField(null=True, blank=True, help_text="Date début")
    duration_ferm = models.CharField(max_length=10, blank=True, null=True, help_text="Durée ferme (mois)")
    without_end_date = models.CharField(max_length=3, choices=[
        ('Yes', 'Oui'),
        ('No', 'Non'),
    ], blank=True, null=True, help_text="Contrat sans date de fin")
    original_end_date = models.DateField(null=True, blank=True, help_text="Date de fin initiale")
    updated_end_date = models.DateField(null=True, blank=True, help_text="Date de fin réactualisée")
    date_ferm = models.DateField(null=True, blank=True, help_text="Date de fin ferme")
    
    # Résiliation
    termination = models.CharField(max_length=3, choices=[
        ('Yes', 'Oui'),
        ('No', 'Non'),
    ], blank=True, null=True, help_text="Contrat résilié ou non")
    termination_date = models.DateField(null=True, blank=True, help_text="Date de résiliation")
    termination_comment = models.TextField(blank=True, null=True, help_text="Commentaire de résiliation")
    
    # Conditions financières
    pay_term_code = models.CharField(max_length=10, blank=True, null=True, help_text="Code de conditions de paiement")
    pay_term = models.CharField(max_length=100, blank=True, null=True, help_text="Conditions de paiement")
    amount = models.DecimalField(max_digits=28, decimal_places=10, null=True, blank=True, help_text="Montant global")
    amount_entry = models.DecimalField(max_digits=28, decimal_places=10, null=True, blank=True, help_text="Montant du contrat HT")
    tva = models.CharField(max_length=100, blank=True, null=True, help_text="Information TVA")
    unit = models.CharField(max_length=3, blank=True, null=True, help_text="Unité monétaire")
    
    # Clauses contractuelles
    jurisdiction = models.TextField(blank=True, null=True, help_text="Juridiction applicable")
    penalty = models.TextField(blank=True, null=True, help_text="Clause pénale")
    payment = models.TextField(blank=True, null=True, help_text="Modalités de paiement")
    price_conditions = models.TextField(blank=True, null=True, help_text="Conditions tarifaires")
    seuil_renego = models.TextField(blank=True, null=True, help_text="Seuils de renégociation")
    invoice_conditions = models.TextField(blank=True, null=True, help_text="Conditions de facturation")
    delivery = models.TextField(blank=True, null=True, help_text="Conditions de livraison")
    garantie_conditions = models.TextField(blank=True, null=True, help_text="Conditions de garantie")
    complaint_procedure = models.TextField(blank=True, null=True, help_text="Procédure de réclamation")
    return_procedure = models.TextField(blank=True, null=True, help_text="Procédure de retour")
    choice_criteria = models.TextField(blank=True, null=True, help_text="Critères de choix")
    
    # Dates calculées
    begin_date_payment = models.DateField(null=True, blank=True, help_text="Début de période de paiement")
    calculated_end_date = models.DateField(null=True, blank=True, help_text="Date de fin calculée")
    days_to_expire = models.IntegerField(null=True, blank=True, help_text="Nombre de jours restants avant expiration")
    
    # Champs additionnels de la classe de base remplacés par les dates spécifiques au contrat
    created = models.DateField(null=True, blank=True, help_text="Date de création du contrat")
    modified = models.DateField(null=True, blank=True, help_text="Date de modification du contrat")
    
    class Meta:
        verbose_name = "Contrat"
        verbose_name_plural = "Contrats"
        indexes = [
            models.Index(fields=['ctr_code']),
            models.Index(fields=['ctr_ref']),
            models.Index(fields=['ctr_sup_code']),
            models.Index(fields=['effective_date']),
            models.Index(fields=['original_end_date']),
        ]
    
    def __str__(self):
        return f"{self.ctr_label} ({self.ctr_code})"


class ContractContact(models.Model):
    """Modèle pour les contacts associés aux contrats"""
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='contract_contacts')
    first_name = models.CharField(max_length=100, help_text="Prénom du contact")
    last_name = models.CharField(max_length=100, help_text="Nom du contact")
    email = models.EmailField(help_text="Email du contact")
    profil_label = models.CharField(max_length=200, blank=True, null=True, help_text="Libellé du profil")
    login = models.CharField(max_length=100, help_text="Login du contact")
    
    class Meta:
        verbose_name = "Contact contrat"
        verbose_name_plural = "Contacts contrat"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.contract.ctr_code}"


class ContractOrganization(models.Model):
    """Modèle pour les organisations associées aux contrats"""
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='contract_orgas')
    orga_label = models.CharField(max_length=200, blank=True, null=True, help_text="Libellé de l'organisation")
    orga_level = models.CharField(max_length=20, help_text="Niveau organisationnel")
    orga_node = models.CharField(max_length=50, help_text="Identifiant du nœud organisationnel")
    
    class Meta:
        verbose_name = "Organisation contrat"
        verbose_name_plural = "Organisations contrat"
        unique_together = ('contract', 'orga_level', 'orga_node')
    
    def __str__(self):
        return f"{self.orga_label or self.orga_node} - {self.contract.ctr_code}"


class ContractFamily(models.Model):
    """Modèle pour les familles associées aux contrats"""
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='contract_family')
    fam_label = models.CharField(max_length=200, blank=True, null=True, help_text="Libellé de la famille")
    fam_level = models.CharField(max_length=20, help_text="Niveau de famille")
    fam_node = models.CharField(max_length=50, help_text="Identifiant du noeud de famille")
    
    class Meta:
        verbose_name = "Famille contrat"
        verbose_name_plural = "Familles contrat"
        unique_together = ('contract', 'fam_level', 'fam_node')
    
    def __str__(self):
        return f"{self.fam_label or self.fam_node} - {self.contract.ctr_code}"


class ContractPatrimoine(models.Model):
    """Modèle pour les patrimoines associés aux contrats"""
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='patrimoines')
    pat_level = models.CharField(max_length=20, help_text="Niveau de patrimoine")
    pat_node = models.CharField(max_length=50, help_text="Identifiant du noeud de patrimoine")
    
    class Meta:
        verbose_name = "Patrimoine contrat"
        verbose_name_plural = "Patrimoines contrat"
        unique_together = ('contract', 'pat_level', 'pat_node')
    
    def __str__(self):
        return f"{self.pat_node} - {self.contract.ctr_code}"


class ContractProgramme(models.Model):
    """Modèle pour les programmes associés aux contrats"""
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='programmes')
    prog_level = models.CharField(max_length=20, help_text="Niveau de programme")
    prog_node = models.CharField(max_length=50, help_text="Identifiant du noeud de programme")
    
    class Meta:
        verbose_name = "Programme contrat"
        verbose_name_plural = "Programmes contrat"
        unique_together = ('contract', 'prog_level', 'prog_node')
    
    def __str__(self):
        return f"{self.prog_node} - {self.contract.ctr_code}"


class ContractOperation(models.Model):
    """Modèle pour les opérations associées aux contrats"""
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='operations')
    oper_code = models.CharField(max_length=50, help_text="Code de l'opération")
    oper_label = models.CharField(max_length=200, blank=True, null=True, help_text="Libellé de l'opération")
    
    class Meta:
        verbose_name = "Opération contrat"
        verbose_name_plural = "Opérations contrat"
    
    def __str__(self):
        return f"{self.oper_label or self.oper_code} - {self.contract.ctr_code}"


class ContractPot(models.Model):
    """Modèle pour les pots associés aux contrats"""
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='pot')
    pot_code = models.CharField(max_length=50, help_text="Code du pot")
    pot_label = models.CharField(max_length=200, blank=True, null=True, help_text="Libellé du pot")
    
    class Meta:
        verbose_name = "Pot contrat"
        verbose_name_plural = "Pots contrat"
    
    def __str__(self):
        return f"{self.pot_label or self.pot_code} - {self.contract.ctr_code}"


# Modèles Commande
class Order(BaseIvaluaModel):
    """Modèle pour les commandes"""
    ord_id_origin = models.IntegerField(null=True, blank=True, help_text="Identifiant de la commande d'origine")
    order_code = models.CharField(max_length=50, unique=True, help_text="Code de la commande (ex: PO000001)")
    order_label = models.CharField(max_length=200, help_text="Libellé de la commande")
    ord_type_code = models.CharField(max_length=50, blank=True, null=True, help_text="Code du type de commande")
    ord_ext_code = models.CharField(max_length=50, blank=True, null=True, help_text="Code externe de la commande")
    ord_ref = models.CharField(max_length=100, blank=True, null=True, help_text="Référence de la commande")
    basket_id = models.IntegerField(null=True, blank=True, help_text="Identifiant du panier")
    
    # Fournisseur
    order_sup_id = models.IntegerField(null=True, blank=True, help_text="Identifiant du fournisseur")
    order_sup_name = models.CharField(max_length=200, blank=True, null=True, help_text="Nom du fournisseur")
    sup_nat_id = models.CharField(max_length=50, blank=True, null=True, help_text="Identifiant national du fournisseur")
    sup_nat_id_type = models.CharField(max_length=50, blank=True, null=True, help_text="Type d'identifiant national")
    
    # Dates et statut
    created = models.DateField(null=True, blank=True, help_text="Date de création de la commande")
    modified = models.DateField(null=True, blank=True, help_text="Date de modification de la commande")
    status_code = models.CharField(max_length=10, blank=True, null=True, help_text="Code de statut de la commande")
    status_label = models.CharField(max_length=100, blank=True, null=True, help_text="Libellé du statut")
    ord_order_date = models.DateField(null=True, blank=True, help_text="Date de la commande")
    
    # Informations financières
    oitems_total_amount = models.DecimalField(max_digits=28, decimal_places=10, null=True, blank=True, help_text="Montant total des items de la commande")
    unit_code_currency = models.CharField(max_length=3, blank=True, null=True, help_text="Code de la devise (ex: EUR)")
    
    # Caractéristiques
    ord_comment = models.TextField(blank=True, null=True, help_text="Commentaire sur la commande")
    inco_code = models.CharField(max_length=50, blank=True, null=True, help_text="Code d'incoterm")
    ord_inco_place = models.CharField(max_length=200, blank=True, null=True, help_text="Lieu d'incoterm")
    payterm_code = models.CharField(max_length=10, blank=True, null=True, help_text="Code des conditions de paiement")
    payterm_label = models.CharField(max_length=100, blank=True, null=True, help_text="Libellé des conditions de paiement")
    payment_type_code = models.CharField(max_length=10, blank=True, null=True, help_text="Code du type de paiement")
    payment_type_label = models.CharField(max_length=100, blank=True, null=True, help_text="Libellé du type de paiement")
    
    # Options
    ord_free_budget = models.CharField(max_length=3, choices=[
        ('Yes', 'Oui'),
        ('No', 'Non'),
    ], blank=True, null=True, help_text="Indique si la commande est hors budget")
    ord_amendment_num = models.CharField(max_length=10, blank=True, null=True, help_text="Numéro d'amendement")
    ord_track_time_sheet = models.CharField(max_length=10, blank=True, null=True, help_text="Suivi des feuilles de temps")
    
    # Entité légale
    legal_comp_code = models.CharField(max_length=10, blank=True, null=True, help_text="Code de l'entité légale")
    legal_comp_legal_form = models.CharField(max_length=100, blank=True, null=True, help_text="Forme juridique de l'entité légale")
    legal_comp_label = models.CharField(max_length=200, blank=True, null=True, help_text="Libellé de l'entité légale")
    
    # Organisation
    orga_level = models.CharField(max_length=20, blank=True, null=True, help_text="Niveau organisationnel")
    orga_node = models.CharField(max_length=50, blank=True, null=True, help_text="Identifiant du nœud organisationnel")
    orga_label = models.CharField(max_length=200, blank=True, null=True, help_text="Libellé de l'organisation")
    
    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        indexes = [
            models.Index(fields=['order_code']),
            models.Index(fields=['ord_ref']),
            models.Index(fields=['order_sup_id']),
            models.Index(fields=['ord_order_date']),
        ]
    
    def __str__(self):
        return f"{self.order_label} ({self.order_code})"


class OrderContact(models.Model):
    """Modèle pour les contacts associés aux commandes"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_contacts')
    
    # Contact demandeur
    contact_requester_firstname = models.CharField(max_length=100, blank=True, null=True, help_text="Prénom du demandeur")
    contact_requester_lastname = models.CharField(max_length=100, blank=True, null=True, help_text="Nom du demandeur")
    contact_requester_email = models.EmailField(blank=True, null=True, help_text="Email du demandeur")
    
    # Contact facturation
    contact_billing_firstname = models.CharField(max_length=100, blank=True, null=True, help_text="Prénom du contact facturation")
    contact_billing_lastname = models.CharField(max_length=100, blank=True, null=True, help_text="Nom du contact facturation")
    contact_billing_email = models.EmailField(blank=True, null=True, help_text="Email du contact facturation")
    
    # Contact livraison
    contact_delivery_firstname = models.CharField(max_length=100, blank=True, null=True, help_text="Prénom du contact livraison")
    contact_delivery_lastname = models.CharField(max_length=100, blank=True, null=True, help_text="Nom du contact livraison")
    contact_delivery_email = models.EmailField(blank=True, null=True, help_text="Email du contact livraison")
    
    # Contact fournisseur
    contact_supplier_firstname = models.CharField(max_length=100, blank=True, null=True, help_text="Prénom du contact fournisseur")
    contact_supplier_lastname = models.CharField(max_length=100, blank=True, null=True, help_text="Nom du contact fournisseur")
    contact_supplier_email = models.EmailField(blank=True, null=True, help_text="Email du contact fournisseur")
    
    class Meta:
        verbose_name = "Contact commande"
        verbose_name_plural = "Contacts commande"
    
    def __str__(self):
        return f"Contacts - {self.order.order_code}"


class OrderItem(models.Model):
    """Modèle pour les items de commandes"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    oitem_id = models.IntegerField(help_text="Identifiant de l'item")
    oitem_label = models.CharField(max_length=200, help_text="Libellé de l'item")
    
    # Famille
    oitem_fam_label = models.CharField(max_length=200, blank=True, null=True, help_text="Libellé de la famille")
    oitem_fam_node = models.CharField(max_length=50, blank=True, null=True, help_text="Identifiant du noeud famille")
    oitem_fam_level = models.CharField(max_length=20, blank=True, null=True, help_text="Niveau famille")
    
    # Quantité et montant
    oitem_quantity = models.DecimalField(max_digits=28, decimal_places=10, help_text="Quantité")
    oitem_total_amount = models.DecimalField(max_digits=28, decimal_places=10, help_text="Montant total")
    
    class Meta:
        verbose_name = "Item commande"
        verbose_name_plural = "Items commande"
    
    def __str__(self):
        return f"{self.oitem_label} - {self.order.order_code}"


class OrderAddress(models.Model):
    """Modèle pour les adresses associées aux commandes"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='addresses')
    type = models.CharField(max_length=20, choices=[
        ('billing', 'Facturation'),
        ('delivery', 'Livraison'),
    ], help_text="Type d'adresse")
    
    # Détails adresse
    adr_num = models.CharField(max_length=20, blank=True, null=True, help_text="Numéro d'adresse")
    adr_nom_complt = models.CharField(max_length=200, blank=True, null=True, help_text="Complément de nom")
    adr_voie = models.CharField(max_length=200, blank=True, null=True, help_text="Voie")
    adr_voie_complt = models.CharField(max_length=200, blank=True, null=True, help_text="Complément de voie")
    zip_code = models.CharField(max_length=20, blank=True, null=True, help_text="Code postal")
    zip_label = models.CharField(max_length=100, blank=True, null=True, help_text="Ville")
    country_code = models.CharField(max_length=2, blank=True, null=True, help_text="Code pays")
    country_label = models.CharField(max_length=100, blank=True, null=True, help_text="Libellé pays")
    
    class Meta:
        verbose_name = "Adresse commande"
        verbose_name_plural = "Adresses commande"
        unique_together = ('order', 'type')
    
    def __str__(self):
        return f"{self.type.capitalize()} - {self.order.order_code}"


# Modèles Facture
class Invoice(BaseIvaluaModel):
    """Modèle pour les factures"""
    invoice_type = models.CharField(max_length=3, choices=[
        ('CRE', 'Avoir'),
        ('INV', 'Facture'),
    ], help_text="Type de facture")
    invoice_ref = models.CharField(max_length=100, unique=True, help_text="Référence de la facture")
    invoice_linked_code = models.CharField(max_length=100, blank=True, null=True, help_text="Code lié à la facture")
    invoice_date = models.DateField(help_text="Date de la facture")
    invoice_due_date = models.DateField(help_text="Date d'échéance de la facture")
    
    # Informations financières
    invoice_unit_code_currency = models.CharField(max_length=3, help_text="Code de la devise")
    invoice_amount_ht = models.DecimalField(max_digits=28, decimal_places=10, help_text="Montant hors taxes")
    invoice_amount_ttc = models.DecimalField(max_digits=28, decimal_places=10, help_text="Montant toutes taxes comprises")
    
    # Relations
    sup_id = models.IntegerField(help_text="Identifiant du fournisseur")
    sup_nat_id = models.CharField(max_length=50, blank=True, null=True, help_text="Identifiant national du fournisseur")
    ctr_id = models.IntegerField(null=True, blank=True, help_text="Identifiant du contrat")
    ctr_code = models.CharField(max_length=50, blank=True, null=True, help_text="Code du contrat")
    order_id = models.IntegerField(null=True, blank=True, help_text="Identifiant de la commande")
    order_code = models.CharField(max_length=50, blank=True, null=True, help_text="Code de la commande")
    
    # Organisation
    orga_level = models.CharField(max_length=20, help_text="Niveau organisationnel")
    orga_node = models.CharField(max_length=50, help_text="Identifiant du nœud organisationnel")
    
    # Entité légale
    legal_comp_code = models.CharField(max_length=3, choices=[
        ('V90', 'Seqens'),
        ('SES', 'Seqens Solidarités'),
        ('ADL', 'Adlis'),
        ('BRE', 'Brénu'),
        ('ART', 'Réserve des arts'),
        ('CHA', 'SCCV Saint Charles'),
        ('SEA', 'Seqens Accessions'),
        ('LOG', 'Logétude'),
        ('ONV', 'Opérateur National de Vente'),
        ('SEM', 'Semine'),
    ], blank=True, null=True, help_text="Code de la société légale")
    
    # Dates spécifiques
    invoice_creation = models.BigIntegerField(null=True, blank=True, help_text="Timestamp de création en millisecondes")
    invoice_modification = models.BigIntegerField(null=True, blank=True, help_text="Timestamp de modification en millisecondes")
    
    # Import
    imp_id = models.IntegerField(null=True, blank=True, help_text="ID de l'import")
    invoice_code = models.CharField(max_length=50, blank=True, null=True, help_text="Code généré de la facture (ex: INV000006)")
    invoice_id = models.IntegerField(null=True, blank=True, help_text="ID généré de la facture")
    
    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        indexes = [
            models.Index(fields=['invoice_ref']),
            models.Index(fields=['invoice_date']),
            models.Index(fields=['sup_id']),
            models.Index(fields=['ctr_code']),
            models.Index(fields=['order_code']),
        ]
    
    def __str__(self):
        return f"{self.invoice_ref} ({self.get_invoice_type_display()})"


class InvoiceItem(models.Model):
    """Modèle pour les items de facture"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    label = models.CharField(max_length=200, help_text="Libellé de l'item")
    amount = models.DecimalField(max_digits=28, decimal_places=10, help_text="Montant")
    tva_code = models.CharField(max_length=50, blank=True, null=True, help_text="Code TVA")
    unit_code_currency = models.CharField(max_length=3, help_text="Code de la devise")
    quantity = models.DecimalField(max_digits=28, decimal_places=10, help_text="Quantité")
    unit_code = models.CharField(max_length=10, blank=True, null=True, help_text="Code de l'unité")
    
    class Meta:
        verbose_name = "Item facture"
        verbose_name_plural = "Items facture"
    
    def __str__(self):
        return f"{self.label} - {self.invoice.invoice_ref}"


# Modèles Programme
class Program(models.Model):
    """Modèle pour les programmes"""
    code = models.CharField(max_length=50, unique=True, help_text="Code programme")
    label = models.CharField(max_length=200, help_text="Libellé du programme")
    label_complt = models.CharField(max_length=200, blank=True, null=True, help_text="Complément de libellé")
    orga_level = models.CharField(max_length=20, help_text="Niveau d'organisation")
    orga_node = models.CharField(max_length=50, help_text="Identifiant du nœud d'organisation")
    orga_label = models.CharField(max_length=200, help_text="Libellé de l'organisation")
    orga_id = models.CharField(max_length=50, help_text="ID de l'organisation")
    status = models.CharField(max_length=10, choices=[
        ('val', 'Validé'),
        ('del', 'Supprimé'),
    ], default='val')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Programme"
        verbose_name_plural = "Programmes"
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['orga_node']),
        ]
    
    def __str__(self):
        return f"{self.label} ({self.code})"