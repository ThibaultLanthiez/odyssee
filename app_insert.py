import streamlit as st
import sqlite3
from datetime import date, timedelta

# Connexion à la base de données SQLite
conn = sqlite3.connect('odyssee.db')
cursor = conn.cursor()

# Fonction pour récupérer les voitures
def fetch_voitures(id_aeroport):
    cursor.execute("""
        SELECT id_voiture, lien_voiture, nb_pers_max, fournisseur, description, modele_voiture 
        FROM voiture 
        WHERE id_aeroport = ?
    """, (id_aeroport,))
    return cursor.fetchall()

# Fonction pour ajouter une voiture
def add_voiture(id_aeroport, lien_voiture, nb_pers_max, fournisseur, description, modele_voiture):
    # Récupérer le prochain id_voiture
    cursor.execute("SELECT IFNULL(MAX(id_voiture), 0) + 1 FROM voiture")
    prochain_id_voiture = cursor.fetchone()[0]

    # Insérer la nouvelle voiture dans la base de données
    cursor.execute("""
        INSERT INTO voiture (id_voiture, id_aeroport, lien_voiture, nb_pers_max, fournisseur, description, modele_voiture)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (prochain_id_voiture, id_aeroport, lien_voiture, nb_pers_max, fournisseur, description, modele_voiture))
    conn.commit()

# Fonction pour supprimer une voiture
def delete_voiture(id_voiture):
    cursor.execute("DELETE FROM voiture WHERE id_voiture = ?", (id_voiture,))
    conn.commit()

# Fonction pour obtenir les informations d'une voiture par son ID
def get_voiture_info(id_voiture):
    cursor.execute("""
        SELECT lien_voiture, nb_pers_max, fournisseur, description, modele_voiture
        FROM voiture
        WHERE id_voiture = ?
    """, (id_voiture,))
    return cursor.fetchone()

# Initialisation du session_state pour les voitures et l'aéroport_id
if 'voitures' not in st.session_state:
    st.session_state.voitures = []
if 'aeroport_id' not in st.session_state:
    st.session_state.aeroport_id = None

# Requête pour récupérer les informations de l'aéroport avec id_aeroport = 2
cursor.execute("""
    SELECT id_aeroport, nom_aeroport, code_iata, descriptif_aeroport
    FROM aeroport
    WHERE id_aeroport = 2
""")
aeroports_depart = cursor.fetchall()

if aeroports_depart:
    # Créer une liste déroulante pour sélectionner l'aéroport de départ
    aeroport_depart_options = {f"{a[1]} ({a[2]})": a for a in aeroports_depart}
    aeroport_depart_selection = st.selectbox("Sélectionnez un aéroport de départ", list(aeroport_depart_options.keys()))

    # Récupération des détails de l'aéroport sélectionné pour le départ
    selected_aeroport_depart = aeroport_depart_options[aeroport_depart_selection]
    id_aeroport_depart, nom_aeroport_depart, code_iata_depart, descriptif_aeroport_depart = selected_aeroport_depart

    # Requête pour récupérer les informations des voyages
    cursor.execute("""
        SELECT v.id_voyage, v.nb_jour_voyage, v.id_ville_destination, vl.nom_ville
        FROM voyage v
        JOIN ville vl ON v.id_ville_destination = vl.id_ville
    """)
    voyages = cursor.fetchall()

    if voyages:
        voyage_options = {f"Voyage {v[0]} - {v[3]} ({v[1]} jours)": v for v in voyages}
        voyage_selection = st.selectbox("Sélectionnez un voyage", list(voyage_options.keys()))

        # Récupération des détails du voyage sélectionné
        selected_voyage = voyage_options[voyage_selection]
        id_voyage, nb_jour_voyage, id_ville_destination, nom_ville = selected_voyage

        # Requête pour récupérer les informations de la ville de destination
        cursor.execute("""
            SELECT nom_ville
            FROM ville
            WHERE id_ville = ?
        """, (id_ville_destination,))
        ville_details = cursor.fetchone()

        if ville_details:
            nom_ville = ville_details[0]
            st.subheader(f"Ville de destination : {nom_ville}")

            # Requête pour récupérer les aéroports de la ville de destination
            cursor.execute("""
                SELECT id_aeroport, nom_aeroport, code_iata 
                FROM aeroport 
                WHERE id_ville = ?
            """, (id_ville_destination,))
            aeroports = cursor.fetchall()

            if aeroports:
                aeroport_options = {f"{a[1]} ({a[2]})": a[0] for a in aeroports}
                aeroport_selection = st.selectbox("Sélectionnez un aéroport", list(aeroport_options.keys()))

                # Récupération du id_aeroport sélectionné
                selected_aeroport_id = aeroport_options[aeroport_selection]

                # Mettre à jour la liste des voitures dans session_state
                if st.session_state.aeroport_id != selected_aeroport_id:
                    st.session_state.voitures = fetch_voitures(selected_aeroport_id)
                    st.session_state.aeroport_id = selected_aeroport_id

                st.subheader("Liste des voitures disponibles")
                if st.session_state.voitures:
                    voiture_options = {f"{v[5]} - {v[3]} - {v[2]} pers - {v[4]}": v for v in st.session_state.voitures}
                    voiture_selection = st.selectbox("Sélectionnez une voiture", list(voiture_options.keys()))
                    selected_voiture = voiture_options[voiture_selection]
                    id_voiture = selected_voiture[0]

                    # Ajout de la fonctionnalité de suppression de voiture
                    with st.expander("Supprimer une voiture", expanded=False):                       
                        if st.button("Supprimer la voiture"):
                            delete_voiture(id_voiture)
                            st.success(f"Voiture avec ID {id_voiture} supprimée avec succès!")
                            # Recharger la liste des voitures après suppression
                            st.session_state.voitures = fetch_voitures(selected_aeroport_id)
                else:
                    st.write("Aucune voiture disponible pour cet aéroport.")

                # Ajouter une nouvelle voiture avec un expander
                with st.expander("Ajouter une nouvelle voiture", expanded=False):
                    with st.form(key="ajouter_voiture_form", clear_on_submit=True):
                        st.subheader("Formulaire de création de voiture")

                        lien_voiture_nouvelle = st.text_input("Lien de la voiture")
                        nb_pers_max_nouvelle = st.number_input("Nombre de personnes maximum", min_value=1)
                        fournisseur_nouvelle = st.text_input("Fournisseur")
                        description_nouvelle = st.text_input("Description")
                        modele_voiture_nouvelle = st.text_input("Modèle de voiture")

                        submit_nouvelle_voiture = st.form_submit_button("Ajouter voiture")

                        if submit_nouvelle_voiture:
                            add_voiture(selected_aeroport_id, lien_voiture_nouvelle, nb_pers_max_nouvelle, fournisseur_nouvelle, description_nouvelle, modele_voiture_nouvelle)
                            st.success("Voiture ajoutée avec succès!")

                            # Recharger la liste des voitures après ajout
                            st.session_state.voitures = fetch_voitures(selected_aeroport_id)

                st.header("INSERT nouvelle période")

                # Formulaire de saisie
                with st.form("formulaire_sql"):
                    # Saisie de la date (fixée)
                    date_reservation = st.date_input("Date de réservation", value=date(2025, 5, 6))

                    # Saisie du prix du vol
                    st.subheader("Vol")
                    prix_vol = st.number_input("Prix du vol", value=155, min_value=0)

                    # Saisie des prix pour la voiture et l'assurance
                    st.subheader("Voiture")
                    prix_voiture = st.number_input("Prix de la voiture", value=343, min_value=0)
                    prix_assurance = st.number_input("Prix de l'assurance voiture", value=97, min_value=0)

                    # Requête pour récupérer les villes de l'itinéraire du voyage sélectionné
                    cursor.execute("""
                        SELECT id_ville, nb_nuit_ville
                        FROM itineraire
                        WHERE id_voyage = ?
                    """, (id_voyage,))
                    itineraires = cursor.fetchall()

                    logement_prix = {}
                    logement_index = 1
                    for ville_id, nb_nuit in itineraires:
                        cursor.execute("""
                            SELECT l.id_logement, l.lien_logement, l.nb_pers_max, v.nom_ville
                            FROM logement l
                            JOIN ville v ON l.id_ville = v.id_ville
                            WHERE l.id_ville = ?
                        """, (ville_id,))
                        ville_logements = cursor.fetchall()

                        if ville_logements:
                            logement_prix[ville_id] = {}
                            for logement in ville_logements:
                                id_logement, lien_logement, nb_pers_max, nom_ville_logement = logement
                                st.subheader(f"Logement {logement_index} ({nb_pers_max} pers) - {nom_ville_logement}")
                                st.write(f"**Lien**: [Voir le logement]({lien_logement})")
                                logement_prix[ville_id][id_logement] = []
                                for i in range(1, 8):
                                    jour = "jour" if i == 1 else "jours"
                                    # Unique key for each number input
                                    key = f"logement_{logement_index}_{id_logement}_{i}"
                                    prix = st.number_input(f"Prix pour {i} {jour}", value=100, min_value=0, key=key)
                                    logement_prix[ville_id][id_logement].append(prix)
                                # Incrémenter l'index pour le prochain logement
                                logement_index += 1
                        else:
                            st.write(f"Aucun logement trouvé pour la ville {ville_id}")

                    # Bouton de soumission
                    submit = st.form_submit_button("Générer les commandes SQL")

                    # Génération des commandes SQL
                    if submit:
                        # Commande SQL pour le vol
                        sql_vol = f"INSERT INTO vol VALUES ({id_aeroport_depart}, {selected_aeroport_id}, {prix_vol}, NULL, '{date_reservation}', '{date_reservation + timedelta(days=nb_jour_voyage)}');"

                        # Commande SQL pour la voiture
                        sql_voiture = f"INSERT INTO dispo_voiture VALUES ({id_voiture}, '{date_reservation}', {nb_jour_voyage}, {prix_voiture}, {prix_assurance});"

                        # Commandes SQL pour les logements
                        sql_logements = []
                        for ville_id, logements_ville in logement_prix.items():
                            for id_logement, prix_list in logements_ville.items():
                                for i, prix in enumerate(prix_list, start=1):
                                    sql_logements.append(f"INSERT INTO dispo_logement VALUES ({id_logement}, '{date_reservation}', {i}, {prix});")

                        # Affichage des commandes SQL
                        st.subheader("Commandes SQL Générées:")
                        st.code(sql_voiture + "\n\n" + sql_vol + "\n\n" + "\n".join(sql_logements))
            else:
                st.error("Aucun aéroport disponible pour la ville de destination.")
        else:
            st.error("Aucune information disponible pour la ville de destination.")
    else:
        st.error("Aucun voyage disponible pour le départ.")
else:
    st.error("Aucun aéroport disponible pour le départ.")

# Fermer la connexion
conn.close()
