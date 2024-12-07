import sqlite3
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
import requests
import uvicorn
import os

"""
Faites l'API avec les "endpoints" suivants :

1. Chemins `/utilisateurs`, `/livres`, `/auteurs` : renvoient la liste en JSON des tables complètes
1. Chemin `/utilisateur/<utilisateur>` : renvoie le dictionnaire correspondant à l'utilisateur d'id `utilisateur` ou par l'utilisateur de nom `utilisateur` si un seul utilisateur porte ce nom-là. Si plusieurs portent le même nom, une erreur est renvoyée.
1. Chemin `/utilisateur/emprunts/<utilisateur>` : renvoie la liste des livres empruntés par l'utilisateur d'id `utilisateur` ou par l'utilisateur de nom `utilisateur` si un seul utilisateur porte ce nom-là.
1. Chemin `/livres/siecle/<numero>` : renvoie la liste des livres du siècle marqué.

1. Chemin `/livres/ajouter` : en POST ajoute un livre au format identique au fichier JSON (si l'auteur n'existe pas encore il est ajouté)
1. Chemin `/utilisateur/ajouter` : en POST ajoute un utilisateur (format {"nom": nom_user, "email": email_user})

1. Chemin `/utilisateur/<utilisateur>/supprimer` : en DELETE

1. Chemin `/utilisateur/{utilisateur_id}/emprunter/{livre_id}` : en PUT, permet d'emprunter un livre
1. Chemin `/utilisateur/{utilisateur_id}/rendre/{livre_id}` : en PUT, permet de rendre un livre
"""

# Votre code ici...

print("Répertoire courant :", os.getcwd())

app = FastAPI()

database = './database.db'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#Verif du token
#Verif du token
def verify_token_external(token: str):
    try:
        response = requests.get(f"http://authenticator:5002/verify", headers={"Authorization": f"Bearer {token}"})

        response.raise_for_status()  # Lève une exception si la réponse n'est pas 200
        return response.json()["username"]
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=401, detail="Invalid token")


'''Partie GET'''
@app.get('/utilisateurs')
async def utilisateurs(token: str = Depends(oauth2_scheme)):
    verify_token_external(token)
    print("Token Valide")

    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM utilisateurs")
    utilisateurs = cursor.fetchall()
    conn.close()
    return utilisateurs

@app.get('/livres')
async def livres(token: str = Depends(oauth2_scheme)):
    verify_token_external(token)
    print("Token Valide")

    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livres")
    livres = cursor.fetchall()
    conn.close()
    return livres

@app.get('/auteurs')
async def auteurs(token: str = Depends(oauth2_scheme)):
    verify_token_external(token)
    print("Token Valide")

    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM auteurs")
    auteurs = cursor.fetchall()
    conn.close()
    return auteurs

@app.get('/utilisateur/{utilisateur}')
async def utilisateur_var(utilisateur: str, token: str = Depends(oauth2_scheme)):
    verify_token_external(token)
    print("Token Valide")

    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    if utilisateur.isdigit():
        cursor.execute("SELECT * FROM utilisateurs WHERE id = ?", (utilisateur,))
    else:
        cursor.execute("SELECT * FROM utilisateurs WHERE nom = ?", (utilisateur,))

    utilisateurs_data = cursor.fetchall()
    conn.close()

    if len(utilisateurs_data) == 1:
        return utilisateurs_data[0]
    elif len(utilisateurs_data) > 1:
        raise HTTPException(status_code=400, detail="plusieurs utilisateur ont le meme nom")
    else:
        raise HTTPException(status_code=404, detail="utilisateur non trouvé")

@app.get('/utilisateur/emprunts/{utilisateur}')
async def utilisateur_emprunts_var(utilisateur: str, token: str = Depends(oauth2_scheme)):
    verify_token_external(token)
    print("Token Valide")

    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    if utilisateur.isdigit():
        cursor.execute("SELECT * FROM utilisateurs WHERE id = ?", (utilisateur,))
    else:
        cursor.execute("SELECT * FROM utilisateurs WHERE nom = ?", (utilisateur,))

    utilisateur_data = cursor.fetchall()

    if len(utilisateur_data) == 1:
        utilisateur_id = utilisateur_data[0][0]
        cursor.execute("SELECT * FROM livres WHERE emprunteur_id = ?", (utilisateur_id,))
        emprunts = cursor.fetchall()
        conn.close()
        return emprunts
    elif len(utilisateur_data) > 1:
        raise HTTPException(status_code=400, detail="plusieurs utilisateur ont le meme nom")
    else:
        raise HTTPException(status_code=404, detail="utilisateur non trouvé")

@app.get('/livres/siecle/{numero}')
async def livres_siecle_var(numero: int, token: str = Depends(oauth2_scheme)):
    verify_token_external(token)
    print("Token Valide")

    if 0 <= numero <= 21:
        start_date = (numero - 1) * 100
        end_date = numero * 100 + 99
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM livres WHERE date_public BETWEEN ? AND ?", (start_date, end_date))
        livres = cursor.fetchall()
        conn.close()
        return livres
    else:
        raise HTTPException(status_code=400, detail="le siecle n'est pas au bon format : doit etre un nombre entier entre 0 et 21")
    

'''Partie POST'''
@app.post('/livres/ajouter')
async def livres_ajouter(request: Request, token: str = Depends(oauth2_scheme)):
    verify_token_external(token)
    print("Token Valide")

    book = await request.json()
    if not book or not 'titre' in book:
        raise HTTPException(status_code=400, detail="Data invalide : demande un format JSON et le titre")

    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM auteurs WHERE nom_auteur = ?", (book['nom_auteur'],))
    auteur = cursor.fetchone()
    if not auteur:
        cursor.execute("INSERT INTO auteurs (nom_auteur) VALUES (?)", (book['nom_auteur'],))
        auteur_id = cursor.lastrowid
    else:
        auteur_id = auteur[0]

    cursor.execute('''
        INSERT INTO livres (titre, pitch, auteur_id, date_public)
        VALUES (?, ?, ?, ?)
    ''', (book['titre'], book['pitch'], auteur_id, book['date_public']))
    conn.commit()
    conn.close()

    return JSONResponse(content={'message': 'Livre ajouter avec succès'}, status_code=201)

@app.post('/utilisateur/ajouter')
async def utilisateur_ajouter(request: Request, token: str = Depends(oauth2_scheme)):
    verify_token_external(token)
    print("Token Valide")

    user = await request.json()
    if not user or not 'nom' in user or not 'email' in user:
        raise HTTPException(status_code=400, detail="Data invalide : demande un format JSON, le nom et l'email")

    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO utilisateurs (nom, email) VALUES (?, ?)", (user['nom'], user['email']))
    conn.commit()
    conn.close()
    return JSONResponse(content={'message': 'utilisateur ajouté avec succès'}, status_code=201)

'''Partie DELETE'''
@app.delete('/utilisateur/{utilisateur}/supprimer')
async def utilisateur_var_supprimer(utilisateur: str, token: str = Depends(oauth2_scheme)):
    verify_token_external(token)
    print("Token Valide")

    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM utilisateurs WHERE id = ? OR nom = ?", (utilisateur, utilisateur))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="L'utilisateur n'existe pas")

    conn.commit()
    conn.close()
    return JSONResponse(content={'message': 'Utilisateur supprimé avec succès'})

'''Partie PUT'''
@app.put('/utilisateur/{utilisateur_id}/emprunter/{livre_id}')
async def utilisateur_var_emprunter_var(utilisateur_id: int, livre_id: int, token: str = Depends(oauth2_scheme)):
    verify_token_external(token)
    print("Token Valide")

    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("UPDATE livres SET emprunteur_id = ? WHERE id = ?", (utilisateur_id, livre_id))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Le livre ou l'utilisateur est introuvable")
    conn.commit()
    conn.close()
    return JSONResponse(content={'message': 'Livre emprunté avec succès'})

@app.put('/utilisateur/{utilisateur_id}/rendre/{livre_id}')
async def utilisateur_var_rendre_var(utilisateur_id: int, livre_id: int, token: str = Depends(oauth2_scheme)):
    verify_token_external(token)
    print("Token Valide")

    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("UPDATE livres SET emprunteur_id = NULL WHERE id = ? AND emprunteur_id = ?", (livre_id, utilisateur_id))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Le livre ou l'utilisateur est introuvable")
    conn.commit()
    conn.close()
    return JSONResponse(content={'message': 'Livres rendu avec succès'})

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5001)