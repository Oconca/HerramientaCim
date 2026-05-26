# Instrucciones para subir a GitHub

## 1. Crear repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre del repositorio: `oconca` (o el que prefieras)
3. Descripción: `OCONCA - Sistema de evaluación CIMTRA`
4. Marca "Public" o "Private" según tu preferencia
5. **NO** marques "Add a README file" (ya tenemos .gitignore)
6. **NO** marques "Add .gitignore"
7. **NO** marques "Choose a license"
8. Haz clic en "Create repository"

## 2. Conectar el repositorio local con GitHub

Después de crear el repositorio, GitHub te mostrará comandos. Usa estos:

```bash
# Reemplaza TU_USUARIO con tu nombre de usuario de GitHub
& "C:\Program Files\Git\cmd\git.exe" remote add origin https://github.com/TU_USUARIO/oconca.git
& "C:\Program Files\Git\cmd\git.exe" push -u origin main
```

## 3. Autenticación (si es necesario)

Si te pide usuario y contraseña:
- **Usuario:** tu nombre de usuario de GitHub
- **Contraseña:** usa un **Personal Access Token** en lugar de tu contraseña

### Crear Personal Access Token:
1. Ve a GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → Classic
3. Selecciona permisos: `repo` (full control)
4. Genera y copia el token
5. Usa el token como contraseña

## 4. Verificar

```bash
& "C:\Program Files\Git\cmd\git.exe" remote -v
```

Debería mostrar:
```
origin  https://github.com/TU_USUARIO/oconca.git (fetch)
origin  https://github.com/TU_USUARIO/oconca.git (push)
```

## 5. Para futuros cambios

```bash
& "C:\Program Files\Git\cmd\git.exe" add .
& "C:\Program Files\Git\cmd\git.exe" commit -m "tu mensaje"
& "C:\Program Files\Git\cmd\git.exe" push
```

## Notas importantes

- El repositorio ya tiene un commit inicial con todos los archivos
- Los archivos sensibles (base de datos, Excel) están en .gitignore
- El Dockerfile está incluido para despliegue fácil
