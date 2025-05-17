#!/bin/bash

# This script runs all the data import commands within Docker

# Set the data directory
DATA_DIR="../data"

# Check if the data directory exists
if [ ! -d "$DATA_DIR" ]; then
    echo "Data directory not found: $DATA_DIR"
    exit 1
fi

# Start the Docker container if not already running
docker-compose up -d

# Define command to run Python in the Docker container
docker_python="docker-compose exec web python"

# Import basic accounting structures first
echo "Importing accounting types..."
$docker_python manage.py import_accounting_types "$DATA_DIR/type-de-comptabilite.csv"

echo "Importing fiscal years..."
$docker_python manage.py import_fiscal_years "$DATA_DIR/exercice_comptable.csv"

echo "Importing journals..."
$docker_python manage.py import_journals "$DATA_DIR/journal_comptable.csv"

echo "Importing PCG (chart of accounts)..."
$docker_python manage.py import_pcg "$DATA_DIR/export_comptes_pcg.csv"

# Import reference data entities
echo "Importing municipalities..."
$docker_python manage.py import_municipalities "$DATA_DIR/commune_insee.csv"

echo "Importing accounting entry types..."
$docker_python manage.py import_accounting_entry_types "$DATA_DIR/type_d_ecrirture_comptable.csv"

echo "Importing engagement types..."
$docker_python manage.py import_engagement_types "$DATA_DIR/type_d_engagement.csv"

echo "Importing reconciliation types..."
$docker_python manage.py import_reconciliation_types "$DATA_DIR/type_lettrage.csv"

echo "Importing payer types..."
$docker_python manage.py import_payer_types "$DATA_DIR/type_payeur.csv"

echo "Importing service types..."
$docker_python manage.py import_service_types "$DATA_DIR/type_prestation.csv"

echo "Importing pricing types..."
$docker_python manage.py import_pricing_types "$DATA_DIR/type_tarification.csv"

echo "Importing client account types..."
$docker_python manage.py import_client_account_types "$DATA_DIR/type-de-compte-client.csv"

echo "Importing activities..."
$docker_python manage.py import_activities "$DATA_DIR/activite.csv"

echo "All data imported successfully!"
