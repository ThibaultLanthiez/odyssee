# Liste initiale
data_list = [
    '1224', 'lun.', '17', 'févr.', 
    '937', 'mar.', '18', 'févr.', 
    '855', 'mer.', '19', 'févr.', 
    '979', 'jeu.', '20', 'févr.', 
    'ven.', '21', 'févr.', 
    'sam.', '22', 'févr.', 
    '1059', 'dim.', '23', 'févr.', 
    '1236', 'lun.', '24', 'févr.', 
    '1096', 'mar.', '25', 'févr.',
    '925', 'mer.', '26', 'févr.', 
    '935', 'jeu.', '27', 'févr.'
]

# Liste pour stocker les résultats
filtered_data = []

# Vérifier que nous avons assez d'éléments
i = 0
while i + 3 < len(data_list):
    price = data_list[i]
    day = data_list[i + 1]
    date = data_list[i + 2]
    month = data_list[i + 3]

    # Vérifier si le prix est valide et si le jour et le mois sont des strings
    if price.isdigit() and isinstance(day, str) and isinstance(month, str):
        # Ajouter à la liste des résultats
        filtered_data.append((price, day, date, month))
        i+=4
    else:
        i+=3

# Afficher les résultats filtrés
for entry in filtered_data:
    print(f"Prix: {entry[0]}, Jour: {entry[1]}, Date: {entry[2]}, Mois: {entry[3]}")
