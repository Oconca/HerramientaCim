import os
import sys
from database import engine, SessionLocal, Base, Usuario
import bcrypt

def create_admin_user():
    """Crea un usuario admin por defecto si no existe"""
    db = SessionLocal()
    
    try:
        # Verificar si ya existe un usuario admin
        admin_user = db.query(Usuario).filter(Usuario.username == "admin").first()
        
        if admin_user:
            print("Usuario admin ya existe")
            return
        
        # Crear usuario admin
        password = os.getenv("ADMIN_PASSWORD", "admin123")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        admin = Usuario(
            username="admin",
            hashed_password=hashed_password,
            es_admin=True
        )
        
        db.add(admin)
        db.commit()
        
        print("Usuario admin creado exitosamente")
        print(f"Usuario: admin")
        print(f"Contraseña: {password}")
        print("¡CAMBIA LA CONTRASEÑA DESPUÉS DEL PRIMER INICIO!")
        
    except Exception as e:
        print(f"Error creando usuario admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Inicializar la base de datos
    Base.metadata.create_all(bind=engine)
    
    # Crear usuario admin
    create_admin_user()
