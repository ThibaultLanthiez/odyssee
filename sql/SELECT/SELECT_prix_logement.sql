SELECT SUM(PRIX_LOGEMENT_PAR_VILLE)/5
FROM (
    SELECT 
        itineraire.id_ville,
        MIN(dispo_logement.prix_total) AS PRIX_LOGEMENT_PAR_VILLE
    FROM 
        itineraire, logement, dispo_logement
    WHERE 
        itineraire.id_ville = logement.id_ville
        AND logement.id_logement = dispo_logement.id_logement
        AND logement.nb_pers_max >= 5
        AND dispo_logement.nb_nuit = itineraire.nb_nuit_ville
        AND itineraire.id_voyage = 1
    GROUP BY 
        itineraire.id_ville
    );