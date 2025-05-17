#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Récupération des données de commandes (orders) depuis l'API Ivalua
et sauvegarde dans un fichier JSON.
"""

import os
import sys
import json
import urllib3
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

import requests

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('orders_etl.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Désactiver les avertissements SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration de l'encodage pour la console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


class IvaluaClient:
    """
    Client pour communiquer avec l'API Ivalua.
    """

    ENVIRONMENTS = {
        "recette": "https://env03.ivalua.com/buyer/actionlogement/rctmaint2/yfwag",
        "dev": "https://env11.ivalua.app/buyer/actionlogement/devmaint2/7wbj8",
        "sandbox": "https://env21.ivalua.app/buyer/actionlogement/sandboxmaint/rvr4t"
    }

    def __init__(self, client_id: str, client_secret: str, environment: str = "recette"):
        """
        Initialise le client avec les identifiants.

        Args:
            client_id: Identifiant pour se connecter
            client_secret: Mot de passe pour se connecter
            environment: Environnement à utiliser ('recette', 'dev' ou 'sandbox')
        """
        self.client_id = client_id
        self.client_secret = client_secret

        # Configuration de l'URL selon l'environnement
        if environment not in self.ENVIRONMENTS:
            raise ValueError(f"Environnement non reconnu. Utilisez: {', '.join(self.ENVIRONMENTS.keys())}")
        
        self.base_url = self.ENVIRONMENTS[environment]
        self.token_url = f"{self.base_url}/oauth2/token"
        self.api_url = f"{self.base_url}/api.aspx"
        self.access_token = None

    def get_oauth_token(self) -> str:
        """
        Récupère un token d'accès pour se connecter à l'API.

        Returns:
            str: Le token d'accès OAuth2

        Raises:
            requests.exceptions.RequestException: Si une erreur survient lors de la requête
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
            'scope': 'auth_api_api_endpoint_exec'
        }

        try:
            logger.info("Récupération du token OAuth2...")
            response = requests.post(self.token_url, headers=headers, data=data, verify=False)
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            logger.info(f"Token OAuth2 obtenu avec succès. Longueur: {len(self.access_token)}")
            return self.access_token
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération du token OAuth2: {e}")
            raise

    def get_orders(self, mode: str = "full", ord_id: Optional[str] = None, 
                  sup_id: Optional[str] = None, tiers_code: Optional[str] = None,
                  date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Récupère les informations des commandes (orders).
        
        Args:
            mode: Type de chargement ('full' pour tout charger, 'diff' pour les modifications)
            ord_id: Identifiant(s) de commande séparés par des virgules (optionnel)
            sup_id: Identifiant(s) de fournisseur séparés par des virgules (optionnel)
            tiers_code: Code(s) tiers séparés par des virgules (optionnel)
            date_from: Date de début au format YYYY-MM-DD (optionnel)
            date_to: Date de fin au format YYYY-MM-DD (optionnel)
        
        Returns:
            dict: Les données des commandes au format JSON
        
        Raises:
            requests.exceptions.RequestException: Si une erreur survient lors de la requête
        """
        # Vérifie si on a un token valide
        if not self.access_token:
            self.get_oauth_token()

        # Prépare la requête
        endpoint = "v1.0/ord/orders"
        url = f"{self.api_url}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        params = {
            'mode': mode,
            'format': 'json'
        }
        
        # Ajoute les paramètres optionnels s'ils sont fournis
        if ord_id:
            params['ord_id'] = ord_id
        if sup_id:
            params['sup_id'] = sup_id
        if tiers_code:
            params['tiers_code'] = tiers_code
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to

        try:
            # Envoie la requête
            logger.info(f"Récupération des commandes avec paramètres: {params}")
            response = requests.get(url, headers=headers, params=params, verify=False)
            response.raise_for_status()
            
            # Assurer que l'encodage est correct
            response.encoding = 'utf-8'
            
            # Analyse les données JSON
            data = response.json()
            logger.info(f"Données récupérées avec succès. Nombre total de commandes: {data.get('header', {}).get('totalRow', 0)}")
            
            # Retourne les données
            return data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des commandes: {e}")
            raise

    def get_order_by_id(self, object_id: str, mode: str = "full") -> Dict[str, Any]:
        """
        Récupère les informations d'une commande spécifique par son ID.
        
        Args:
            object_id: Identifiant unique de la commande
            mode: Type de chargement ('full' ou 'diff')
        
        Returns:
            dict: Les données de la commande au format JSON
        
        Raises:
            requests.exceptions.RequestException: Si une erreur survient lors de la requête
        """
        # Vérifie si on a un token valide
        if not self.access_token:
            self.get_oauth_token()

        # Prépare la requête
        endpoint = f"v1.0/ord/orders/{object_id}"
        url = f"{self.api_url}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        params = {
            'mode': mode,
            'format': 'json'
        }

        try:
            # Envoie la requête
            logger.info(f"Récupération de la commande avec ID: {object_id}")
            response = requests.get(url, headers=headers, params=params, verify=False)
            response.raise_for_status()
            
            # Assurer que l'encodage est correct
            response.encoding = 'utf-8'
            
            # Retourne les données
            data = response.json()
            logger.info(f"Commande {object_id} récupérée avec succès")
            return data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération de la commande {object_id}: {e}")
            raise

    def save_orders_data(self, data: Dict[str, Any], output_file: str) -> None:
        """
        Sauvegarde les données des commandes dans un fichier JSON.
        
        Args:
            data: Données des commandes à sauvegarder
            output_file: Chemin du fichier de sortie
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"Données des commandes sauvegardées dans '{output_file}'")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données: {e}")
            raise

    def display_orders_summary(self, orders_data: Dict[str, Any], max_display: int = 5) -> None:
        """
        Affiche un résumé des commandes récupérées.
        
        Args:
            orders_data: Données des commandes
            max_display: Nombre maximum de commandes à afficher
        """
        if not isinstance(orders_data, dict):
            logger.error("Format de données invalide")
            return
        
        header = orders_data.get('header', {})
        orders_list = orders_data.get('orders', [])
        
        logger.info(f"Nombre total de commandes: {header.get('totalRow', 'Non spécifié')}")
        logger.info(f"Nombre de commandes récupérées: {len(orders_list)}")
        
        # Affiche les informations de base pour chaque commande (limitées à max_display)
        display_count = min(max_display, len(orders_list))
        for i, order in enumerate(orders_list[:display_count]):
            data_order = order.get('dataOrder', {})
            logger.info(f"\nCommande {i + 1}/{display_count}:")
            logger.info(f"ID: {data_order.get('id')}")
            logger.info(f"Code: {data_order.get('orderCode')}")
            logger.info(f"Libellé: {data_order.get('orderLabel')}")
            logger.info(f"Statut: {data_order.get('statusLabel')} ({data_order.get('statusCode')})")
            logger.info(f"Date: {data_order.get('ordOrderDate')}")
            logger.info(f"Montant total: {data_order.get('oitemsTotalAmount')} {data_order.get('unitCodeCurrency')}")
            logger.info(f"Fournisseur: {data_order.get('orderSupName')} (ID: {data_order.get('orderSupId')})")
            
            # Affiche des informations sur les lignes de commande
            order_items = order.get('orderItems', [])
            if order_items:
                logger.info(f"Lignes de commande ({len(order_items)}):")
                for j, item in enumerate(order_items[:3], 1):  # Affiche seulement les 3 premières lignes
                    logger.info(f"  {j}. {item.get('oitemLabel')} - Quantité: {item.get('oitemQuantity')} - "
                               f"Montant: {item.get('oitemTotalAmount')}")
                if len(order_items) > 3:
                    logger.info(f"  ... et {len(order_items) - 3} autre(s) ligne(s)")


def main():
    """Fonction principale pour récupérer et sauvegarder les données des commandes."""
    try:
        # Identifiants de connexion
        client_id = "a1359da1-a321-4ff9-9c1b-bb136459bdb0"
        client_secret = "20ba391f0518754bbd314776ee0595771b6abcd5697f68ea522c7fcbc1611303"

        # Paramètres pour la récupération des commandes
        environment = "recette"
        output_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Format du nom de fichier de sortie avec date
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"orders_data_{current_date}.json")
        
        # Création du client
        logger.info(f"Initialisation du client Ivalua (environnement: {environment})")
        client = IvaluaClient(client_id, client_secret, environment=environment)

        # Récupération des commandes
        logger.info("=== RÉCUPÉRATION DES COMMANDES ===")
        
        # Récupération en mode "full" - toutes les commandes
        orders_data = client.get_orders(mode="full")
        
        # Alternative: récupération avec filtres de date
        # orders_data = client.get_orders(
        #     mode="diff",
        #     date_from="2025-03-01",
        #     date_to="2025-05-09"
        # )
        
        # Sauvegarde des données
        client.save_orders_data(orders_data, output_file)
        
        # Affichage d'un résumé
        client.display_orders_summary(orders_data)
        
        # Vous pouvez également récupérer une commande spécifique par son ID
        # order_id = "1"  # Remplacer par l'ID réel d'une commande
        # specific_order = client.get_order_by_id(order_id)
        # client.save_orders_data(specific_order, f"order_{order_id}_{current_date}.json")
        
        logger.info("Traitement terminé avec succès")
        
    except Exception as e:
        logger.error(f"Une erreur est survenue lors du traitement: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()