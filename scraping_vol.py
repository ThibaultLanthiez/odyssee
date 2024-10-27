import requests
from bs4 import BeautifulSoup

# URL de la page que vous souhaitez scraper
url = 'https://www.kayak.fr/flights/LYS-OSL/2025-05-03/2025-05-10?sort=bestflight_a'

# Envoyer la requête HTTP pour récupérer la page
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
response = requests.get(url, headers=headers)

# Vérifier si la requête a réussi
if response.status_code == 200:
    page_content = response.text

    # Analyser la page avec BeautifulSoup
    soup = BeautifulSoup(page_content, 'html.parser')
    print(str(soup)[:1000])



    # Exemple: Extraire tous les noms de vols affichés
    flights = soup.find_all('div', class_='root') 
    for flight in flights:
        print(flight.text)
else:
    print(f"Erreur: la requête a échoué avec le statut {response.status_code}")
