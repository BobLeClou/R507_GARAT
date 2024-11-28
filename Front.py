import requests
from flask import Flask, abort, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.j2')


@app.route('/accueil')
def accueil():
    return render_template('accueil.j2')

@app.route('/emprunts')
def emprunts():
    return render_template('emprunts.j2')

@app.route('/livres')
def livres():
    return render_template('livres.j2')

@app.route('/rechercher', methods=['GET'])
def rechercher():
    
    variable = request.args.get('type')

    url = f'http://127.0.0.1:5001/{variable}'
    response = requests.get(url)
    return render_template('rechercher.j2', name=variable, result=response.json())
       
@app.route("/ajouter", methods=["GET", "POST"])
def ajouter():
    

    if request.method == "GET":
        variable = request.args.get('type')
        variable = str(variable)
        print(variable)
        try:
            return render_template(f'ajouter_{variable}.j2', name=variable)
        except Exception as e:
            print(f"Erreur : {e}")  # Affiche l'erreur dans la console
            return f"Une erreur est survenue : {e}", 500
        
    if request.method == "POST":
        type = request.form.get('type')
        print(type)
        if type == "utilisateurs":
            url = 'http://127.0.0.1:5001/utilisateur/ajouter'
            nom = request.form.get('nom')
            email = request.form.get('email')
            data = {
                "nom": nom,
                "email": email
            }
            # Effectuer une requête POST
            response = requests.post(url, json=data)

            # Vérifier la réponse de l'API
            if response.status_code == 201:
                return "Utilisateur ajouté avec succès", 201
            else:
                return f"Erreur lors de l'ajout : {response.json()}", response.status_code

        elif type == "livres":
            url = 'http://127.0.0.1:5001/livres/ajouter'
            titre = request.form.get('titre')
            pitch = request.form.get('pitch')
            nom_auteur = request.form.get('nom_auteur')
            date = request.form.get('date')

            # Formater les données pour l'API
            livre_data = {
                "titre": titre,
                "pitch": pitch,
                "nom_auteur": nom_auteur,
                "date_public": date
            }

            # Envoyer les données via une requête POST
            response = requests.post(url, json=livre_data)

            # Gérer la réponse
            if response.status_code == 201:
                return "Livre ajouté avec succès", 201
            else:
                return f"Erreur lors de l'ajout du livre : {response.json()}", response.status_code
        elif type == "auteurs":
            url = 'http://127.0.0.1:5001/auteur'
        else:
            return "Type non supporté", 400



@app.route('/resultats', methods=["GET", "POST"], endpoint='resultats')
def resultats():
    utilisateur = request.form.get("utilisateur")
    livre = request.form.get("livres")

    if utilisateur:
        url_utilisateur = f'http://127.0.0.1:5001/utilisateur/emprunts/{utilisateur}'

        try:
            response = requests.get(url_utilisateur)

            if response.status_code == 200:
                emprunt = response.json()
                return render_template('resultats.j2', emprunt=emprunt, utilisateur=utilisateur)
            else:
                abort(400, description="L'utilisateur n'a pas été trouvé.")

        except:
            abort(400, description="Erreur")
    if livre:
        url_livre = f'http://127.0.0.1:5001/utilisateur/emprunts/{utilisateur}'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)