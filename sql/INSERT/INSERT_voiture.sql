INSERT INTO voiture 
VALUES ((SELECT IFNULL(MAX(id_voiture), 0) + 1 FROM voiture), 
        3, 
        NULL,
        5,
        'Europcar',
        'Toyota Auris');