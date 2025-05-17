#!/bin/bash

# This script runs all the data import commands in the correct order

# Set the working directory to the Django project root
cd "$(dirname "$0")" || exit

# Set the data directory to the parent project's data
DATA_DIR="../data"

# Check if the data directory exists
if [ ! -d "$DATA_DIR" ]; then
    echo "Data directory not found: $DATA_DIR"
    exit 1
fi

# Convert all CSV files to latin1 encoding to ensure compatibility
echo "Converting all CSV files to latin1 encoding..."
find "$DATA_DIR" -name "*.csv" -exec iconv -f utf-8 -t latin1 -o {}.tmp {} \; -exec mv {}.tmp {} \;

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
python manage.py import_municipalities "$DATA_DIR/commune_insee.csv"

echo "Importing accounting entry types..."
python manage.py import_accounting_entry_types "$DATA_DIR/type_d_ecrirture_comptable.csv"

echo "Importing engagement types..."
python manage.py import_engagement_types "$DATA_DIR/type_d_engagement.csv"

echo "Importing reconciliation types..."
python manage.py import_reconciliation_types "$DATA_DIR/type_lettrage.csv"

echo "Importing payer types..."
python manage.py import_payer_types "$DATA_DIR/type_payeur.csv"

echo "Importing service types..."
python manage.py import_service_types "$DATA_DIR/type_prestation.csv"

echo "Importing pricing types..."
python manage.py import_pricing_types "$DATA_DIR/type_tarification.csv"

echo "Importing client account types..."
python manage.py import_client_account_types "$DATA_DIR/type-de-compte-client.csv"

echo "Importing activities..."
python manage.py import_activities "$DATA_DIR/activite.csv"

echo "All data imported successfully!"
