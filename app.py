import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go

# URLs de l'API Flask
API_VOYAGE_INFO = 'http://127.0.0.1:5000/api/info_voyage'
API_DATES_URL = 'http://127.0.0.1:5000/api/dates_disponibles'
API_RESULTATS_URL = 'http://127.0.0.1:5000/api/resultats'

# Fonction pour obtenir les ID de voyage depuis l'API
def get_voyage_info():
    try:
        response = requests.get(API_VOYAGE_INFO)
        response.raise_for_status()
        
        resultats = response.json()

        if not resultats:
            st.write('Aucun résultat trouvé pour les voyages.')
            return []
        
        # Convertir les résultats en tuples (label, valeur)
        return [(f'{ligne["nom_ville"]} ({ligne["nb_jour_voyage"]} jours)', ligne['id_voyage']) for ligne in resultats]
    except requests.exceptions.RequestException as e:
        st.error(f'Erreur lors de la récupération des ID de voyage : {e}')
        return []

# Fonction pour obtenir les dates disponibles depuis l'API
def get_dates_disponibles():
    try:
        response = requests.get(API_DATES_URL)
        response.raise_for_status()
        return response.json()  # On suppose que cela renvoie une liste de dates sous forme de chaînes
    except requests.exceptions.RequestException as e:
        st.error(f'Erreur lors de la récupération des dates : {e}')
        return []

# Interface utilisateur Streamlit
st.title('Calcul du Prix du Voyage')

# Récupération des ID de voyage distincts pour la liste déroulante
voyage_ids = get_voyage_info()
if voyage_ids:
    id_voyage_label, id_voyage = st.selectbox(
        'Sélectionnez l\'ID du voyage',
        voyage_ids,
        format_func=lambda x: x[0]  # Affiche uniquement le label
    )
else:
    id_voyage = None

# Récupération des dates disponibles pour la liste déroulante
dates_disponibles = get_dates_disponibles()
if dates_disponibles:
    date_premier_jour = st.selectbox('Sélectionnez la date du premier jour', dates_disponibles)
else:
    date_premier_jour = None

# Liste déroulante pour le nombre de personnes
nb_personne = st.selectbox('Sélectionnez le nombre de personnes', list(range(1, 7)))

# Bouton pour exécuter la requête
if st.button('Calculer le Prix'):
    if id_voyage and date_premier_jour:
        try:
            # Effectuer la requête GET à l'API Flask
            response = requests.get(API_RESULTATS_URL, params={
                'nb_personne': nb_personne,
                'id_voyage': id_voyage,
                'date_premier_jour': date_premier_jour
            })
            response.raise_for_status()
            
            resultats = response.json()

            if not resultats:
                st.write('Aucun résultat trouvé.')
            else:
                for ligne in resultats:
                    total = ligne['total']
                    logement = ligne['logement']
                    vol = ligne['vol']
                    voiture = ligne['voiture']

                    # Mise en page améliorée
                    st.header('Résultats du Calcul')
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label='Total par personne', value=f'{total}€')
                    with col2:
                        fig = go.Figure(
                            data=[
                                go.Pie(
                                    labels=['Logement', 'Vol', 'Voiture'],
                                    values=[logement, vol, voiture],
                                    textinfo='label+value',  # Afficher label et valeur
                                    texttemplate='%{label}: %{value}€',  # Format de texte avec € après les valeurs
                                    insidetextorientation='horizontal',  # Orientation du texte
                                    hole=0.2  # Ajouter un trou au centre pour un effet donut (optionnel)
                                )
                            ]
                        )

                        # Mise à jour de la mise en page pour enlever la légende
                        fig.update_layout(
                                showlegend=False,  # Désactiver la légende
                                margin=dict(t=50, b=50, l=50, r=50),  # Marges autour du graphique
                                width=400,  # Largeur du graphique
                                height=400  # Hauteur du graphique
                        )
                    
                    
                    # Affichage du graphique
                    st.plotly_chart(fig)
        except requests.exceptions.RequestException as e:
            st.write(f'Erreur lors de la récupération des résultats : {e}')
    else:
        st.write('Veuillez sélectionner un ID de voyage et une date.')
