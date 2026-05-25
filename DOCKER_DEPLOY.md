# Despliegue con Docker

## Construir la imagen Docker

```bash
docker build -t oconca-app .
```

## Ejecutar con Docker

```bash
docker run -d -p 8000:8000 -v $(pwd)/oconca.db:/app/oconca.db oconca-app
```

## Ejecutar con Docker Compose (recomendado)

```bash
docker-compose up -d
```

## Ver logs

```bash
docker-compose logs -f
```

## Detener

```bash
docker-compose down
```

## Para despliegue en la nube (Render, Railway, etc.)

1. Subir el código a GitHub
2. Conectar el repositorio a la plataforma de hosting
3. Configurar:
   - Build Command: `docker build -t oconca-app .`
   - Start Command: `docker run -p 8000:8000 oconca-app`
   - Puerto: 8000

## Notas importantes

- La base de datos SQLite se monta como volumen para persistencia
- Los archivos Excel de plantillas también se montan como volúmenes
- El servidor escucha en 0.0.0.0:8000 para acceso externo
