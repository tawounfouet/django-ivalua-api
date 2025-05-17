# PowerShell script to import all accounting data

# Set the working directory to the Django project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $ScriptDir

# Set the data directory to the parent project's data
$DATA_DIR = "../data"

# Check if the data directory exists
if (-not (Test-Path $DATA_DIR)) {
    Write-Error "Data directory not found: $DATA_DIR"
    exit 1
}

# Note: We don't need to convert encoding in PowerShell script
# The import scripts will try different encodings automatically

# Import basic accounting structures first
Write-Host "Importing accounting types..."
python manage.py import_accounting_types "$DATA_DIR/type-de-comptabilite.csv"

Write-Host "Importing fiscal years..."
python manage.py import_fiscal_years "$DATA_DIR/exercice_comptable.csv"

Write-Host "Importing journals..."
python manage.py import_journals "$DATA_DIR/journal_comptable.csv"

Write-Host "Importing PCG (chart of accounts)..."
python manage.py import_pcg "$DATA_DIR/export_comptes_pcg.csv"

# Import reference data entities
Write-Host "Importing municipalities..."
python manage.py import_municipalities "$DATA_DIR/commune_insee.csv"

Write-Host "Importing accounting entry types..."
python manage.py import_accounting_entry_types "$DATA_DIR/type_d_ecrirture_comptable.csv"

Write-Host "Importing engagement types..."
python manage.py import_engagement_types "$DATA_DIR/type_d_engagement.csv"

Write-Host "Importing reconciliation types..."
python manage.py import_reconciliation_types "$DATA_DIR/type_lettrage.csv"

Write-Host "Importing payer types..."
python manage.py import_payer_types "$DATA_DIR/type_payeur.csv"

Write-Host "Importing service types..."
python manage.py import_service_types "$DATA_DIR/type_prestation.csv"

Write-Host "Importing pricing types..."
python manage.py import_pricing_types "$DATA_DIR/type_tarification.csv"

Write-Host "Importing client account types..."
python manage.py import_client_account_types "$DATA_DIR/type-de-compte-client.csv"

Write-Host "Importing activities..."
python manage.py import_activities "$DATA_DIR/activite.csv"

Write-Host "All data imported successfully!"
