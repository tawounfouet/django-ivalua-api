# PowerShell script to import all accounting data through Docker

# Set the data directory to the parent project's data
$DATA_DIR = "../data"

# Check if the data directory exists
if (-not (Test-Path $DATA_DIR)) {
    Write-Error "Data directory not found: $DATA_DIR"
    exit 1
}

# Start the Docker container if not already running
docker-compose up -d

# Define command to run Python in the Docker container
$docker_python = "docker-compose exec -T web python"

# Import basic accounting structures first
Write-Host "Importing accounting types..."
Invoke-Expression "$docker_python manage.py import_accounting_types '$DATA_DIR/type-de-comptabilite.csv'"

Write-Host "Importing fiscal years..."
Invoke-Expression "$docker_python manage.py import_fiscal_years '$DATA_DIR/exercice_comptable.csv'"

Write-Host "Importing journals..."
Invoke-Expression "$docker_python manage.py import_journals '$DATA_DIR/journal_comptable.csv'"

Write-Host "Importing PCG (chart of accounts)..."
Invoke-Expression "$docker_python manage.py import_pcg '$DATA_DIR/export_comptes_pcg.csv'"

# Import reference data entities
Write-Host "Importing municipalities..."
Invoke-Expression "$docker_python manage.py import_municipalities '$DATA_DIR/commune_insee.csv'"

Write-Host "Importing accounting entry types..."
Invoke-Expression "$docker_python manage.py import_accounting_entry_types '$DATA_DIR/type_d_ecrirture_comptable.csv'"

Write-Host "Importing engagement types..."
Invoke-Expression "$docker_python manage.py import_engagement_types '$DATA_DIR/type_d_engagement.csv'"

Write-Host "Importing reconciliation types..."
Invoke-Expression "$docker_python manage.py import_reconciliation_types '$DATA_DIR/type_lettrage.csv'"

Write-Host "Importing payer types..."
Invoke-Expression "$docker_python manage.py import_payer_types '$DATA_DIR/type_payeur.csv'"

Write-Host "Importing service types..."
Invoke-Expression "$docker_python manage.py import_service_types '$DATA_DIR/type_prestation.csv'"

Write-Host "Importing pricing types..."
Invoke-Expression "$docker_python manage.py import_pricing_types '$DATA_DIR/type_tarification.csv'"

Write-Host "Importing client account types..."
Invoke-Expression "$docker_python manage.py import_client_account_types '$DATA_DIR/type-de-compte-client.csv'"

Write-Host "Importing activities..."
Invoke-Expression "$docker_python manage.py import_activities '$DATA_DIR/activite.csv'"

Write-Host "All data imported successfully!"
