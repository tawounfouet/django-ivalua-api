# filepath: c:\Users\awounfouet\projets\p2p-ivalua\django-ivalua-api\project\admin.py

from django.contrib import admin
from django.contrib.admin import AdminSite

# Personnaliser l'admin site
admin.site.site_header = 'Administration P2P Ivalua'
admin.site.site_title = 'P2P Ivalua'
admin.site.index_title = 'Tableau de bord'

# Regrouper les modèles (pour Django standard admin, pas admin_interface)
admin.site.register_index = lambda request, extra_context=None: admin.site.index(request, {
    'app_list': [
        {
            'name': 'Utilisateurs',
            'models': [
                {'name': 'Utilisateurs', 'object_name': 'User', 'admin_url': '/admin/authentication/user/'},
                {'name': 'Profils', 'object_name': 'UserProfile', 'admin_url': '/admin/authentication/userprofile/'},
            ]
        },
        {
            'name': 'Fournisseurs',
            'models': [
                {'name': 'Fournisseurs', 'object_name': 'Supplier', 'admin_url': '/admin/suppliers/supplier/'},
                # Ajoutez d'autres modèles ici
            ]
        }
    ]
})