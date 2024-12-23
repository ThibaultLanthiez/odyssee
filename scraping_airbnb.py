from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configurer Selenium
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
service = Service('chromedriver/130/chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

# Liste des URLs à interroger
date_check_in = '2025-01-01'
date_check_out = '2025-01-07'
urls = [
    f"https://www.airbnb.fr/rooms/659198879972604993?adults=1&check_in={date_check_in}&check_out={date_check_out}",
    f"https://www.airbnb.fr/rooms/1060097329998675531?adults=1&check_in={date_check_in}&check_out={date_check_out}"
]

try:
    for index, url in enumerate(urls):
        print(f"Chargement de l'URL : {url}")
        driver.get(url)
        time.sleep(5)  # Attente pour le chargement de la page

        if index == 0:  # Exécuter seulement pour la première URL
            # Fermer la traduction
            try:
                translation_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Fermer"]'))
                )
                translation_button.click()
                print("Le bouton 'translation_button' a été cliqué")
            except Exception:
                print("Aucun bouton de traduction trouvé")

            time.sleep(2)

            # Accepter les cookies
            try:
                accept_cookies_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accepter tout')]"))
                )
                accept_cookies_button.click()
                print("Le bouton 'accept_cookies_button' a été cliqué.")
            except Exception:
                print("Aucun bouton de cookies trouvé")

        time.sleep(2)

        # Trouver et afficher le prix total
        try:
            price_element = driver.find_element(By.CSS_SELECTOR, 'div[data-section-id="BOOK_IT_SIDEBAR"]')
            total_price = price_element.text.split('Total')[-1].strip()
            if len(total_price) < 8:
                print(f"Prix total trouvé : {total_price}")
            else :
                print("Ces dates ne sont pas disponibles")
        except Exception:
            print("Impossible de trouver le prix total.")

        print("-------")

except Exception as e:
    print("Une erreur s'est produite :", e)

finally:
    driver.quit()
