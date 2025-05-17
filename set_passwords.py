import os
import django

# Configurez Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# Importez le modèle après avoir configuré Django
from authentication.models import User

# Définissez des mots de passe pour les utilisateurs fixtures
def set_passwords():
    # Password: 'admin123'
    user = User.objects.get(email='admin@example.com')
    user.set_password('admin123')
    user.save()
    
    # Password: 'staff123'
    user = User.objects.get(email='staff@example.com')
    user.set_password('staff123')
    user.save()
    
    # Password: 'supplier123'
    user = User.objects.get(email='supplier@example.com')
    user.set_password('supplier123')
    user.save()
    
    # Password: 'user123'
    user = User.objects.get(email='user@example.com')
    user.set_password('user123')
    user.save()
    
    # Password: 'inactive123'
    user = User.objects.get(email='inactive@example.com')
    user.set_password('inactive123')
    user.save()
    
    print("All passwords have been set successfully!")

if __name__ == '__main__':
    set_passwords()