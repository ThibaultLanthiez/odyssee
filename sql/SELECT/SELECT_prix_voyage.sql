SELECT 
    TOTAL_LOGEMENT_PAR_PERS+TOTAL_VOL_PAR_PERS+PRIX_VOITURE, 
    TOTAL_LOGEMENT_PAR_PERS,
    TOTAL_VOL_PAR_PERS,
    PRIX_VOITURE
FROM (
        SELECT SUM(PRIX_LOGEMENT_PAR_VILLE)/:nb_personne AS TOTAL_LOGEMENT_PAR_PERS
        FROM (
            SELECT 
                itineraire.id_ville,
                MIN(dispo_logement.prix_total) AS PRIX_LOGEMENT_PAR_VILLE
            FROM 
                itineraire, logement, dispo_logement
            WHERE 
                itineraire.id_ville = logement.id_ville
                AND logement.id_logement = dispo_logement.id_logement
                AND logement.nb_pers_max >= :nb_personne
                AND dispo_logement.nb_nuit = itineraire.nb_nuit_ville
                AND dispo_logement.date_premiere_nuit = :date_premier_jour
                AND itineraire.id_voyage = :id_voyage
            GROUP BY 
                itineraire.id_ville
            )
    ),
    (
        SELECT prix_vol AS TOTAL_VOL_PAR_PERS
        FROM vol, aeroport, voyage
        WHERE 
            aeroport.id_ville = voyage.id_ville_destination 
            AND aeroport.id_aeroport = vol.id_aeroport_destination
            AND vol.date_aller = :date_premier_jour
            AND voyage.id_voyage = :id_voyage
        ORDER BY vol.prix_vol
        LIMIT 1
    ),
    (
        SELECT 
            MIN(dispo_voiture.prix_voiture+dispo_voiture.prix_assurance)/:nb_personne AS PRIX_VOITURE
        FROM 
            voyage, aeroport, voiture, dispo_voiture
        WHERE 
            voiture.id_voiture = dispo_voiture.id_voiture
            AND voiture.nb_pers_max >= :nb_personne
            AND dispo_voiture.nb_jour = voyage.nb_jour_voyage
            AND dispo_voiture.date_debut = :date_premier_jour
            AND aeroport.id_ville = voyage.id_ville_destination 
            AND aeroport.id_aeroport = voiture.id_aeroport
            AND voyage.id_voyage = :id_voyage
    );