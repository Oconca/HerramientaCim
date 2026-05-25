import os
import json
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import bcrypt
from pydantic import BaseModel
import jwt

from database import engine, SessionLocal, Base, Usuario, Evaluacion, init_db, get_db

# Initialize database
init_db()

# --- Security Config ---
SECRET_KEY = "tu_clave_secreta_super_segura" # Cámbiar en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 días

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- App Config ---
app = FastAPI(title="Backend OCONCA")

# CORS config to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Asegurar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    password: str

class CuestionarioSave(BaseModel):
    entidad: str
    periodo: str
    cuestionario_data: list

# --- Helper Functions ---
def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    user = db.query(Usuario).filter(Usuario.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# --- Routes ---

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(Usuario).filter(Usuario.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    
    hashed_password = get_password_hash(user.password)
    new_user = Usuario(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuario registrado exitosamente"}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/me")
def get_user_me(current_user: Usuario = Depends(get_current_user)):
    return {"username": current_user.username, "es_admin": current_user.es_admin}

@app.post("/api/guardar")
def save_evaluation(payload: CuestionarioSave, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    # Buscar si ya existe una evaluación para este usuario, entidad y periodo
    evaluacion = db.query(Evaluacion).filter(
        Evaluacion.usuario_id == current_user.id,
        Evaluacion.entidad == payload.entidad,
        Evaluacion.periodo == payload.periodo
    ).first()

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if evaluacion:
        # Actualizar
        evaluacion.datos_cuestionario = json.dumps(payload.cuestionario_data)
        evaluacion.ultima_modificacion = now_str
    else:
        # Crear nueva
        evaluacion = Evaluacion(
            usuario_id=current_user.id,
            entidad=payload.entidad,
            periodo=payload.periodo,
            datos_cuestionario=json.dumps(payload.cuestionario_data),
            fecha_creacion=now_str,
            ultima_modificacion=now_str
        )
        db.add(evaluacion)
    
    db.commit()
    return {"message": "Progreso guardado correctamente"}

@app.get("/api/cargar")
def load_evaluation(entidad: str, periodo: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    evaluacion = db.query(Evaluacion).filter(
        Evaluacion.usuario_id == current_user.id,
        Evaluacion.entidad == entidad,
        Evaluacion.periodo == periodo
    ).first()

    if not evaluacion or not evaluacion.datos_cuestionario:
        raise HTTPException(status_code=404, detail="No se encontró registro para esta entidad y periodo")

    return {
        "entidad": evaluacion.entidad,
        "periodo": evaluacion.periodo,
        "cuestionario_data": json.loads(evaluacion.datos_cuestionario),
        "ultima_modificacion": evaluacion.ultima_modificacion
    }

@app.get("/api/evaluaciones")
def list_evaluations(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    evaluaciones = db.query(Evaluacion).filter(Evaluacion.usuario_id == current_user.id).all()
    
    resultado = []
    for ev in evaluaciones:
        resultado.append({
            "id": ev.id,
            "entidad": ev.entidad,
            "periodo": ev.periodo,
            "ultima_modificacion": ev.ultima_modificacion
        })
    return resultado

if __name__ == "__main__":
    import uvicorn
    # Corre el servidor en el puerto 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
