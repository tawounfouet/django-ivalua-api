#!/bin/bash
# Th# Import basic accounting structures first
echo "Importing accounting types..."
python manage.py import_accounting_types "$DATA_DIR/type-de-comptabilite.csv"

echo "Importing fiscal years..."
python manage.py import_fiscal_years "$DATA_DIR/exercice_comptable.csv"

echo "Importing journals..."
python manage.py import_journals "$DATA_DIR/journal_comptable.csv"

echo "Importing PCG (chart of accounts)..."
python manage.py import_pcg "$DATA_DIR/export_comptes_pcg.csv"

# Import reference data entities
echo "Importing municipalities..."
python manage.py import_municipalities "$DATA_DIR/commune_insee.csv"tes the virtual environment and runs all import commands

# Navigate to the Django project directory
cd ~/projets/p2p-ivalua/django-ivalua-api

# Make sure we're in the virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
  source .venv/Scripts/activate
  echo "Virtual environment activated"
fi

DATA_DIR="accounting/data"

echo "Starting import process using data from $DATA_DIR"

# Import basic accounting structures first
echo "Importing accounting types..."
python manage.py import_accounting_types "$DATA_DIR/type-de-comptabilite.csv"

echo "Importing fiscal years..."
python manage.py import_fiscal_years "$DATA_DIR/exercice_comptable.csv"

echo "Importing journals..."
python manage.py import_journals "$DATA_DIR/journal_comptable.csv"

echo "Importing PCG (chart of accounts)..."
python manage.py import_pcg "$DATA_DIR/export_comptes_pcg.csv"

# Import reference data entities
echo "Importing municipalities..."
python manage.py import_municipalities --path "$DATA_DIR/commune_insee.csv"

# Rename the updated import scripts before using them
if [ -f "accounting/management/commands/import_client_account_types.py.new" ]; then
    echo "Using updated import_client_account_types script..."
    mv accounting/management/commands/import_client_account_types.py accounting/management/commands/import_client_account_types.py.bak
    mv accounting/management/commands/import_client_account_types.py.new accounting/management/commands/import_client_account_types.py
fi

echo "Importing client account types..."
python manage.py import_client_account_types --path "$DATA_DIR/type-de-compte-client.csv"

echo "Importing accounting entry types..."
python manage.py import_accounting_entry_types --path "$DATA_DIR/type_d_ecrirture_comptable.csv"

echo "Importing engagement types..."
python manage.py import_engagement_types --path "$DATA_DIR/type_d_engagement.csv"

echo "Importing reconciliation types..."
python manage.py import_reconciliation_types --path "$DATA_DIR/type_lettrage.csv"

echo "Importing payer types..."
python manage.py import_payer_types --path "$DATA_DIR/type_payeur.csv"

echo "Importing service types..."
python manage.py import_service_types --path "$DATA_DIR/type_prestation.csv"

echo "Importing pricing types..."
python manage.py import_pricing_types --path "$DATA_DIR/type_tarification.csv"

echo "Importing activities..."
python manage.py import_activities --path "$DATA_DIR/activite.csv"

echo "All data imported successfully!"
