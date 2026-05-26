# Instrucciones para Despliegue en Render

## Problema Actual
El proyecto está desplegado pero no funciona el login porque:
1. No hay usuarios iniciales en la base de datos
2. La base de datos SQLite local no se subió a GitHub
3. Render necesita PostgreSQL con configuración adecuada

## Solución Implementada

### 1. Cambios Realizados
- ✅ Agregado `create_seed_user()` en `app.py` - crea usuario admin automáticamente
- ✅ Agregado `psycopg2-binary` en `requirements.txt` - soporte para PostgreSQL
- ✅ Actualizado `Dockerfile` - incluye libpq-dev para PostgreSQL
- ✅ Creado `seed.py` - script alternativo para crear usuarios

### 2. Configuración en Render

#### Paso 1: Configurar Variables de Entorno
En tu dashboard de Render, ve al servicio y agrega estas variables:

**Variables de Entorno Necesarias:**
```
DATABASE_URL = postgresql://usuario:password@host:puerto/database
ADMIN_PASSWORD = tu_contraseña_segura
SECRET_KEY = tu_clave_secreta_para_jwt
```

#### Paso 2: Configurar Base de Datos PostgreSQL
1. En Render, crea una nueva base de datos PostgreSQL
2. Copia la `Internal Database URL` que te proporciona Render
3. Úsala como valor para `DATABASE_URL`

#### Paso 3: Redesplegar
1. Haz push de los cambios a GitHub
2. Render detectará los cambios y redeployará automáticamente
3. El usuario admin se creará automáticamente al iniciar

## Credenciales por Defecto
Después del deploy, usa:
- **Usuario:** `admin`
- **Contraseña:** `admin123` (o el valor de `ADMIN_PASSWORD` si lo configuraste)

⚠️ **IMPORTANTE:** Cambia la contraseña después del primer login

## Instrucciones Paso a Paso

### 1. Subir cambios a GitHub
```bash
& "C:\Program Files\Git\cmd\git.exe" add .
& "C:\Program Files\Git\cmd\git.exe" commit -m "Add seed user and PostgreSQL support"
& "C:\Program Files\Git\cmd\git.exe" push
```

### 2. Configurar en Render
1. Ve a tu servicio en Render
2. En "Environment", agrega las variables:
   - `DATABASE_URL`: (copia de tu base de datos PostgreSQL)
   - `ADMIN_PASSWORD`: `admin123` (o una contraseña segura)
   - `SECRET_KEY`: genera una clave segura (puedes usar: https://randomkeygen.com/)

3. Crea una base de datos PostgreSQL si no tienes una
4. Copia la conexión y úsala en `DATABASE_URL`

### 3. Redesplegar
- Render redeployará automáticamente cuando detecte cambios
- O haz clic en "Manual Deploy" → "Deploy latest commit"

### 4. Verificar
1. Espera a que el deploy termine
2. Ve a la URL de tu servicio
3. Intenta login con `admin` / `admin123`

## Solución de Problemas

### Error: "Usuario o contraseña incorrectos"
- Verifica que la base de datos PostgreSQL esté configurada
- Revisa los logs de Render para ver si el usuario admin se creó
- Verifica que `ADMIN_PASSWORD` esté configurado

### Error de conexión a base de datos
- Verifica que `DATABASE_URL` sea correcta
- Asegúrate de que la base de datos PostgreSQL esté funcionando
- Revisa los logs en Render

### El usuario admin no se crea
- Revisa los logs de la aplicación en Render
- Verifica que no haya errores en `create_seed_user()`
- Asegúrate de que la base de datos tenga permisos de escritura

## Alternativa: Sin PostgreSQL (Solo para desarrollo)

Si quieres usar SQLite en Render (no recomendado para producción):
1. No configures `DATABASE_URL`
2. La aplicación usará SQLite localmente
3. **NOTA:** Los datos se perderán en cada redeploy

## Seguridad
- Cambia `SECRET_KEY` en producción
- Cambia la contraseña del admin después del primer login
- Usa HTTPS (Render lo proporciona automáticamente)
- Considera agregar rate limiting para el login
