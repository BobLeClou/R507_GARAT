import requests
from flask import Flask, abort, render_template, request

app_flask = Flask(__name__)

@app_flask.route('/accueil')
def accueil():
    return render_template('accueil.j2')

@app_flask.route('/emprunts')
def emprunts():
    return render_template('emprunts.j2')

@app_flask.route('/livres')
def livres():
    return render_template('livres.j2')

@app_flask.route('/resultats', methods=["GET", "POST"], endpoint='resultats')
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
    app_flask.run(debug=True)