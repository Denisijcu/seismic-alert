Claro. Te dejo un `README.md` corto y práctico, alineado con lo que ya tienes funcionando: Docker para correr la app, Alembic para migraciones y `pytest` con DB aislada para tests. [github](https://github.com/Buuntu/fastapi-react/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/README.md)

## `README.md`
```md
# seismic-alert

API para ingesta y seguimiento de eventos sísmicos con FastAPI, PostgreSQL, Alembic y Pytest.

## Requisitos

- Docker y Docker Compose.
- Python 3.12+ para ejecutar tests locales.

## Estructura de entorno

- `.env.docker`: usado por la API dentro de Docker.
- `.env.local`: usado por Alembic desde Windows o desde tu máquina.
- Tests: usan una base aislada mediante `dependency_overrides`.

## Levantar el proyecto

```bash
docker compose up --build
```

La API queda disponible en:

- `http://localhost:8000`
- `http://localhost:8000/docs`

## Migraciones

Para aplicar migraciones desde tu máquina:

```bash
alembic upgrade head
```

Si quieres crear una nueva migración:

```bash
alembic revision --autogenerate -m "mensaje"
```

## Docker y base de datos

Dentro de Docker, la API usa:

- `POSTGRES_HOST=postgres`
- `POSTGRES_PORT=5432`

Desde tu máquina local, Alembic usa:

- `POSTGRES_HOST=localhost`
- `POSTGRES_PORT=5434`

## Endpoints

### Health

```bash
curl http://localhost:8000/health
```

### Ingesta de evento

```bash
curl -i -X POST http://localhost:8000/ingest/event \
  -H "Content-Type: application/json" \
  -d "{\"event_id\":\"test-001\",\"magnitude\":4.2,\"depth_km\":10.5,\"latitude\":-12.0464,\"longitude\":-77.0428,\"timestamp_utc\":\"2026-06-29T18:08:51Z\"}"
```

### Feedback

```bash
curl -i -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d "{\"event_id\":\"test-001\",\"was_correct\":true,\"note\":\"Test ok\"}"
```

## Tests

Ejecutar tests locales:

```bash
pytest -q
```

Los tests usan una base de prueba separada y sobrescriben la dependencia de base de datos para no tocar PostgreSQL de Docker.

## Solución de problemas

### La API arranca pero falla `/ingest/event`
Verifica que las tablas existan y que hayas ejecutado:

```bash
alembic upgrade head
```

### `pytest` intenta conectar a `postgres`
Asegúrate de que los tests usen el override de `get_db` y una base de prueba local.

### `curl` devuelve `500`
Revisa los logs del contenedor:

```bash
docker logs -f seismic-alert-api-1
```
```

## Qué hace este README
Deja claro qué archivo de entorno usa cada contexto, cómo levantar Docker, cómo correr migraciones y cómo ejecutar pruebas sin volver a caer en el problema de `postgres` vs `localhost`. [github](https://github.com/tzelleke/fastapi-sqlalchemy/blob/main/README.md)

## Recomendación
Si quieres, el siguiente paso útil es agregar una sección de “Comandos rápidos” y otra de “Arquitectura” con tu diagrama de carpetas real.