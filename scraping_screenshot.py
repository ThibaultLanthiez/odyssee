import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time

# Fonction pour extraire les prix
def extract_prices(text):
    # Convertir le texte en une liste de mots
    words = text.split()
    for i, word in enumerate(words):
        if word.endswith('€'):
            # Ajouter le prix à la liste si le mot se termine par €
            return words[i-1]  # Retourne le montant du prix
    return None

# Fonction pour scraper les données
def scrape_data(num_days, delta_jours, start_month, scraping=False):
    # Chemin vers le ChromeDriver ou autre driver
    driver_path = 'chromedriver\chromedriver.exe'  # Remplacez par le chemin réel vers chromedriver.exe
    service = Service(driver_path)

    # Date de départ initiale
    # Modifier l'année pour la date de départ initiale et le mois basé sur le choix de l'utilisateur
    date_debut_initiale = datetime(2025, start_month, 1)

    results = []

    # Créer un objet de barre de progression
    progress_bar = st.progress(0)

    # Générer et afficher les paires de dates de début et de fin
    for i in range(num_days):
        # Mettre à jour la barre de progression
        progress = (i + 1) / num_days
        progress_bar.progress(progress)

        # Calculer la date de début
        date_debut = date_debut_initiale + timedelta(days=i)

        # Calculer la date de fin en ajoutant delta_jours à la date de début
        date_fin = date_debut + timedelta(days=delta_jours)

        # Formater les dates en chaîne de caractères
        date_debut_str = date_debut.strftime('%Y-%m-%d')
        date_fin_str = date_fin.strftime('%Y-%m-%d')

        # URL que vous voulez ouvrir (par exemple, Kayak)
        url = (
            'https://www.kayak.fr/flights/'
                'LYS-'  # Aeroport départ
                'FUK,HND,OSA/'  # Aeroport destination
                f'{date_debut_str}/'  # Date allé
                f'{date_fin_str}'  # Date retour
            '?sort='
                'price_a&'  # Prix croissant
                'fs=cfc=1'  # 1 bagage cabine
        )

        results.append((url, f'{date_debut_str} au {date_fin_str}'))

        if scraping:
            try:
                # Démarrer le navigateur
                driver = webdriver.Chrome(service=service)
                driver.get(url)

                time.sleep(4)

                # Trouver un élément par exemple par son tag <body> et afficher son contenu texte
                body_element = driver.find_element(By.TAG_NAME, 'body')
                recherche_string = body_element.text[:2000]

                start_phrase = "Le moins cher"
                start_index = recherche_string.find(start_phrase)
                if start_index != -1:
                    substring = recherche_string[start_index:start_index+106]
                    
                    # Extraire les prix
                    price = extract_prices(substring)
                    if price:
                        results[-1] = (results[-1][0], results[-1][1], price)
                    else:
                        results[-1] = (results[-1][0], results[-1][1], "Aucun prix trouvé")
                else:
                    results[-1] = (results[-1][0], results[-1][1], "Impossible de trouver la sous-chaîne")
            
            finally:
                # Fermer le navigateur
                driver.quit()
        
        # Assurer que la barre de progression atteint 100%
        progress_bar.progress(1.0)

        if scraping:
            # Trier les résultats par prix (le dernier élément du tuple)
            def parse_price(price):
                try:
                    if "€" in price:
                        return int(price.split()[0].replace(',', ''))
                    return float('inf')
                except:
                    return float('inf')

            results.sort(key=lambda x: parse_price(x[2]))
    
    return results

# Configuration de l'application Streamlit
st.title('Scraper Kayak')
st.write('Entrez le nombre de jours pour générer les paires de dates.')

# Paramètre modifiable pour le nombre de jours
num_days = st.slider('Nombre de jours pour les dates', min_value=1, max_value=31, value=31)

# Paramètre modifiable pour delta_jours
delta_jours = st.slider('Nombre de jours entre départ et retour', min_value=1, max_value=30, value=7)

# Paramètre modifiable pour le mois
months = {
    "Janvier": 1,
    "Février": 2,
    "Mars": 3,
    "Avril": 4,
    "Mai": 5,
    "Juin": 6,
    "Juillet": 7,
    "Août": 8,
    "Septembre": 9,
    "Octobre": 10,
    "Novembre": 11,
    "Décembre": 12
}
selected_month = st.selectbox('Sélectionnez le mois', list(months.keys()))
start_month = months[selected_month]

if st.button('Lancer le scraping'):
    with st.spinner('Scraping en cours...'):
        results = scrape_data(num_days, delta_jours, start_month, False)
        st.success('Scraping terminé!')

    for url, dates in results:
        st.write(f"URL: {url}")
        st.write(f"Date: {dates}")
        #st.write(f"Prix: {price}")
        st.write('---')
