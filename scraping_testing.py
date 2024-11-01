import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from datetime import datetime, timedelta

# Configurer le service pour ChromeDriver
driver_path = 'chromedriver/130/chromedriver.exe'  # Remplacez par le chemin réel vers chromedriver.exe
service = Service(driver_path)

# Initialiser Selenium avec les options nécessaires
def start_browser():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')  # Ignorer les erreurs SSL
    return webdriver.Chrome(service=service, options=options)

# Démarrer le navigateur
driver = start_browser()

def accept_cookies(driver):
    try:
        accept_cookies_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[class="RxNS RxNS-mod-stretch RxNS-mod-variant-outline RxNS-mod-theme-base RxNS-mod-shape-default RxNS-mod-spacing-base RxNS-mod-size-small"]'))
        )
        accept_cookies_button.click()
        time.sleep(5)  # Laisser un peu de temps après l'acceptation des cookies
    except Exception as e:
        print(f"Erreur lors de l'acceptation des cookies : {e}")

def extract_price(text):
    # Utiliser une expression régulière pour trouver la première séquence de chiffres dans le texte
    match = re.search(r'\d+', text)
    if match:
        return int(match.group())  # Convertir en entier si on a trouvé un nombre
    else:
        raise ValueError("Aucun prix trouvé dans le texte fourni")
    
def find_price(driver):
    WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'g.price-box'))
        )
    price_box = driver.find_elements(By.CSS_SELECTOR, 'g.price-box')[0]
    price_text = price_box.find_element(By.CLASS_NAME, 'price').text
    print(f"Prix : {extract_price(price_text)}€")

def find_date(driver):
    # Récupérer la div de classe "day-label" qui est "selected"
    day_label = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.day-label.selected'))
    )
    data_val = day_label.get_attribute('data-val')
    print(f"Date : {data_val}")


try:
    # Ouvrir l'URL de Kayak
    url = "https://www.kayak.fr/explore/LYS-AMS/20250101,20250131?tripdurationrange=8,8"
    driver.get(url)

    accept_cookies(driver)

    # Attendre que le SVG avec la classe "graph-area" soit chargé
    svg_graph_area = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'svg.graph-area'))
    )

    # Localiser la première balise <g class="emptyBar selected"> dans le SVG de classe "graph-area"
    empty_bar_selected = svg_graph_area.find_element(By.CSS_SELECTOR, 'g.emptyBar.selected')
    empty_bar_selected.click()
    print("Clic début graphique")

    # Attendre que le bouton increase-duration soit visible
    increase_duration_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'increase-duration'))
    )
    time.sleep(3) 
    # Cliquer sur le bouton increase-duration quatre fois
    for i in range(4): # De 4 à 8
        increase_duration_button.click()
        print("Clic increase duration")

    find_date(driver)
    find_price(driver)

    counter_click = 1 
    # Variable de compteur pour chaque boucle
    while True:
        try:                
            svg_graph_area.find_elements(By.CSS_SELECTOR, 'g.bar.preselected')[0].click()
            counter_click += 1
            find_date(driver)
            find_price(driver)

            if counter_click == 14:
                counter_click = 0
                scroll_right_button = driver.find_element(By.CSS_SELECTOR, '.scroll-right')
                scroll_right_button.click()


        except Exception as e:
            scroll_right_button = driver.find_element(By.CSS_SELECTOR, '.scroll-right')
            scroll_right_button.click()
            scroll_right_button.click()
            print("Défilement vers la droite effectué. [Exception]")
            counter_click = 0
            # find_date(driver)
            # find_price(driver)

except Exception as e:
    print(f"Erreur lors du clic : {e}")

finally:
    # Fermer le navigateur
    driver.quit()
