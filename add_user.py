import os
import sys
import bcrypt
from database import SessionLocal, Usuario

def add_user(username, password, es_admin=False):
    """Agrega un nuevo usuario al sistema"""
    db = SessionLocal()
    
    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(Usuario).filter(Usuario.username == username).first()
        if existing_user:
            print(f"El usuario '{username}' ya existe")
            return False
        
        # Crear nuevo usuario
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        new_user = Usuario(
            username=username,
            hashed_password=hashed_password,
            es_admin=es_admin
        )
        
        db.add(new_user)
        db.commit()
        
        print(f"Usuario '{username}' creado exitosamente")
        print(f"¿Es admin?: {es_admin}")
        return True
        
    except Exception as e:
        print(f"Error creando usuario: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def list_users():
    """Lista todos los usuarios"""
    db = SessionLocal()
    
    try:
        users = db.query(Usuario).all()
        print("\n=== Usuarios existentes ===")
        for user in users:
            admin_str = "(ADMIN)" if user.es_admin else ""
            print(f"- {user.username} {admin_str}")
        print(f"Total: {len(users)} usuarios\n")
        
    except Exception as e:
        print(f"Error listando usuarios: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python add_user.py listar              - Lista todos los usuarios")
        print("  python add_user.py <usuario> <password> - Crea nuevo usuario")
        print("  python add_user.py <usuario> <password> admin - Crea usuario admin")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "listar":
        list_users()
    elif len(sys.argv) >= 3:
        username = sys.argv[1]
        password = sys.argv[2]
        es_admin = len(sys.argv) >= 4 and sys.argv[3].lower() == "admin"
        
        add_user(username, password, es_admin)
    else:
        print("Argumentos insuficientes")
        sys.exit(1)
