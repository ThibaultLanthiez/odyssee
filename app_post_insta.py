import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Titre de l'application
st.title("Prix minimum par mois et durée de voyage avec sélection d'aéroport et de mois")

# Chemin vers votre base de données SQLite
db_path = 'odyssee.db'

# Liste d'aéroports spécifiques pour le départ
departure_airports = [
    (9, "Tous les aéroports de Paris"),
    (7, "Marseille-Provence"),
    (2, "Lyon"),
    (25, "Genève-Cointrin"),
    (10, "Nice Côte d'Azur"),
    (11, "Bordeaux Mérignac"),
    (12, "Nantes Atlantique"),
    (13, "Lille Lesquin"),
    (43, "Toulouse Blagnac")
]

# Convertir la liste des aéroports de départ en DataFrame pour faciliter la gestion
departure_airports_df = pd.DataFrame(departure_airports, columns=["id_aeroport", "nom_aeroport"])

# Créer un menu déroulant pour sélectionner l'aéroport de départ
selected_departure_airport = st.selectbox(
    "Sélectionnez l'aéroport de départ",
    options=departure_airports_df['id_aeroport'],
    format_func=lambda x: departure_airports_df.loc[departure_airports_df['id_aeroport'] == x, 'nom_aeroport'].values[0]
)

# Fonction pour récupérer tous les aéroports pour les destinations, excluant les aéroports de départ
def get_destination_airports(departure_airport_ids):
    with sqlite3.connect(db_path) as conn:
        query = f"""
        SELECT id_aeroport, nom_aeroport FROM aeroport
        WHERE id_aeroport NOT IN ({','.join(map(str, departure_airport_ids))})
        """
        airports_df = pd.read_sql_query(query, conn)
    return airports_df

# Récupérer la liste filtrée des aéroports pour la destination
destination_airports_df = get_destination_airports(departure_airports_df['id_aeroport'].tolist())

# Créer un menu déroulant pour sélectionner l'aéroport de destination à partir de la liste filtrée
selected_destination_airport = st.selectbox(
    "Sélectionnez l'aéroport de destination",
    options=destination_airports_df['id_aeroport'],
    format_func=lambda x: destination_airports_df.loc[destination_airports_df['id_aeroport'] == x, 'nom_aeroport'].values[0]
)

# Récupérer la date du jour
current_date = datetime.now().strftime('%Y-%m-%d')

# Fonction pour récupérer les mois disponibles dans les résultats de la requête
def get_available_months(departure_airport_id, destination_airport_id):
    with sqlite3.connect(db_path) as conn:
        query = f"""
        SELECT DISTINCT strftime('%Y-%m', date_aller) AS mois_annee
        FROM vol
        WHERE
            id_aeroport_depart = {departure_airport_id}
            AND id_aeroport_destination = {destination_airport_id}
            AND date_aller > date('{current_date}')
        ORDER BY mois_annee;
        """
        months_df = pd.read_sql_query(query, conn)
    return months_df['mois_annee'].tolist()

# Récupérer les mois disponibles pour la sélection
available_months = get_available_months(selected_departure_airport, selected_destination_airport)
selected_months = st.multiselect(
    "Sélectionnez les mois à inclure",
    options=available_months,
    default=available_months
)

# Fonction pour exécuter la requête et récupérer les données
def fetch_data(departure_airport_id, destination_airport_id, selected_months):
    with sqlite3.connect(db_path) as conn:
        # Convertir la liste de mois sélectionnés en chaîne pour la requête SQL
        selected_months_str = ', '.join([f"'{month}'" for month in selected_months])
        
        query = f"""
        SELECT
            strftime('%Y-%m', date_aller) AS mois_annee,
            MIN(prix_vol) AS prix_minimum,
            date_aller,
            date_retour,
            CASE
                WHEN julianday(date_retour) - julianday(date_aller) = 7 THEN 7
                WHEN julianday(date_retour) - julianday(date_aller) = 10 THEN 10
                WHEN julianday(date_retour) - julianday(date_aller) = 14 THEN 14
                ELSE 'Autre'
            END AS duree_voyage
        FROM
            vol
        WHERE
            id_aeroport_depart = {departure_airport_id}
            AND id_aeroport_destination = {destination_airport_id}
            AND (julianday(date_retour) - julianday(date_aller)) IN (7, 10, 14)
            AND date_aller > date('{current_date}')
            AND strftime('%Y-%m', date_aller) IN ({selected_months_str})
        GROUP BY
            strftime('%Y-%m', date_aller),
            duree_voyage
        ORDER BY
            duree_voyage, 
            date_aller;
        """
        # Exécuter la requête et charger les résultats dans un DataFrame
        df = pd.read_sql_query(query, conn)
    return df

# Exécuter la requête et afficher les résultats si les aéroports et mois sont sélectionnés
if selected_departure_airport and selected_destination_airport and selected_months:
    data = fetch_data(selected_departure_airport, selected_destination_airport, selected_months)

    if data.empty:
        st.warning("Aucune donnée ne correspond aux critères spécifiés.")
    else:
        # Afficher le premier tableau avec toutes les colonnes, y compris les dates
        st.write("### Résultats de la requête SQL")
        st.dataframe(data)

        # Calcul de la moyenne de la colonne `prix_minimum`
        moyenne_prix_minimum = round(data['prix_minimum'].mean())
        st.write(f"**Moyenne du prix minimum :** {moyenne_prix_minimum} €")

        # Créer un tableau formaté pour afficher les prix minimums par durée de voyage
        st.write("### Tableau des prix minimums par durée de voyage")
        
        # Pivot des données pour exclure les dates et afficher uniquement le mois et les prix par durée
        formatted_table = data.pivot_table(index="mois_annee", columns="duree_voyage", values="prix_minimum", aggfunc='min')
        
        # Réorganiser les colonnes pour s'assurer que l'ordre soit correct
        formatted_table = formatted_table[[7, 10, 14]].fillna("-")  # Assurer que les colonnes sont dans le bon ordre et combler les valeurs manquantes
        formatted_table = formatted_table.rename(columns={7: '7 jours', 10: '10 jours', 14: '14 jours'})  # Renommer les colonnes
        
        # Afficher le tableau avec 3 colonnes distinctes : 7 jours, 10 jours, 14 jours
        st.dataframe(formatted_table)
