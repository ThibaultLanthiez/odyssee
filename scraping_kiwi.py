from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time 
from datetime import datetime, timedelta
import re
import pandas as pd

global_index = 0

# Configurer le service pour ChromeDriver
driver_path = 'chromedriver/chromedriver.exe'  # Remplacez par le chemin réel vers chromedriver.exe
service = Service(driver_path)

# Configurer le navigateur avec Selenium
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # Exécuter en arrière-plan sans interface graphique

# Démarrer le navigateur
driver = webdriver.Chrome(service=service, options=options)

def get_data(date_depart, aeroport_depart, aeroport_destination, nb_jours_voyage = 7, nb_month = 1, cookie=False):

    date_depart_type_date = datetime.strptime(date_depart, "%Y-%m-%d")
    date_retour_type_date = date_depart_type_date + timedelta(days=nb_jours_voyage)

    date_depart = date_depart_type_date.strftime("%Y-%m-%d")
    date_retour = date_retour_type_date.strftime("%Y-%m-%d")

    url = (
        "https://www.kiwi.com/fr/search/results"
        f"/{aeroport_depart}"
        f"/{aeroport_destination}"
        f"/{date_depart}"
        f"/{date_retour}"
        "?bags=1.0")
    driver.get(url)


    try:
        if cookie:
            # Attendre que le bouton d'acceptation des cookies soit cliquable et cliquer dessus
            accept_cookies_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-test="CookiesPopup-Accept"]')) 
                # Sélecteur basé sur data-test
            )
            accept_cookies_button.click()
            # print("Cookies acceptés")

        time.sleep(1)

        # Attendre que le bouton d'acceptation des cookies soit cliquable et cliquer dessus
        # Cliquer sur le bouton 'Tendances des prix'
        trends_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Tendances des prix']"))
        )
        trends_button.click()
        # print("Bouton 'Tendances des prix' cliqué")

        time.sleep(7)

        # Attendre que le wrapper des éléments PriceGraph soit visible
        price_columns = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-test="PriceGraphWrapper"]'))
        )
        data = price_columns.get_attribute('innerText')

        lines_with_prices = []
        # Séparer la chaîne en lignes
        lines = data.strip().split('\n')
        start_index = find_first_index_with_dot(lines)
        lines_with_prices+=lines[start_index:] # 5 premières valeurs sont des mois inutiles

        for _ in range(4*nb_month):
            next_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-test="priceGraphArrowRight"]'))
            )
            for _ in range(2):
                next_button.click()
                # print("Bouton 'Suivant' cliqué")

            time.sleep(7)

            # Attendre que le wrapper des éléments PriceGraph soit visible
            price_columns = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-test="PriceGraphWrapper"]'))
            )
            data = price_columns.get_attribute('innerText')

            # Séparer la chaîne en lignes
            lines = data.strip().split('\n')
            start_index = find_first_index_with_dot(lines)
            lines_with_prices+=lines[start_index:] # 5 premières valeurs sont des mois inutiles

        return lines_with_prices

    except Exception as e:
        print(f"Erreur lors de la récupération des prix : {e}")

def find_first_index_with_dot(lines):
    for index, line in enumerate(lines):
        if '.' in line:  # Vérifier si la ligne contient un point
            return index  # Retourner l'index de la première occurrence
    return -1  # Retourner -1 si aucun point n'est trouvé

def format_data(data):
    formatted_results = []
    i = 0
    while i + 3 < len(data):
        price, day, date, month = data[i:i + 4]
        day_without_dot = day[:-1]
        month_without_dot = month[:-1]

        # Vérifier si le prix est valide et si le jour et le mois sont des strings
        if price.isdigit() and isinstance(day, str) and isinstance(month, str):
            # Ajouter à la liste des résultats
            formatted_results.append(f"{day_without_dot} {date} {month_without_dot} : {price}€")
            i += 4
        else:
            i += 3

    return formatted_results

def generate_dates(start_date_str):
    # Convertir la chaîne de caractères en objet date
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    # Générer les dates espacées
    #return [(start_date + timedelta(days=i * spacing_days)).strftime("%Y-%m-%d") for i in range(num_dates)]
    return [start_date.strftime("%Y-%m-%d")]

def print_all_prices(results):
    for result in results:
        print(result)

trans_int_to_month = {
    "01":"janv",
    "02":"févr",
    "03":"mar",
    "04":"avr",
    "05":"ma",
    "06":"jui"
}

def get_min_price(results, mois_principal):
    min_price_line = None
    min_price = float('inf')  # Utiliser l'infini pour pouvoir comparer

    # Parcourir chaque ligne de données
    for result in results:
        # Extraire le prix en retirant le symbole '€' et le convertissant en entier
        price_str = result.split(': ')[1].replace('€', '')
        price = int(price_str)  # Convertir en entier

        mois = result.split(': ')[0].split(" ")[2]
        
        # Vérifier si le prix est le plus bas trouvé jusqu'à présent
        if (price < min_price) and (mois == mois_principal):
            min_price = price
            min_price_line = result  # Mémoriser la ligne correspondante

    return min_price_line


list_nb_jours = [7,10,14]
list_months = ["01","02","03","04","05","06"]
list_aeroports = [
    "aeroport-de-paris-charles-de-gaulle-paris-france,aeroport-de-paris-orly-paris-france",
    "aeroport-de-lyon-saint-exupery-lyon-france",
    "aeroport-marseille-provence-marseille-france",
    "aeroport-de-nice-cote-d-azur-nice-france",
    "aeroport-de-bordeaux-merignac-bordeaux-france",
    "aeroport-de-nantes-atlantique-nantes-france",
    "aeroport-de-lille-lesquin-lille-france"
]
aeroport_destination = "aeroport-de-l-ile-de-mykonos-mykonos-grece"
# "aeroport-d-amsterdam-schiphol-amsterdam-pays-bas"
#"aeroport-de-londres-gatwick-londres-royaume-uni,aeroport-de-londres-heathrow-londres-royaume-uni,aeroport-de-londres-luton-londres-royaume-uni,aeroport-de-londres-city-londres-royaume-uni,aeroport-de-londres-southend-londres-royaume-uni" 
#"seychelles-international-mahe-seychelles"
accept_cookies = True
final_print_bilan = []

for aeroport_depart in list_aeroports:
    list_min_price_lines_global = []
    for nb_jours_voyage in list_nb_jours:
        list_min_price_lines = []

        date_debut_recherche = f"2025-{list_months[0]}-01"
        # Obtenir et afficher les résultats pour toutes les dates
        results = format_data(get_data(date_debut_recherche, aeroport_depart, aeroport_destination, nb_jours_voyage, len(list_months), accept_cookies))
        accept_cookies = False

        # print_all_prices(results)
        for month in list_months:
            list_min_price_lines.append(get_min_price(results, trans_int_to_month[month]))
        
        list_min_price_lines_global.append(list_min_price_lines)

    final_print_bilan.append("_____________________")
    final_print_bilan.append(aeroport_depart)
    for line_bilan, nb_jours_voyage in zip(list_min_price_lines_global, list_nb_jours):
        final_print_bilan.append(f"Bilan pour voyage de {nb_jours_voyage} jours:")
        for line in line_bilan:
            final_print_bilan.append(line)
    
    print(aeroport_depart)
    voyage_7j = {}
    voyage_10j = {}
    voyage_14j = {}
    current_voyage = None
    for line in final_print_bilan:
        if "7 jours" in line:
            current_voyage = voyage_7j
        elif "10 jours" in line:
            current_voyage = voyage_10j
        elif "14 jours" in line:
            current_voyage = voyage_14j
        else:
            # Extraction de la date et du prix avec une regex
            match = re.search(r'(\d{1,2}) (\w+) : (\d+)€', line)
            if match:
                jour, mois, prix = match.groups()
                current_voyage[mois] = prix + "€"  # Ajouter le symbole € après le prix
    df = pd.DataFrame({
        '7 jours': pd.Series(voyage_7j),
        '10 jours': pd.Series(voyage_10j),
        '14 jours': pd.Series(voyage_14j)
    })
    mois_order = ['janv', 'févr', 'mar', 'avr', 'ma', 'jui']
    df = df.reindex(mois_order)
    output = df.apply(lambda row: f"{row['7 jours']}                {row['10 jours']}                {row['14 jours']}", axis=1)
    print("\n".join(output.values))

# for line in final_print_bilan:
#     print(line)


# Fermer le navigateur
driver.quit()