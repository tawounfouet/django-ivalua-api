import os
import django
import sys
import csv
from pathlib import Path

# Add the project directory to the Python path
project_path = os.path.dirname(os.path.abspath(__file__))
if project_path not in sys.path:
    sys.path.append(project_path)

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

# Now we can import Django models
from accounting.models.reference_data import (
    Municipality, 
    ClientAccountType,
    AccountingEntryType,
    EngagementType,
    ReconciliationType,
    Activity,
    ServiceType,
    PricingType,
    PayerType
)

# Data directory inside accounting app
data_dir = Path(os.path.join(project_path, 'accounting', 'data'))

def import_municipalities():
    print("Importing municipalities...")
    path = data_dir / 'commune_insee.csv'
    try:
        with open(path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            # Clear existing data if any
            Municipality.objects.all().delete()
            print('All existing municipalities cleared from database.')
            
            # Import data
            count = 0
            for row in reader:
                # Extract data from CSV
                insee_code = row.get('CODE_COMMUNE_INSEE', '').strip()
                name = row.get('LIB_COMMUNE_INSEE', '').strip()
                postal_code = row.get('CODE_POSTAL', '').strip()
                department_code = row.get('CODE_DEPT_COMMUNE_INSEE', '').strip()
                region_code = row.get('INDIC_EPCI', '').strip()
                
                if not insee_code or not name:
                    continue
                
                # Create Municipality object
                Municipality.objects.create(
                    insee_code=insee_code,
                    name=name,
                    postal_code=postal_code,
                    department_code=department_code,
                    region_code=region_code
                )
                count += 1
            
            print(f'Successfully imported {count} municipalities')
    except Exception as e:
        print(f'Error importing municipalities: {str(e)}')

def import_client_account_types():
    print("Importing client account types...")
    path = data_dir / 'type-de-compte-client.csv'
    try:
        with open(path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            # Clear existing data if any
            ClientAccountType.objects.all().delete()
            print('All existing client account types cleared from database.')
            
            # Import data
            count = 0
            for row in reader:
                code = row.get('CODE', '').strip()
                name = row.get('NAME', '').strip()
                
                if not code or not name:
                    continue
                
                ClientAccountType.objects.create(
                    code=code,
                    name=name
                )
                count += 1
            
            print(f'Successfully imported {count} client account types')
    except Exception as e:
        print(f'Error importing client account types: {str(e)}')

def import_accounting_entry_types():
    print("Importing accounting entry types...")
    path = data_dir / 'type_d_ecrirture_comptable.csv'
    try:
        with open(path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            # Clear existing data if any
            AccountingEntryType.objects.all().delete()
            print('All existing accounting entry types cleared from database.')
            
            # Import data
            count = 0
            for row in reader:
                code = row.get('CODE', '').strip()
                name = row.get('NAME', '').strip()
                indicator_code = row.get('INDICATOR_CODE', '').strip()
                indicator_name = row.get('INDICATOR_NAME', '').strip()
                
                if not code or not name:
                    continue
                
                AccountingEntryType.objects.create(
                    code=code,
                    name=name,
                    indicator_code=indicator_code,
                    indicator_name=indicator_name
                )
                count += 1
            
            print(f'Successfully imported {count} accounting entry types')
    except Exception as e:
        print(f'Error importing accounting entry types: {str(e)}')

def import_engagement_types():
    print("Importing engagement types...")
    path = data_dir / 'type_d_engagement.csv'
    try:
        with open(path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            # Clear existing data if any
            EngagementType.objects.all().delete()
            print('All existing engagement types cleared from database.')
            
            # Import data
            count = 0
            for row in reader:
                code = row.get('CODE', '').strip()
                name = row.get('NAME', '').strip()
                
                if not code or not name:
                    continue
                
                EngagementType.objects.create(
                    code=code,
                    name=name
                )
                count += 1
            
            print(f'Successfully imported {count} engagement types')
    except Exception as e:
        print(f'Error importing engagement types: {str(e)}')

def import_reconciliation_types():
    print("Importing reconciliation types...")
    path = data_dir / 'type_lettrage.csv'
    try:
        with open(path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            # Clear existing data if any
            ReconciliationType.objects.all().delete()
            print('All existing reconciliation types cleared from database.')
            
            # Import data
            count = 0
            for row in reader:
                code = row.get('CODE', '').strip()
                name = row.get('NAME', '').strip()
                
                if not code or not name:
                    continue
                
                ReconciliationType.objects.create(
                    code=code,
                    name=name
                )
                count += 1
            
            print(f'Successfully imported {count} reconciliation types')
    except Exception as e:
        print(f'Error importing reconciliation types: {str(e)}')

def import_payer_types():
    print("Importing payer types...")
    path = data_dir / 'type_payeur.csv'
    try:
        with open(path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            # Clear existing data if any
            PayerType.objects.all().delete()
            print('All existing payer types cleared from database.')
            
            # Import data
            count = 0
            for row in reader:
                code = row.get('CODE', '').strip()
                name = row.get('NAME', '').strip()
                
                if not code or not name:
                    continue
                
                PayerType.objects.create(
                    code=code,
                    name=name
                )
                count += 1
            
            print(f'Successfully imported {count} payer types')
    except Exception as e:
        print(f'Error importing payer types: {str(e)}')

def import_service_types():
    print("Importing service types...")
    path = data_dir / 'type_prestation.csv'
    try:
        with open(path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            # Clear existing data if any
            ServiceType.objects.all().delete()
            print('All existing service types cleared from database.')
            
            # Import data
            count = 0
            for row in reader:
                id_service_type = row.get('ID_SERVICE_TYPE', '').strip()
                code = row.get('CODE', '').strip()
                name = row.get('NAME', '').strip()
                category_code = row.get('CATEGORY_CODE', '').strip()
                category_name = row.get('CATEGORY_NAME', '').strip()
                
                if not id_service_type or not code or not name:
                    continue
                
                ServiceType.objects.create(
                    id_service_type=id_service_type,
                    code=code,
                    name=name,
                    category_code=category_code,
                    category_name=category_name
                )
                count += 1
            
            print(f'Successfully imported {count} service types')
    except Exception as e:
        print(f'Error importing service types: {str(e)}')

def import_pricing_types():
    print("Importing pricing types...")
    path = data_dir / 'type_tarification.csv'
    try:
        with open(path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            # Clear existing data if any
            PricingType.objects.all().delete()
            print('All existing pricing types cleared from database.')
            
            # Import data
            count = 0
            for row in reader:
                code = row.get('CODE', '').strip()
                name = row.get('NAME', '').strip()
                
                if not code or not name:
                    continue
                
                PricingType.objects.create(
                    code=code,
                    name=name
                )
                count += 1
            
            print(f'Successfully imported {count} pricing types')
    except Exception as e:
        print(f'Error importing pricing types: {str(e)}')

def import_activities():
    print("Importing activities...")
    path = data_dir / 'activite.csv'
    try:
        with open(path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            # Clear existing data if any
            Activity.objects.all().delete()
            print('All existing activities cleared from database.')
            
            # Import data
            count = 0
            for row in reader:
                code = row.get('CODE', '').strip()
                name = row.get('NAME', '').strip()
                
                if not code or not name:
                    continue
                
                Activity.objects.create(
                    code=code,
                    name=name
                )
                count += 1
            
            print(f'Successfully imported {count} activities')
    except Exception as e:
        print(f'Error importing activities: {str(e)}')

if __name__ == '__main__':
    print("Running reference data imports...")
    
    import_client_account_types()
    import_accounting_entry_types()
    import_engagement_types()
    import_reconciliation_types()
    import_payer_types()
    import_service_types()
    import_pricing_types()
    import_activities()
    import_municipalities()
    
    print("All reference data imports completed successfully!")
