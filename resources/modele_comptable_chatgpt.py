from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.db.models import Max
from django.core.exceptions import ValidationError
from django.utils import timezone

# ----------------------------------
# PLAN COMPTABLE : COMPTES GÉNÉRAUX
# ----------------------------------
class GeneralLedgerAccount(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name=_("Code compte"))
    title = models.CharField(max_length=255, verbose_name=_("Intitulé compte"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description détaillée"))
    short_description = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Description courte"))

    def __str__(self):
        return f"{self.code} - {self.title}"

# -------------------
# JOURNAL / EXERCICE
# -------------------
class Journal(models.Model):
    code = models.CharField(max_length=5, unique=True, verbose_name=_("Code"))
    title = models.CharField(max_length=100, verbose_name=_("Libellé"))

    def __str__(self):
        return f"{self.code} - {self.title}"

class Exercice(models.Model):
    year = models.PositiveIntegerField(unique=True, verbose_name=_("Année"))
    start_date = models.DateField(verbose_name=_("Date début"))
    end_date = models.DateField(verbose_name=_("Date fin"))

    def __str__(self):
        return str(self.year)

    class Meta:
        ordering = ['-year']

# ---------------------
# CLASSE ABSTRAITE TIERS
# ---------------------
class TiersBase(models.Model):
    nom = models.CharField(max_length=200)
    is_actif = models.BooleanField(default=True)

    class Meta:
        abstract = True

# ------------------
# TIERS GÉNÉRIQUE
# ------------------
class Tiers(TiersBase):
    TYPE_CHOIX = [
        ('PP', 'Personne Physique'),
        ('PM', 'Personne Morale'),
    ]
    TYPE_METIER_CHOIX = [
        ('CLIENT', 'Client'),
        ('FOURNISSEUR', 'Fournisseur'),
        ('EMPLOYE', 'Employé'),
        ('BANQUE', 'Banque'),
        ('ETAT', 'État'),
        ('ASSOCIE', 'Associé'),
        ('AUTRE', 'Autre'),
    ]

    type = models.CharField(max_length=2, choices=TYPE_CHOIX)
    type_metier = models.CharField(max_length=20, choices=TYPE_METIER_CHOIX)
    identifiant_fiscal = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.nom} ({self.get_type_display()})"

    def clean(self):
        if self.type == 'PP' and hasattr(self, 'numero_siret'):
            raise ValidationError("Une personne physique ne doit pas avoir de numéro SIRET.")
        if self.type == 'PM' and not hasattr(self, 'numero_siret'):
            raise ValidationError("Une personne morale doit avoir un numéro SIRET.")

class PersonnePhysique(Tiers):
    date_naissance = models.DateField(null=True, blank=True)

class PersonneMorale(Tiers):
    numero_siret = models.CharField(max_length=50, unique=True)

class CompteAuxiliaire(models.Model):
    tiers = models.ForeignKey(TiersBase, on_delete=models.CASCADE, related_name='comptes_auxiliaires')
    code_comptable = models.CharField(max_length=20)
    intitule = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.code_comptable} - {self.intitule}"

# -----------------------------
# CONTACT & ADRESSES DES TIERS
# -----------------------------
class Contact(models.Model):
    TYPE_CONTACT_CHOIX = [
        ('EMAIL', 'Email'),
        ('TEL', 'Téléphone'),
        ('FAX', 'Fax'),
        ('WEB', 'Site web'),
        ('AUTRE', 'Autre'),
    ]
    tiers = models.ForeignKey(TiersBase, on_delete=models.CASCADE, related_name='contacts')
    type_contact = models.CharField(max_length=10, choices=TYPE_CONTACT_CHOIX)
    valeur = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.get_type_contact_display()} : {self.valeur}"

class Adresse(models.Model):
    TYPE_ADRESSE_CHOIX = [
        ('FACTURATION', 'Facturation'),
        ('LIVRAISON', 'Livraison'),
        ('SIEGE', 'Siège social'),
        ('AUTRE', 'Autre'),
    ]
    tiers = models.ForeignKey(TiersBase, on_delete=models.CASCADE, related_name='adresses')
    type_adresse = models.CharField(max_length=20, choices=TYPE_ADRESSE_CHOIX)
    rue = models.CharField(max_length=255)
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=20)
    pays = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.rue}, {self.code_postal} {self.ville} ({self.get_type_adresse_display()})"

# -----------------------------
# ECRITURE COMPTABLE & LIGNES
# -----------------------------
class EcritureComptable(models.Model):
    STATUS_CHOICES = [
        ('brouillon', "Brouillon"),
        ('valide', "Validé"),
        ('archive', "Archivé"),
    ]

    journal = models.ForeignKey(Journal, on_delete=models.PROTECT)
    exercice = models.ForeignKey(Exercice, on_delete=models.PROTECT)
    date_ecriture = models.DateField()
    reference = models.CharField(max_length=20, unique=True, blank=True, null=True)
    libelle = models.CharField(max_length=255)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='brouillon')
    commentaire = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_ecriture', 'reference']

    def __str__(self):
        return f"{self.reference} - {self.date_ecriture} - {self.libelle}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()
        super().save(*args, **kwargs)

    def generate_reference(self):
        base_ref = f"{self.journal.code}/{self.exercice.year}"
        last_ref = EcritureComptable.objects.filter(
            journal=self.journal, exercice=self.exercice, reference__startswith=base_ref
        ).aggregate(max_ref=Max('reference'))['max_ref']

        if last_ref:
            try:
                last_seq = int(last_ref.split('/')[-1])
            except Exception:
                last_seq = 0
            next_seq = last_seq + 1
        else:
            next_seq = 1

        return f"{base_ref}/{next_seq:05d}"

    @property
    def total_debit(self):
        return sum(line.debit for line in self.lines.all())

    @property
    def total_credit(self):
        return sum(line.credit for line in self.lines.all())

    def is_balanced(self):
        return self.total_debit == self.total_credit

    def clean(self):
        if self.statut == 'valide' and not self.is_balanced():
            raise ValidationError("L'écriture comptable doit être équilibrée (débit = crédit).")

class LigneEcriture(models.Model):
    ecriture = models.ForeignKey(EcritureComptable, on_delete=models.CASCADE, related_name='lines')
    compte = models.ForeignKey(GeneralLedgerAccount, on_delete=models.PROTECT)
    libelle = models.CharField(max_length=255)
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tiers = models.ForeignKey(Tiers, null=True, blank=True, on_delete=models.SET_NULL)
    lettrage = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        sens = "D" if self.debit > 0 else "C"
        montant = self.debit if self.debit > 0 else self.credit
        return f"{self.compte.code} | {sens} {montant}"
