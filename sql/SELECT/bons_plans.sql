SELECT
    id_aeroport_destination,
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
    id_aeroport_depart = 13
    AND id_aeroport_destination IN (8, 6, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23)  -- Liste précise des destinations
    AND (julianday(date_retour) - julianday(date_aller)) IN (7, 10, 14)  -- Filtrer pour les voyages de 7, 10 ou 14 jours
    AND strftime('%Y-%m', date_aller) = '2024-12'  -- Limiter les départs à décembre 2024
GROUP BY
    id_aeroport_destination,
    strftime('%Y-%m', date_aller)  -- Grouper par destination et mois uniquement
ORDER BY
    id_aeroport_destination,
    prix_minimum,
    date_aller;


/*
9|Tous les aéroports de Paris|PAR|     
7|Marseille-Provence|MRS|
2|Lyon|LYS|
10|Nice Côte d'Azur|NCE|
11|Bordeaux Mérignac|BOD|
12|Nantes Atlantique|NTE|
13|Lille Lesquin|LIL|

6|Amsterdam Schiphol|AMS|
8|Oslo Sandefjord|TRF|
14|Tous les aéroports de Montréal|YMQ|
15|Tous les aéroports de Bangkok|BKK|
16|Tous les aéroports de Londres|LON|
17|Dublin|DUB|
18|Mykonos|JMK|
19|Réunion Roland Garros|RUN|
20|Le Caire|CAI|
21|Lisbonne Humberto Delgado|LIS|
22|Tous les aéroports de Venise|VCE|
23|Split|SPU|
*/
