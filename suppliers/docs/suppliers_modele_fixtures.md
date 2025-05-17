

Fixtures pour l'application Suppliers
Voici des fixtures pour votre application Suppliers qui complètent celles déjà définies pour l'application Authentication. Je vais créer plusieurs fichiers pour organiser les différentes entités du modèle.

1. suppliers.json - Données des fournisseurs principaux
2. addresses.json - Adresses des fournisseurs

GitHub Copilot
Fixtures pour l'application Suppliers
Voici des fixtures pour votre application Suppliers qui complètent celles déjà définies pour l'application Authentication. Je vais créer plusieurs fichiers pour organiser les différentes entités du modèle.

1. suppliers.json - Données des fournisseurs principaux
2. addresses.json - Adresses des fournisseurs
3. banking_information.json - Informations bancaires
4. contacts.json - Contacts des fournisseurs
5. contact_roles.json - Rôles des contacts
6. supplier_partners.json - Partenariats fournisseurs
7. supplier_roles.json - Rôles des fournisseurs

Utilisation des fixtures
Pour utiliser ces fixtures, procédez comme suit :

Créez le répertoire fixtures s'il n'existe pas déjà :
```bash 
mkdir -p suppliers/fixtures
```
Créez les fichiers JSON dans ce répertoire :
```bash
touch suppliers/fixtures/suppliers.json
touch suppliers/fixtures/addresses.json 
touch suppliers/fixtures/banking_information.json
touch suppliers/fixtures/contacts.json
touch suppliers/fixtures/contact_roles.json
touch suppliers/fixtures/supplier_partners.json
touch suppliers/fixtures/supplier_roles.json
```
Enregistrez les fichiers JSON dans ce répertoire.
Chargez les fixtures dans votre base de données :
```bash
python manage.py loaddata suppliers/fixtures/suppliers.json suppliers/fixtures/addresses.json suppliers/fixtures/banking_information.json suppliers/fixtures/contacts.json suppliers/fixtures/contact_roles.json suppliers/fixtures/supplier_partners.json suppliers/fixtures/supplier_roles.json
```

Ces fixtures proposent un jeu de données complet et réaliste pour votre modèle suppliers, avec :

Cinq fournisseurs de différents types (entreprises, individu, syndicat)
Leurs adresses respectives
Des informations bancaires pour chaque fournisseur
Des contacts internes et externes
Des rôles attribués aux contacts
Des partenariats entre fournisseurs et divisions organisationnelles
Des rôles spécifiques attribués aux fournisseurs dans l'organisation
Ces données d'exemple vous permettront de tester toutes les fonctionnalités de votre application et de visualiser rapidement comment elle se comportera avec des données réelles.