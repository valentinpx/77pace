#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "requests>=2.28.0",
#     "python-dotenv>=0.19.0",
# ]
# ///
"""
Script pour analyser le temps loggé via l'API 7pace
Usage: uv run 7pace_analyzer.py <work_item_id1> <work_item_id2> ...
"""

import os
import sys
import requests
import json
from collections import defaultdict
from dotenv import load_dotenv
import argparse

class SevenPaceAnalyzer:
    def __init__(self, base_domain, api_key):
        """
        Initialise l'analyseur 7pace
        
        Args:
            base_domain: URL de base de l'organisation 7pace
            api_key: Clé d'API pour l'authentification
        """
        self.base_domain = base_domain.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def get_worklogs_for_workitems(self, work_item_ids):
        """
        Récupère les worklogs pour une liste de work items (par lots de 10)
        """
        def chunked(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        all_worklogs = []

        for work_items_chunk in chunked(work_item_ids, 10):
            work_items_filter = ' or '.join([f"WorkItemId eq {wid}" for wid in work_items_chunk])
            url = f"{self.base_domain}/api/odata/v3.2/workLogsWorkItems"
            params = {
                '$filter': work_items_filter,
                '$select': 'WorkItemId,PeriodLength,User,ActivityType,WorkItem/System_Title,WorkItem/System_WorkItemType,WorkItem/System_TeamProject,Comment,Timestamp'
            }

            while url:
                try:
                    response = requests.get(
                        url,
                        headers=self.headers,
                        params=params if url == f"{self.base_domain}/api/odata/v3.2/workLogsWorkItems" else None
                    )
                    response.raise_for_status()
                    data = response.json()
                    if 'value' in data:
                        all_worklogs.extend(data['value'])
                    url = data.get('@odata.nextLink')
                    params = None  # Les paramètres sont inclus dans nextLink
                except requests.exceptions.RequestException as e:
                    print(f"Erreur lors de la requête API: {e}")
                    return []
                except json.JSONDecodeError as e:
                    print(f"Erreur de décodage JSON: {e}")
                    return []

        return all_worklogs
    
    def analyze_time_by_person_and_category(self, worklogs):
        """
        Analyse le temps par personne et par catégorie
        
        Args:
            worklogs: Liste des worklogs
            
        Returns:
            Dictionnaire avec l'analyse des données
        """
        # Structure: {personne: {catégorie: temps_total}}
        time_by_person_category = defaultdict(lambda: defaultdict(float))
        time_by_person = defaultdict(float)
        time_by_category = defaultdict(float)
        work_items_info = {}
        
        for worklog in worklogs:
            # Extraction des informations
            user_name = worklog.get('User', {}).get('Name', 'Utilisateur inconnu') if isinstance(worklog.get('User'), dict) else str(worklog.get('User', 'Utilisateur inconnu'))
            activity_type = worklog.get('ActivityType', {}).get('Name', 'Activité inconnue') if isinstance(worklog.get('ActivityType'), dict) else str(worklog.get('ActivityType', 'Activité inconnue'))
            period_length = worklog.get('PeriodLength', 0)
            work_item_id = worklog.get('WorkItemId')
            
            # Conversion du temps (PeriodLength est en minutes)
            time_hours = period_length / 3600.00
            
            # Agrégation des données
            time_by_person_category[user_name][activity_type] += time_hours
            time_by_person[user_name] += time_hours
            time_by_category[activity_type] += time_hours
            
            # Stockage des informations de work item
            if work_item_id and work_item_id not in work_items_info:
                work_item = worklog.get('WorkItem', {})
                work_items_info[work_item_id] = {
                    'title': work_item.get('System_Title', 'Titre inconnu'),
                    'type': work_item.get('System_WorkItemType', 'Type inconnu'),
                    'project': work_item.get('System_TeamProject', 'Projet inconnu')
                }
        
        return {
            'by_person_category': dict(time_by_person_category),
            'by_person': dict(time_by_person),
            'by_category': dict(time_by_category),
            'work_items': work_items_info
        }
    
    def display_results(self, analysis, work_item_ids):
        """
        Affiche les résultats dans la console
        
        Args:
            analysis: Résultats de l'analyse
            work_item_ids: Liste des work items analysés
        """
        print("=" * 80)
        print("ANALYSE DU TEMPS LOGGÉ - 7PACE")
        print("=" * 80)
        
        # Informations sur les work items
        print(f"\nWork Items analysés: {', '.join(map(str, work_item_ids))}")
        print("\nDétails des Work Items:")
        for wid, info in analysis['work_items'].items():
            print(f"  #{wid}: {info['title']} ({info['type']} - {info['project']})")
        
        # Temps total par personne
        print(f"\n{'TEMPS TOTAL PAR PERSONNE':<50}")
        print("-" * 50)
        for person, total_time in sorted(analysis['by_person'].items(), key=lambda x: x[1], reverse=True):
            print(f"{person:<30} {total_time:>8.2f}h")
        
        # Temps total par catégorie
        print(f"\n{'TEMPS TOTAL PAR CATÉGORIE':<50}")
        print("-" * 50)
        for category, total_time in sorted(analysis['by_category'].items(), key=lambda x: x[1], reverse=True):
            print(f"{category:<30} {total_time:>8.2f}h")
        
        # Détail par personne et catégorie
        print(f"\n{'DÉTAIL PAR PERSONNE ET CATÉGORIE':<50}")
        print("=" * 80)
        for person, categories in sorted(analysis['by_person_category'].items()):
            print(f"\n{person}:")
            for category, time in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  {category:<28} {time:>8.2f}h")
            print(f"  {'TOTAL':<28} {analysis['by_person'][person]:>8.2f}h")
        
        # Résumé global
        total_time = sum(analysis['by_person'].values())
        print(f"\n{'RÉSUMÉ GLOBAL':<50}")
        print("-" * 50)
        print(f"Temps total loggé: {total_time:.2f}h")
        print(f"Nombre de personnes: {len(analysis['by_person'])}")
        print(f"Nombre de catégories: {len(analysis['by_category'])}")
        print("=" * 80)

def main():
    """Fonction principale"""
    # Chargement des variables d'environnement
    load_dotenv()
    
    base_domain = os.getenv('BASE_DOMAIN')
    api_key = os.getenv('API_KEY')
    
    if not base_domain or not api_key:
        print("Erreur: BASE_DOMAIN et API_KEY doivent être définis dans le fichier .env")
        sys.exit(1)
    
    # Parsing des arguments
    parser = argparse.ArgumentParser(description='Analyse le temps loggé pour des work items 7pace')
    parser.add_argument('work_items', nargs='+', type=int, help='IDs des work items à analyser')
    
    args = parser.parse_args()
    
    # Initialisation de l'analyseur
    analyzer = SevenPaceAnalyzer(base_domain, api_key)
    
    print(f"Récupération des données pour les work items: {args.work_items}")
    
    # Récupération des worklogs
    worklogs = analyzer.get_worklogs_for_workitems(args.work_items)
    
    if not worklogs:
        print("Aucun worklog trouvé pour ces work items.")
        sys.exit(0)
    
    print(f"Trouvé {len(worklogs)} worklogs à analyser...")
    
    # Analyse des données
    analysis = analyzer.analyze_time_by_person_and_category(worklogs)
    
    # Affichage des résultats
    analyzer.display_results(analysis, args.work_items)

if __name__ == "__main__":
    main()
