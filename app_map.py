import streamlit as st
import sqlite3
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from datetime import datetime

# Titre de l'application
st.title("Carte des vols les moins chers par mois")

# Chemin vers votre base de données SQLite
db_path = 'odyssee.db'

# Récupérer la date du jour
current_date = datetime.now().strftime('%Y-%m-%d')

# Fonction pour récupérer les mois disponibles
def get_available_months():
    with sqlite3.connect(db_path) as conn:
        query = f"""
        SELECT DISTINCT strftime('%Y-%m', date_aller) AS mois_annee
        FROM vol
        WHERE date_aller > date('{current_date}')
        ORDER BY mois_annee;
        """
        months_df = pd.read_sql_query(query, conn)
    return months_df['mois_annee'].tolist()

# Coordonnées des aéroports
airport_coordinates = {
    "Lyon": {"latitude": 45.7277, "longitude": 5.0908},
    "Amsterdam Schiphol": {"latitude": 52.3105, "longitude": 4.7683},
    "Marseille-Provence": {"latitude": 43.4356, "longitude": 5.2134},
    "Tous les aéroports de Paris": {"latitude": 48.8566, "longitude": 2.3522},
    "Nice Côte d'Azur": {"latitude": 43.6654, "longitude": 7.2159},
    "Bordeaux Mérignac": {"latitude": 44.8283, "longitude": -0.7156},
    "Nantes Atlantique": {"latitude": 47.156, "longitude": -1.608},
    "Lille Lesquin": {"latitude": 50.5619, "longitude": 3.0894},
    "Tous les aéroports de Montréal": {"latitude": 45.5017, "longitude": -73.5673},
    "Tous les aéroports de Bangkok": {"latitude": 13.7563, "longitude": 100.5018},
    "Tous les aéroports de Londres": {"latitude": 51.5074, "longitude": -0.1278},
    "Dublin": {"latitude": 53.4273, "longitude": -6.2436},
    "Mykonos": {"latitude": 37.4467, "longitude": 25.3289},
    "Réunion Roland Garros": {"latitude": -20.8871, "longitude": 55.5103},
    "Le Caire": {"latitude": 30.0444, "longitude": 31.2357},
    "Lisbonne Humberto Delgado": {"latitude": 38.7742, "longitude": -9.1342},
    "Tous les aéroports de Venise": {"latitude": 45.4408, "longitude": 12.3155},
    "Split": {"latitude": 43.5081, "longitude": 16.4402},
    "Casablanca Mohammed V": {"latitude": 33.3675, "longitude": -7.5898},
    "Genève-Cointrin": {"latitude": 46.232, "longitude": 6.108},
    "Tous les aéroports d'Oslo": {"latitude": 59.9115, "longitude": 10.7579},
    "Tous les aéroports de Stockholm": {"latitude": 59.3293, "longitude": 18.0686},
    "Tous les aéroports d'Istanbul": {"latitude": 41.0082, "longitude": 28.9784},
    "Helsinki-Vantaa": {"latitude": 60.3172, "longitude": 24.9633},
    "Guadeloupe - Pointe-à-Pitre Le Raizet": {"latitude": 16.265, "longitude": -61.527},
    "Édimbourg": {"latitude": 55.9533, "longitude": -3.1883},
    "Osaka": {"latitude": 34.6937, "longitude": 135.5023},
    "Copenhague Kastrup": {"latitude": 55.6181, "longitude": 12.656},
    "Madrid-Barajas": {"latitude": 40.4983, "longitude": -3.5676},
    "Vienne-Schwechat": {"latitude": 48.1103, "longitude": 16.5697},
    "Tous les aéroports de Varsovie": {"latitude": 52.2297, "longitude": 21.0122},
    "Berlin Brandebourg": {"latitude": 52.3667, "longitude": 13.5033},
    "Tous les aéroports de Rome": {"latitude": 41.9028, "longitude": 12.4964},
    "Sardaigne Cagliari-Elmas": {"latitude": 39.2238, "longitude": 9.1121},
    "Malaga": {"latitude": 36.7213, "longitude": -4.4214},
    "Palma de Majorque": {"latitude": 39.5712, "longitude": 2.6466},
    "Tous les aéroports de Reykjavik": {"latitude": 64.1355, "longitude": -21.8954},
    "Toulouse Blagnac": {"latitude": 43.6293, "longitude": 1.3641},
    "Vilnius": {"latitude": 54.6872, "longitude": 25.2797},
    "Riga": {"latitude": 56.9496, "longitude": 24.1052},
    "Tallinn": {"latitude": 59.437, "longitude": 24.7536},
    "Malte": {"latitude": 35.8997, "longitude": 14.5146},
    "Larnaca": {"latitude": 34.9011, "longitude": 33.6232},
    "Palerme Falcone-Borsellino": {"latitude": 38.1758, "longitude": 13.0913},
}

# Fonction pour récupérer les données pour la carte
def get_map_data(selected_month):
    with sqlite3.connect(db_path) as conn:
        query = f"""
        SELECT 
            aeroport.nom_aeroport AS ville, 
            MIN(vol.prix_vol) AS prix_minimum
        FROM vol
        JOIN aeroport ON vol.id_aeroport_destination = aeroport.id_aeroport
        WHERE strftime('%Y-%m', vol.date_aller) = '{selected_month}'
        GROUP BY aeroport.nom_aeroport;
        """
        df = pd.read_sql_query(query, conn)
    
    # Vérifier les coordonnées et ajouter les colonnes latitude/longitude
    def get_coordinates(ville):
        if ville in airport_coordinates:
            return airport_coordinates[ville]["latitude"], airport_coordinates[ville]["longitude"]
        return None, None

    df['latitude'], df['longitude'] = zip(*df['ville'].apply(get_coordinates))
    df = df.dropna(subset=['latitude', 'longitude'])  # Supprimer les villes sans coordonnées
    
    return df

# Récupérer les mois disponibles pour la sélection
available_months = get_available_months()
selected_month = st.selectbox(
    "Sélectionnez le mois à afficher",
    options=available_months,
    format_func=lambda x: datetime.strptime(x, "%Y-%m").strftime("%B %Y")
)

# Récupérer les données pour le mois sélectionné
if selected_month:
    map_data = get_map_data(selected_month)
    
    if map_data.empty:
        st.warning("Aucune donnée ou les coordonnées GPS des destinations sont manquantes pour le mois sélectionné.")
    else:
        st.write(f"### Carte des vols pour {selected_month}")
        
        # Créer une carte Folium centrée sur la moyenne des latitudes et longitudes
        m = folium.Map(location=[map_data['latitude'].mean(), map_data['longitude'].mean()], zoom_start=5)

        # Ajouter un cluster de marqueurs
        marker_cluster = MarkerCluster().add_to(m)

        # Ajouter des marqueurs pour chaque destination avec un popup contenant le prix minimum et couleur en fonction du prix
        for _, row in map_data.iterrows():
            if row['prix_minimum'] <= 100:
                marker_color = "green"  # Prix entre 0 et 100 €
            elif row['prix_minimum'] <= 200:
                marker_color = "orange"  # Prix entre 100 et 200 €
            else:
                marker_color = "red"  # Prix au-delà de 200 €

            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"{row['ville']} - {row['prix_minimum']} €",
                icon=folium.Icon(color=marker_color)
            ).add_to(marker_cluster)

        # Afficher la carte
        st.components.v1.html(m._repr_html_(), height=600)

        # Afficher les données sous forme de tableau
        st.write("### Détails des vols pour le mois sélectionné")
        st.dataframe(map_data)
