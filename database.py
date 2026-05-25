from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.pool import StaticPool
import os

# Determina la base de datos a usar
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'oconca.db')}")

# Configurar el motor de la base de datos.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool # Requerido para SQLite en threads
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    es_admin = Column(Boolean, default=False)

    evaluaciones = relationship("Evaluacion", back_populates="usuario")

class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    entidad = Column(String(255), index=True)
    periodo = Column(String(255), index=True)
    tipo = Column(String(50), default="Capital")
    
    # Campo JSON para almacenar el progreso actual usando string para compatibilidad con todas las BD
    datos_cuestionario = Column(Text) 
    fecha_creacion = Column(String(50))
    ultima_modificacion = Column(String(50))

    usuario = relationship("Usuario", back_populates="evaluaciones")

# Función para inicializar la base de datos
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependencia para obtener la sesión de BD en FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
