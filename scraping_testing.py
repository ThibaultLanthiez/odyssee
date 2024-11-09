import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from datetime import datetime, timedelta
import sqlite3

# Initialiser Selenium avec les options nécessaires
def start_browser():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')  # Ignorer les erreurs SSL
    # Configurer le service pour ChromeDriver
    driver_path = 'chromedriver/130/chromedriver.exe'  # Remplacez par le chemin réel vers chromedriver.exe
    service = Service(driver_path)
    return webdriver.Chrome(service=service, options=options)

def accept_cookies(driver):
    try:
        global is_cookies
        if is_cookies:
            accept_cookies_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[class="RxNS RxNS-mod-stretch RxNS-mod-variant-outline RxNS-mod-theme-base RxNS-mod-shape-default RxNS-mod-spacing-base RxNS-mod-size-small"]'))
            )
            accept_cookies_button.click()
            is_cookies = False
            time.sleep(3)  # Laisser un peu de temps après l'acceptation des cookies
    except Exception as e:
        print(f"Erreur lors de l'acceptation des cookies : {e}")

def extract_price(text):
    # Expression régulière pour capturer un nombre qui peut contenir des espaces insécables ou des espaces normaux
    match = re.search(r'\d[\d\s\u202f\u00a0]*', text)
    if match:
        # Supprime tous les types d'espaces et convertir en entier
        return int(match.group().replace(' ', '').replace('\u202f', '').replace('\u00a0', ''))
    else:
        raise ValueError("Aucun prix trouvé dans le texte fourni")
    
def find_price(driver):
    WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'g.price-box'))
        )
    price_box = driver.find_elements(By.CSS_SELECTOR, 'g.price-box')[0]
    price_text = price_box.find_element(By.CLASS_NAME, 'price').text
    # print(f"Prix : {extract_price(price_text)}€")
    return extract_price(price_text)

def find_date(driver):
    # Récupérer la div de classe "day-label" qui est "selected"
    day_label = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.day-label.selected'))
    )
    data_val = day_label.get_attribute('data-val')
    # print(f"Date : {data_val}")
    return data_val

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

def update_db(driver, conn, nb_jours_voyage, id_aeroport_depart, id_aeroport_destination):
    prix = find_price(driver)
    date_debut = find_date(driver)
    date_debut_format = datetime.strptime(date_debut, "%Y-%m-%d")
    date_fin_format = date_debut_format + timedelta(days=nb_jours_voyage)
    print(date_debut_format.strftime("%Y-%m-%d"), 
            date_fin_format.strftime("%Y-%m-%d"), 
            prix, 
            id_aeroport_depart, 
            id_aeroport_destination)
    insert_vol(conn, 
            date_debut_format.strftime("%Y-%m-%d"), 
            date_fin_format.strftime("%Y-%m-%d"), 
            prix, 
            id_aeroport_depart, 
            id_aeroport_destination)
        
try:
    driver = start_browser() # Démarrer le navigateur
    conn = sqlite3.connect('odyssee.db')  # Créer une connexion dans chaque thread
    is_cookies = True
    aeroports_depart = [
                          ["Tous les aéroports de Paris", "PAR", "Paris"],
                          ["Marseille-Provence", "MRS", "Marseille"],
                          ["Lyon Saint-Exupéry", "LYS", "Lyon"],
                          ["Nice Côte d'Azur", "NCE", "Nice"],
                          ["Bordeaux Mérignac", "BOD", "Bordeaux"],
                          ["Nantes Atlantique", "NTE", "Nantes"],
                          ["Lille Lesquin", "LIL", "Lille"],
                          ["Genève-Cointrin", "GVA", "Genève"]
                       ]
    aeroports_destination = [
                               ["Casablanca Mohammed V", "CMN", "Casablanca"],
                               ["Lisbonne Humberto Delgado", "LIS", "Lisbonne"],
                               ["Tous les aéroports de Venise", "VCE", "Venise"],
                               ["Split", "SPU", "Split"],
                               ["Réunion Roland Garros", "RUN", "Saint Denis"],
                               ["Le Caire", "CAI", "Le Caire"],
                               ["Tous les aéroports de Bangkok", "BKK", "Bangkok"],
                               ["Tous les aéroports de Londres", "LON", "Londres"],
                               ["Dublin", "DUB", "Dublin"],
                               ["Mykonos", "JMK", "Mykonos"],
                               ["Tous les aéroports d'Oslo", "OSL", "Oslo"],
                               ["Amsterdam Schiphol", "AMS", "Amsterdam"],
                               ["Tous les aéroports de Montréal", "YMQ", "Montréal"]
                            ]
    nb_jours_voyage_liste = [7, 10, 14]

    for nom_aeroport_destination, code_iata_destination, ville_aeroport_destination in aeroports_destination:
        id_aeroport_destination = get_or_create_aeroport(conn, nom_aeroport_destination, code_iata_destination, ville_aeroport_destination)

        for nom_aeroport_depart, code_iata_depart, ville_aeroport_depart in aeroports_depart:
            id_aeroport_depart = get_or_create_aeroport(conn, nom_aeroport_depart, code_iata_depart, ville_aeroport_depart)
            print(f"{nom_aeroport_depart} <-> {nom_aeroport_destination}")

            try:
                for nb_jours_voyage in nb_jours_voyage_liste:
                    # Ouvrir l'URL de Kayak
                    url = (
                        "https://www.kayak.fr/explore/"
                        f"{code_iata_depart}-{code_iata_destination}/"
                    )
                    driver.get(url)

                    accept_cookies(driver)

                    # Attendre que le SVG avec la classe "graph-area" soit chargé
                    svg_graph_area = WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, 'svg.graph-area'))
                    )

                    # Localiser la première balise <g class="emptyBar selected"> dans le SVG de classe "graph-area"
                    empty_bar_selected = svg_graph_area.find_element(By.CSS_SELECTOR, 'g.emptyBar.selected')
                    empty_bar_selected.click()

                    # Attendre que le bouton increase-duration soit visible
                    increase_duration_button = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'increase-duration'))
                    )
                    time.sleep(3) 

                    nb_click_necessaire = (nb_jours_voyage-4)+1
                    for i in range(nb_click_necessaire): # De 4 à 8
                        increase_duration_button.click()

                    update_db(driver, conn, nb_jours_voyage, id_aeroport_depart, id_aeroport_destination)

                    counter_click = 1 
                    while True:
                        try: 
                            WebDriverWait(svg_graph_area, 20).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, 'g.bar.preselected'))
                            ).click()        
                            counter_click += 1
                            
                            update_db(driver, conn, nb_jours_voyage, id_aeroport_depart, id_aeroport_destination)

                            if counter_click == 14:
                                counter_click = 0
                                driver.find_element(By.CSS_SELECTOR, '.scroll-right').click()

                        except Exception as e:
                            print("Fin du graphique")
                            break
            except Exception as e:
                print(f"Graphique des prix non disponible")
                continue

except Exception as e:
    print(f"Erreur lors du clic : {e}")
finally:
    driver.quit() # Fermer navigateur
    conn.close()  # Fermer connexion bdd
