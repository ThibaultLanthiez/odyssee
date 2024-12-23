import time
import threading
import sqlite3
import re
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialiser Selenium avec les options nécessaires
def start_browser():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    driver_path = 'chromedriver/130/chromedriver.exe'
    service = Service(driver_path)
    return webdriver.Chrome(service=service, options=options)

def accept_cookies(driver):
    try:
        global is_cookies
        if is_cookies:
            accept_cookies_button = WebDriverWait(driver, 40).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[class="RxNS RxNS-mod-stretch RxNS-mod-variant-outline RxNS-mod-theme-base RxNS-mod-shape-default RxNS-mod-spacing-base RxNS-mod-size-small"]'))
            )
            
            accept_cookies_button.click()
            time.sleep(12)
            is_cookies = False
    except Exception as e:
        print(f"Erreur lors de l'acceptation des cookies : {e}")

def extract_price(text):
    match = re.search(r'\d[\d\s\u202f\u00a0]*', text)
    if match:
        return int(match.group().replace(' ', '').replace('\u202f', '').replace('\u00a0', ''))
    else:
        raise ValueError("Aucun prix trouvé dans le texte fourni")

def find_price(driver):
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'g.price-box'))
    )
    price_box = driver.find_elements(By.CSS_SELECTOR, 'g.price-box')[0]
    price_text = price_box.find_element(By.CLASS_NAME, 'price').text
    return extract_price(price_text)

def find_date(driver):
    day_label = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.day-label.selected'))
    )
    return day_label.get_attribute('data-val')

def get_or_create_ville(conn, nom_ville):
    cursor = conn.cursor()
    cursor.execute("SELECT id_ville FROM ville WHERE nom_ville = ?", (nom_ville,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("INSERT INTO ville (nom_ville, descriptif_ville) VALUES (?, ?)", (nom_ville, None))
    conn.commit()
    return cursor.lastrowid

def get_or_create_aeroport(conn, nom_aeroport, code_iata, ville_name):
    cursor = conn.cursor()
    cursor.execute("SELECT id_aeroport FROM aeroport WHERE code_iata = ?", (code_iata,))
    result = cursor.fetchone()
    if result:
        return result[0]
    id_ville = get_or_create_ville(conn, ville_name)
    cursor.execute(
        "INSERT INTO aeroport (id_ville, nom_aeroport, code_iata, descriptif_aeroport) VALUES (?, ?, ?, ?)",
        (id_ville, nom_aeroport, code_iata, None)
    )
    conn.commit()
    return cursor.lastrowid

def insert_vol(conn, date_debut, date_fin, prix, aeroport_depart, aeroport_destination):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT prix_vol FROM vol WHERE id_aeroport_depart = ? AND id_aeroport_destination = ? "
        "AND date_aller = ? AND date_retour = ?",
        (aeroport_depart, aeroport_destination, date_debut, date_fin)
    )
    result = cursor.fetchone()
    if result:
        cursor.execute(
            "UPDATE vol SET prix_vol = ? WHERE id_aeroport_depart = ? AND id_aeroport_destination = ? "
            "AND date_aller = ? AND date_retour = ?",
            (prix, aeroport_depart, aeroport_destination, date_debut, date_fin)
        )
    else:
        cursor.execute(
            "INSERT INTO vol (id_aeroport_depart, id_aeroport_destination, prix_vol, lien_vol, date_aller, date_retour) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (aeroport_depart, aeroport_destination, prix, None, date_debut, date_fin)
        )
    conn.commit()

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

def process_destinations(destinations):
    driver = start_browser()
    conn = sqlite3.connect('odyssee.db')
    global is_cookies
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
    nb_jours_voyage_liste = [7, 10, 14]

    for nom_aeroport_destination, code_iata_destination, ville_aeroport_destination in destinations:
        id_aeroport_destination = get_or_create_aeroport(conn, nom_aeroport_destination, code_iata_destination, ville_aeroport_destination)

        for nom_aeroport_depart, code_iata_depart, ville_aeroport_depart in aeroports_depart:
            id_aeroport_depart = get_or_create_aeroport(conn, nom_aeroport_depart, code_iata_depart, ville_aeroport_depart)
            print(f"{nom_aeroport_depart} <-> {nom_aeroport_destination}")

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
                empty_bar_selected = WebDriverWait(svg_graph_area, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'g.emptyBar.selected'))
                )
                empty_bar_selected.click()

                # Attendre que le bouton increase-duration soit visible
                increase_duration_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'increase-duration'))
                )
                nb_click_necessaire = (nb_jours_voyage-4)+1
                for i in range(nb_click_necessaire): # De 4 à 8
                    increase_duration_button.click()

                update_db(driver, conn, nb_jours_voyage, id_aeroport_depart, id_aeroport_destination)

                counter_click = 1 
                while True:
                    try: 
                        WebDriverWait(svg_graph_area, 20).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'g.bar.preselected'))
                        ).click()        
                        counter_click += 1
                        
                        update_db(driver, conn, nb_jours_voyage, id_aeroport_depart, id_aeroport_destination)

                        if counter_click == 14:
                            counter_click = 0
                            driver.find_element(By.CSS_SELECTOR, '.scroll-right').click()

                    except Exception as e:
                        print("Fin du graphique")
                        break
    driver.quit()
    conn.close()

def split_list(lst, n):
    result = [[] for _ in range(n)]
    for i, elem in enumerate(lst):
        result[i % n].append(elem)
    return result

if __name__ == "__main__":

    nb_threads = 3

    # Listes de destinations
    aeroports_destinations = [
        ["Tous les aéroports de Reykjavik", "REK", "Reykjavik"], 
        ["Palma de Majorque", "PMI", "Palma de Majorque"], 
        ["Vilnius", "VNO", "Vilnius"], 
        ["Riga", "RIX", "Riga"], 
        ["Tallinn", "TLL", "Tallinn"], 
        ["Berlin Brandebourg", "BER", "Berlin"],
        ["Tous les aéroports de Varsovie", "WAW", "Varsovie"], 
        ["Palerme Falcone-Borsellino", "PMO", "Palerme"], 
        ["Sardaigne Cagliari-Elmas", "CAG", "Cagliari"], 
        ["Tous les aéroports de Rome", "ROM", "Rome"], 
        ["Malaga", "AGP", "Malaga"], 
        ["Madrid-Barajas", "MAD", "Madrid"],
        ["Copenhague Kastrup", "CPH", "Copenhague"],
        ["Vienne-Schwechat", "VIE", "Vienne"],
        ["Tous les aéroports d'Istanbul", "IST", "Istanbul"], 
        ["Guadeloupe - Pointe-à-Pitre Le Raizet", "PTP", "Guadeloupe"],
        ["Osaka", "KIX", "Osaka"], 
        ["Le Caire", "CAI", "Le Caire"],
        ["Tous les aéroports de Montréal", "YMQ", "Montréal"],
        ["Casablanca Mohammed V", "CMN", "Casablanca"],
        ["Lisbonne Humberto Delgado", "LIS", "Lisbonne"],
        ["Tous les aéroports de Venise", "VCE", "Venise"],
        ["Amsterdam Schiphol", "AMS", "Amsterdam"],
        ["Helsinki-Vantaa", "HEL", "Helsinki"], 
        ["Édimbourg", "EDI", "Édimbourg"],
        ["Tous les aéroports de Stockholm", "STO", "Stockholm"], 
        ["Split", "SPU", "Split"],
        ["Réunion Roland Garros", "RUN", "Saint Denis"],
        ["Tous les aéroports de Bangkok", "BKK", "Bangkok"],
        ["Tous les aéroports de Londres", "LON", "Londres"],
        ["Dublin", "DUB", "Dublin"],
        ["Mykonos", "JMK", "Mykonos"],
        ["Tous les aéroports d'Oslo", "OSL", "Oslo"]
    ]

    # Diviser en 4 sous-listes
    destinations_split = split_list(aeroports_destinations, nb_threads)

    # Création et démarrage des threads
    threads = []
    for i in range(nb_threads):
        thread = threading.Thread(target=process_destinations, args=(destinations_split[i],))
        threads.append(thread)
        thread.start()

    # Attente de la fin des threads
    for thread in threads:
        thread.join()

    print("Tous les traitements sont terminés.")