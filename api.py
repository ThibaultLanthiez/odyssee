from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/api/resultats', methods=['GET'])
def api_resultats():
    id_voyage = request.args.get('id_voyage', type=int)
    date_premier_jour = request.args.get('date_premier_jour', type=str)
    nb_personne = request.args.get('nb_personne', type=int)
    
    if nb_personne is None or id_voyage is None:
        return jsonify({'error': 'Les paramètres nb_personne et id_voyage sont requis.'}), 400
    
    try:
        # Lire la commande SQL depuis le fichier
        with open('sql/SELECT/SELECT_prix_voyage.sql', 'r') as fichier_sql:
            commande_sql = fichier_sql.read()

        # Valeurs dynamiques à insérer sous forme de dictionnaire
        parametres = {
            'id_voyage': id_voyage,
            'date_premier_jour': date_premier_jour,
            'nb_personne': nb_personne
        }

        # Exécuter la commande SQL avec les valeurs dynamiques
        connexion = sqlite3.connect('odyssee.db')
        curseur = connexion.cursor()
        curseur.execute(commande_sql, parametres)

        # Récupération de toutes les lignes de résultats
        resultats = curseur.fetchall()
        if not resultats:
            return jsonify({'message': 'Aucun résultat trouvé.'}), 404
        
        # Convertir les résultats en JSON
        resultats_json = [{'total': row[0], 'logement': row[1], 'vol': row[2], 'voiture': row[3]} for row in resultats]
        connexion.close()
        return jsonify(resultats_json)
    
    except Exception as e:
        connexion.close()
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/voyage_ids', methods=['GET'])
def get_voyage_ids():   
    connexion = sqlite3.connect('odyssee.db')
    curseur = connexion.cursor()
    curseur.execute('SELECT DISTINCT id_voyage FROM voyage')
    resultats = curseur.fetchall()
    connexion.close()
    return jsonify([row[0] for row in resultats])

@app.route('/api/dates_disponibles', methods=['GET'])
def get_dates_disponibles():
    connexion = sqlite3.connect('odyssee.db')
    curseur = connexion.cursor()
    curseur.execute('SELECT DISTINCT date_aller FROM vol')
    resultats = curseur.fetchall()
    connexion.close()
    return jsonify([row[0] for row in resultats])

@app.route('/api/info_voyage', methods=['GET'])
def get_voyage_info():   
    connexion = sqlite3.connect('odyssee.db')
    curseur = connexion.cursor()
    curseur.execute('SELECT id_voyage, nb_jour_voyage, nom_ville FROM voyage, ville WHERE voyage.id_ville_destination = ville.id_ville')
    resultats = curseur.fetchall()
    if not resultats:
        return jsonify({'message': 'Aucun résultat trouvé.'}), 404

    # Convertir les résultats en JSON
    resultats_json = [{'id_voyage': row[0], 'nb_jour_voyage': row[1], 'nom_ville': row[2]} for row in resultats]
    connexion.close()
    return jsonify(resultats_json)


if __name__ == '__main__':
    app.run(debug=True)
