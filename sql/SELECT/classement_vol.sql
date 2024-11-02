SELECT
    strftime('%Y-%m', date_aller),
    MIN(prix_vol) AS prix_minimum,
    date_aller,
    date_retour
FROM
    vol
WHERE
    id_aeroport_depart = 2
    AND id_aeroport_destination = 8
    AND julianday(date_retour) - julianday(date_aller) = 7  -- Filtrer pour un voyage de 7 jours
GROUP BY
    strftime('%Y-%m', date_aller)  -- Regrouper par année et mois de date de départ
ORDER BY
    date_aller;
