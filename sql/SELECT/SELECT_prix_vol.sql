SELECT prix_vol
FROM vol, aeroport, voyage
WHERE 
    aeroport.id_ville = voyage.id_ville_destination 
    AND aeroport.id_aeroport = vol.id_aeroport_destination
    AND voyage.id_voyage = 1
ORDER BY vol.prix_vol
LIMIT 1;