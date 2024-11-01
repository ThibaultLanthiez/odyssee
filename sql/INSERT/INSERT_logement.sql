INSERT INTO logement 
VALUES ((SELECT IFNULL(MAX(id_logement), 0) + 1 FROM logement), 
        2, 
        'https://www.airbnb.fr/rooms/886670030219807022',
        6);