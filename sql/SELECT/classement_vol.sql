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
    id_aeroport_depart = 13
    AND id_aeroport_destination = 16
    AND (julianday(date_retour) - julianday(date_aller)) IN (7, 10, 14)  -- Filtrer pour les voyages de 7, 10 ou 14 jours
    AND date_aller > date('2024-11-02')
GROUP BY
    strftime('%Y-%m', date_aller),
    duree_voyage  -- Regrouper par mois/année et durée de voyage
ORDER BY
    duree_voyage, 
    date_aller;


/*
9|Tous les aéroports de Paris|PAR|     
7|Marseille-Provence|MRS|
2|Lyon|LYS|
10|Nice Côte d'Azur|NCE|
11|Bordeaux Mérignac|BOD|
12|Nantes Atlantique|NTE|
13|Lille Lesquin|LIL|
25|Genève-Cointrin|GVA|

8|Oslo Sandefjord|TRF|
6|Amsterdam Schiphol|AMS|
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
24|Casablanca Mohammed V|CMN|
*/

163
155
184
179
171
194
186
198
268