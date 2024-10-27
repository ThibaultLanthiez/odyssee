from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

driver_path = 'chromedriver\chromedriver.exe'  # Remplacez par le chemin réel vers chromedriver.exe
service = Service(driver_path)

url = (
    'https://www.kayak.fr/flights/'
    'LYS-FAO/'
    '2025-05-06-flexible-3days/'
    '2025-05-13-flexible-3days?'
    'fs=flexdepart=~20250506;'
    'flexreturn=~20250513;'
    'bfc=1&sort=bestflight_a'
)

driver = webdriver.Chrome(service=service)
driver.get(url)

body_element = driver.find_element(By.CLASS_NAME, 'jvgZ')
cells = body_element.find_elements(By.TAG_NAME, 'li') 

# Parcourir les cellules et cliquer dessus
for index, cell in enumerate(cells):
    print(f"Cellule {index+1} : {cell.text}")  # Affiche le texte de la cellule
    cell.find_elements(By.ID, 'FlexMatrixCell__20250510_20250503')[0].click()
    #print(cell.find_elements(By.TAG_NAME, 'div'))

    # body_element = driver.find_element(By.TAG_NAME, 'body')
    # recherche_string = body_element.text[:2000]

    # start_phrase = "Le moins cher"
    # start_index = recherche_string.find(start_phrase)
    # if start_index != -1:
    #     print(recherche_string[start_index:start_index+106])

    # Optionnel: ajouter une pause entre les clics si nécessaire
    # time.sleep(1)
    break

# Fermer le navigateur
driver.quit()