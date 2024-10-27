INSERT INTO logement 
VALUES ((SELECT IFNULL(MAX(id_logement), 0) + 1 FROM logement), 
        2, 
        127,
        'https://www.airbnb.fr/rooms/886670030219807022?check_in=2025-04-25&check_out=2025-04-26&guests=1&adults=6&s=67&unique_share_id=68c064f0-ee9e-4f45-a022-27b2cbd2a6ba',
        '2025-04-25',
        6);