import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time

# Configurer Selenium
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
service = Service('chromedriver/130/chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

# Configurer SQLite
conn = sqlite3.connect('odyssee.db')
cursor = conn.cursor()


def get_or_create_ville(nom_ville):
    cursor.execute("SELECT id_ville FROM ville WHERE nom_ville = ?", (nom_ville,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("SELECT COALESCE(MAX(id_ville), 0) + 1 FROM ville")
    new_id_ville = cursor.fetchone()[0]
    cursor.execute("INSERT INTO ville (id_ville, nom_ville) VALUES (?, ?)", (new_id_ville, nom_ville))
    conn.commit()
    return new_id_ville

def get_or_create_logement(id_ville, lien_logement, nb_pers_max):
    cursor.execute("SELECT id_logement FROM logement WHERE lien_logement = ?", (lien_logement,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("SELECT COALESCE(MAX(id_logement), 0) + 1 FROM logement")
    new_id_logement = cursor.fetchone()[0]
    cursor.execute("INSERT INTO logement (id_logement, id_ville, lien_logement, nb_pers_max) VALUES (?, ?, ?, ?)",
                   (new_id_logement, id_ville, lien_logement, nb_pers_max))
    conn.commit()
    return new_id_logement

def insert_or_update_dispo_logement(id_logement, date_premiere_nuit, nb_nuit, prix_total):
    cursor.execute("SELECT 1 FROM dispo_logement WHERE id_logement = ? AND date_premiere_nuit = ? AND nb_nuit = ?",
                   (id_logement, date_premiere_nuit, nb_nuit))
    exists = cursor.fetchone()
    if exists:
        cursor.execute("""UPDATE dispo_logement 
                          SET prix_total = ? 
                          WHERE id_logement = ? AND date_premiere_nuit = ? AND nb_nuit = ?""",
                       (prix_total, id_logement, date_premiere_nuit, nb_nuit))
    else:
        cursor.execute("""INSERT INTO dispo_logement (id_logement, date_premiere_nuit, nb_nuit, prix_total) 
                          VALUES (?, ?, ?, ?)""",
                       (id_logement, date_premiere_nuit, nb_nuit, prix_total))
    conn.commit()

def delete_dispo_logement(id_logement, date_premiere_nuit):
    cursor.execute("DELETE FROM dispo_logement WHERE id_logement = ? AND date_premiere_nuit = ?",
                   (id_logement, date_premiere_nuit))
    conn.commit()

# Générer les paires de dates d'arrivée et de départ pour les 30 prochains jours
def generate_date_ranges(nb_days):
    today = datetime.now()
    date_ranges = []
    for i in range(30):
        check_in = today + timedelta(days=i)
        check_out = check_in + timedelta(days=nb_days)
        date_ranges.append((check_in.strftime('%Y-%m-%d'), check_out.strftime('%Y-%m-%d')))
    return date_ranges

def handle_initial_popups():
    """Gérer les popups comme la traduction et les cookies."""
    try:
        translation_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Fermer"]'))
        )
        translation_button.click()
    except Exception:
        pass

    time.sleep(2)

    try:
        accept_cookies_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accepter tout')]")
        ))
        accept_cookies_button.click()
    except Exception:
        pass

def fetch_price():
    """Extraire et afficher le prix total ou signaler l'indisponibilité."""
    try:
        time.sleep(3)
        price_element = WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-section-id="BOOK_IT_SIDEBAR"]'))
                )        
        total_price = price_element.text.split('Total')[-1].strip()
        return int(total_price.replace('\u202f', '').replace('\xa0', '').replace('€', '').strip())
    except Exception:
        return None

# Exécuter le scraping
def main():

    id_ville = get_or_create_ville("Rome")
    lien_logement = "https://www.airbnb.fr/rooms/1081988723303637094"
    nb_pers = 2
    id_logement = get_or_create_logement(id_ville, lien_logement, nb_pers)

    nb_days = 7
    date_ranges = generate_date_ranges(nb_days)

    for check_in, check_out in date_ranges:
        url = f"{lien_logement}?adults={nb_pers}&check_in={check_in}&check_out={check_out}"
        driver.get(url)

        if date_ranges.index((check_in, check_out)) == 0:
            handle_initial_popups()

        total_price = fetch_price()
        if total_price:
            insert_or_update_dispo_logement(id_logement, check_in, nb_days, total_price)
            print(f"Prix pour les dates {check_in} au {check_out} : {total_price}")
        else:
            delete_dispo_logement(id_logement, check_in)
            print(f"Aucun prix disponible pour les dates {check_in} au {check_out}.")

    driver.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Une erreur s'est produite :", e)
        driver.quit()
        conn.close()
