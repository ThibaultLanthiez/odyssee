SELECT 
    MIN(dispo_voiture.prix_voiture+dispo_voiture.prix_assurance)/5 AS PRIX_VOITURE
FROM 
    voyage, aeroport, voiture, dispo_voiture
WHERE 
    voiture.id_voiture = dispo_voiture.id_voiture
    AND voiture.nb_pers_max >= 5
    AND dispo_voiture.nb_jour = voyage.nb_jour_voyage
    AND aeroport.id_ville = voyage.id_ville_destination 
    AND aeroport.id_aeroport = voiture.id_aeroport
    AND voyage.id_voyage = 1;