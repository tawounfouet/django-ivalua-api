from django.contrib import admin
from .models import (
    Organization, Commodity, User, UserProfile, UserOrganization, UserFamily,
    Supplier, SupplierAddress, BankingInformation, SupplierContact, SupplierContactProfile,
    SupplierPartner, SupplierRole, Contract, ContractContact, ContractOrganization,
    ContractFamily, ContractPatrimoine, ContractProgramme, ContractOperation, ContractPot,
    Order, OrderContact, OrderItem, OrderAddress, Invoice, InvoiceItem, Program
)


# Inlines pour les modèles imbriqués
class UserProfileInline(admin.TabularInline):
    model = UserProfile
    extra = 0


class UserOrganizationInline(admin.TabularInline):
    model = UserOrganization
    extra = 0


class UserFamilyInline(admin.TabularInline):
    model = UserFamily
    extra = 0


class SupplierAddressInline(admin.StackedInline):
    model = SupplierAddress
    can_delete = False
    max_num = 1


class BankingInformationInline(admin.TabularInline):
    model = BankingInformation
    extra = 0


class SupplierContactInline(admin.TabularInline):
    model = SupplierContact
    extra = 0


class SupplierPartnerInline(admin.TabularInline):
    model = SupplierPartner
    extra = 0


class SupplierRoleInline(admin.TabularInline):
    model = SupplierRole
    extra = 0


class ContractContactInline(admin.TabularInline):
    model = ContractContact
    extra = 0


class ContractOrganizationInline(admin.TabularInline):
    model = ContractOrganization
    extra = 0


class ContractFamilyInline(admin.TabularInline):
    model = ContractFamily
    extra = 0


class ContractPatrimoineInline(admin.TabularInline):
    model = ContractPatrimoine
    extra = 0


class ContractProgrammeInline(admin.TabularInline):
    model = ContractProgramme
    extra = 0


class ContractOperationInline(admin.TabularInline):
    model = ContractOperation
    extra = 0


class ContractPotInline(admin.TabularInline):
    model = ContractPot
    extra = 0


class OrderContactInline(admin.StackedInline):
    model = OrderContact
    can_delete = False
    max_num = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAddressInline(admin.TabularInline):
    model = OrderAddress
    extra = 0


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0


# Définition des classes Admin
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('orga_label', 'orga_node', 'orga_level', # filepath: admin.py
from django.contrib import admin
from .models import (
    Organization, Commodity, User, UserProfile, UserOrganization, UserFamily,
    Supplier, SupplierAddress, BankingInformation, SupplierContact, SupplierContactProfile,
    SupplierPartner, SupplierRole, Contract, ContractContact, ContractOrganization,
    ContractFamily, ContractPatrimoine, ContractProgramme, ContractOperation, ContractPot,
    Order, OrderContact, OrderItem, OrderAddress, Invoice, InvoiceItem, Program
)


# Inlines pour les modèles imbriqués
class UserProfileInline(admin.TabularInline):
    model = UserProfile
    extra = 0


class UserOrganizationInline(admin.TabularInline):
    model = UserOrganization
    extra = 0


class UserFamilyInline(admin.TabularInline):
    model = UserFamily
    extra = 0


class SupplierAddressInline(admin.StackedInline):
    model = SupplierAddress
    can_delete = False
    max_num = 1


class BankingInformationInline(admin.TabularInline):
    model = BankingInformation
    extra = 0


class SupplierContactInline(admin.TabularInline):
    model = SupplierContact
    extra = 0


class SupplierPartnerInline(admin.TabularInline):
    model = SupplierPartner
    extra = 0


class SupplierRoleInline(admin.TabularInline):
    model = SupplierRole
    extra = 0


class ContractContactInline(admin.TabularInline):
    model = ContractContact
    extra = 0


class ContractOrganizationInline(admin.TabularInline):
    model = ContractOrganization
    extra = 0


class ContractFamilyInline(admin.TabularInline):
    model = ContractFamily
    extra = 0


class ContractPatrimoineInline(admin.TabularInline):
    model = ContractPatrimoine
    extra = 0


class ContractProgrammeInline(admin.TabularInline):
    model = ContractProgramme
    extra = 0


class ContractOperationInline(admin.TabularInline):
    model = ContractOperation
    extra = 0


class ContractPotInline(admin.TabularInline):
    model = ContractPot
    extra = 0


class OrderContactInline(admin.StackedInline):
    model = OrderContact
    can_delete = False
    max_num = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAddressInline(admin.TabularInline):
    model = OrderAddress
    extra = 0


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0


# Définition des classes Admin
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('orga_label', 'orga_node', 'orga_level', 