import re
import pandas as pd
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configurer le service pour ChromeDriver
driver_path = 'chromedriver/130/chromedriver.exe'  # Remplacez par le chemin réel vers chromedriver.exe
service = Service(driver_path)

# Fonction pour démarrer un navigateur Selenium
def start_browser():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')  # Ignorer les erreurs SSL
    return webdriver.Chrome(service=service, options=options)

# Fonction pour accepter les cookies
def accept_cookies(driver):
    try:
        accept_cookies_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[class="RxNS RxNS-mod-stretch RxNS-mod-variant-outline RxNS-mod-theme-base RxNS-mod-shape-default RxNS-mod-spacing-base RxNS-mod-size-small"]'))
        )
        accept_cookies_button.click()
        time.sleep(5)  # Laisser un peu de temps après l'acceptation des cookies
    except Exception as e:
        print(f"Erreur lors de l'acceptation des cookies : {e}")

# Vérifier si une ville existe dans la table 'ville' et l'insérer si elle n'existe pas
def get_or_create_ville(conn, nom_ville):
    cursor = conn.cursor()
    cursor.execute("SELECT id_ville FROM ville WHERE nom_ville = ?", (nom_ville,))
    result = cursor.fetchone()
    if result:
        return result[0]  # Retourne l'id_ville si la ville existe déjà

    # Insérer la nouvelle ville
    cursor.execute("INSERT INTO ville (nom_ville, descriptif_ville) VALUES (?, ?)", (nom_ville, None))
    conn.commit()
    return cursor.lastrowid  # Retourne l'id_ville nouvellement créé

# Vérifier si un aéroport existe dans la table 'aeroport' et l'insérer si nécessaire
def get_or_create_aeroport(conn, nom_aeroport, code_iata, ville_name):
    cursor = conn.cursor()

    # Vérifier si l'aéroport existe déjà
    cursor.execute("SELECT id_aeroport FROM aeroport WHERE code_iata = ?", (code_iata,))
    result = cursor.fetchone()
    if result:
        return result[0]  # Retourne l'id_aeroport si l'aéroport existe déjà

    # Sinon, obtenir l'id de la ville ou la créer si elle n'existe pas
    id_ville = get_or_create_ville(conn, ville_name)

    # Insérer l'aéroport
    cursor.execute(
        "INSERT INTO aeroport (id_ville, nom_aeroport, code_iata, descriptif_aeroport) VALUES (?, ?, ?, ?)",
        (id_ville, nom_aeroport, code_iata, None)
    )
    conn.commit()
    return cursor.lastrowid  # Retourne l'id_aeroport nouvellement créé

# Insérer un vol dans la table 'vol' ou mettre à jour si les dates existent déjà
def insert_vol(conn, date_debut, date_fin, prix, aeroport_depart, aeroport_destination):
    cursor = conn.cursor()
    
    # Vérifier si un vol existe déjà avec les mêmes dates
    cursor.execute(
        "SELECT prix_vol FROM vol WHERE id_aeroport_depart = ? AND id_aeroport_destination = ? "
        "AND date_aller = ? AND date_retour = ?",
        (aeroport_depart, aeroport_destination, date_debut, date_fin)
    )
    
    result = cursor.fetchone()
    
    if result:
        # Si une entrée existe déjà, on met à jour le prix du vol
        cursor.execute(
            "UPDATE vol SET prix_vol = ? WHERE id_aeroport_depart = ? AND id_aeroport_destination = ? "
            "AND date_aller = ? AND date_retour = ?",
            (prix, aeroport_depart, aeroport_destination, date_debut, date_fin)
        )
    else:
        # Insérer un nouveau vol si aucune entrée n'est trouvée
        cursor.execute(
            "INSERT INTO vol (id_aeroport_depart, id_aeroport_destination, prix_vol, lien_vol, date_aller, date_retour) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (aeroport_depart, aeroport_destination, prix, None, date_debut, date_fin)
        )
    
    conn.commit()  # Confirmer la transaction

# Fonction pour effectuer le scraping d'une période donnée avec un navigateur déjà démarré
def scrape_with_browser(driver, date_debut, date_fin, cookies_accepted):
    url = (
        f"https://www.kayak.fr/flights/CDG,ORY-AMS/{date_debut}/{date_fin}?"
        "fs=cfc=1&sort=bestflight_a#default"
    )
    driver.get(url)

    try:
        if not cookies_accepted:
            accept_cookies(driver)
            cookies_accepted = True

        time.sleep(2)

        price_columns = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f'div[data-content="bestflight_a"]'))
        )

        data = price_columns.get_attribute('innerText')
        price = ''.join([char for char in data.split(' ')[2] if char.isdigit()])
        print(date_debut, date_fin, price)

        data_json = {
            "date_debut": date_debut,
            "date_fin": date_fin,
            "prix": price,
        }
        print(data_json)
        return data_json

    except Exception as e:
        print(f"Erreur lors de la récupération des données pour {date_debut} - {date_fin} : {e}")
        return None

# Fonction gérant le scraping pour une liste de dates avec réutilisation du navigateur
def thread_scraper(date_ranges):
    driver = start_browser()  # Démarrer un navigateur pour ce thread
    cookies_accepted = False
    thread_data = []
    conn = sqlite3.connect('odyssee.db')  # Créer une connexion dans chaque thread

    for date_debut, date_fin in date_ranges:
        data = scrape_with_browser(driver, date_debut, date_fin, cookies_accepted)
        if data:
            # Obtenir ou créer les aéroports
            id_aeroport_depart = get_or_create_aeroport(conn, 'Charles de Gaulle', 'CDG', 'Paris')
            id_aeroport_orly = get_or_create_aeroport(conn, 'Orly', 'ORY', 'Paris')
            id_aeroport_destination = get_or_create_aeroport(conn, 'Amsterdam Schiphol', 'AMS', 'Amsterdam')

            # Insertion du vol
            insert_vol(conn, data["date_debut"], data["date_fin"], data["prix"], id_aeroport_depart, id_aeroport_destination)
            thread_data.append(data)
        cookies_accepted = True  # Les cookies sont acceptés une fois, pas besoin de répéter

    #driver.quit()  # Fermer le navigateur lorsque toutes les requêtes sont terminées
    conn.close()  # Fermer la connexion à la base de données
    return thread_data

# Boucle sur chaque jour de janvier 2025 avec des intervalles de 7 jours
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 6, 30)
delta = timedelta(days=1)
days_span = timedelta(days=7)

# Liste pour stocker les périodes à scraper
date_ranges = []

while start_date <= end_date:
    date_debut = start_date.strftime("%Y-%m-%d")
    date_fin = (start_date + days_span).strftime("%Y-%m-%d")
    date_ranges.append((date_debut, date_fin))
    start_date += delta

# Diviser les date_ranges pour chaque thread
def split_date_ranges(date_ranges, num_splits):
    k, m = divmod(len(date_ranges), num_splits)
    return [date_ranges[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(num_splits)]

# Répartir les périodes à scraper pour chaque thread
num_threads = 3  # Nombre de threads à utiliser
split_ranges = split_date_ranges(date_ranges, num_threads)

# Utiliser ThreadPoolExecutor pour exécuter les appels de scraping en parallèle
all_data = []

with ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = [executor.submit(thread_scraper, ranges) for ranges in split_ranges]

    for future in as_completed(futures):  # as_completed attend chaque future indépendamment
        result = future.result()
        if result:
            all_data.extend(result)
