from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Chemin vers le ChromeDriver téléchargé
driver_path = 'chromedriver\chromedriver.exe'  # Remplacez par le chemin réel vers chromedriver.exe

# Configurer Selenium avec ChromeDriver
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service(driver_path), options=options)

# Naviguer vers l'URL cible
url = "https://www.kayak.fr/flights/LYS-OSL/2025-05-03/2025-05-10?sort=bestflight_a"
driver.get(url)

# Attendre que la page soit complètement chargée
time.sleep(5)  # Vous pouvez ajuster ce délai si nécessaire

# Exemple pour trouver un élément par son XPath (à ajuster selon vos besoins)
# flights = driver.find_elements(By.XPATH, '//div[@class="some-class"]')

# Extraire des informations spécifiques
# for flight in flights:
#     print(flight.text)  # Ou toute autre opération de traitement des données

# Fermer le driver
driver.quit()
