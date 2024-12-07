from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import encode, decode, PyJWTError as JWTError
import jwt
from datetime import datetime, timedelta


# Configuration
SECRET_KEY = "mon secret"  # Utilisez un secret plus sécurisé en production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Utilisation de OAuth2 pour la gestion des tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Application pour authentification
auth_app = FastAPI()

# Base utilisateurs fictive
fake_users_db = {
    "admin": {
        "username": "admin",
        "password": "password",  # À remplacer par un système de hash sécurisé comme bcrypt
    }
}

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@auth_app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@auth_app.get("/protected")
async def read_protected_data(token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    return {"message": f"Hello {username}, you have access to this protected data"}

@auth_app.get("/verify")
async def verify_endpoint(token: str = Depends(oauth2_scheme)):
    """
    Vérifie le token reçu et retourne le username associé s'il est valide.
    """
    username = verify_token(token)
    return {"username": username}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(auth_app, host="0.0.0.0", port=5002)
