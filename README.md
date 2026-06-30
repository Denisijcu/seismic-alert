`README.md` actualizado y más estratégico, para que cualquiera que se sume entienda qué estamos construyendo, qué ya está hecho y cuál es la ruta de crecimiento. [earthquake.usgs](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php)

```md
# seismic-alert

Sistema de alertas sísmicas construido con FastAPI, PostgreSQL, Alembic, Redis y Telegram.

El objetivo del proyecto es detectar eventos sísmicos reales desde una fuente externa, procesarlos en nuestro backend, guardarlos en base de datos y notificar por Telegram cuando corresponda.

## Visión del proyecto

Este proyecto nace como una plataforma de alertas sísmicas en tiempo real.  
La idea es conectar una fuente oficial de eventos sísmicos, normalizar los datos, aplicar reglas de negocio y enviar notificaciones automáticas a usuarios o canales de alerta.

En esta primera fase ya tenemos resuelta la base técnica del sistema:
- API funcional.
- Persistencia en PostgreSQL.
- Migraciones con Alembic.
- Tests automatizados.
- Canal de notificación por Telegram en prueba.
- Estructura preparada para crecer a nuevos canales como push y SMS.

## Arquitectura actual

Flujo general:

1. Una fuente externa entrega un evento sísmico.
2. El backend recibe o consulta ese evento.
3. Se valida y normaliza la información.
4. Se guarda en PostgreSQL.
5. Se decide si el evento amerita alerta.
6. Se envía notificación por Telegram.
7. Se registra el resultado del envío.
8. El usuario puede dar feedback sobre el evento.

## Fuente de eventos sísmicos

La idea es trabajar con una fuente real y confiable de eventos sísmicos.  
Una de las principales candidatas es la API pública del USGS, que ofrece feeds en tiempo real y consultas en formato GeoJSON y FDSN Event Catalog.

Feeds útiles del USGS:
- `all_hour.geojson`
- `all_day.geojson`
- `all_week.geojson`
- `all_month.geojson`

El feed GeoJSON está pensado para consumo programático y se actualiza cada minuto.

## Estado actual del proyecto

### Ya resuelto
- FastAPI funcionando.
- PostgreSQL funcionando.
- Alembic aplicado.
- Endpoints principales operativos.
- Tests pasando.
- Integración inicial con Telegram.
- README base creado.
- Separación entre entorno de Docker y entorno local para pruebas.

### En desarrollo
- Conexión a una fuente real de eventos sísmicos.
- Regla de decisión para alertas.
- Persistencia del resultado de envío por canal.
- Reintentos y control de duplicados.
- Integración real de push y SMS.

### Pendiente
- Worker o proceso de polling para consultar la fuente externa.
- Normalización de eventos desde la API externa al formato interno.
- Trazabilidad completa de alertas.
- Observabilidad y métricas básicas.

## Flujo funcional

### Ingesta
El sistema recibe un evento sísmico con campos como:
- magnitud.
- profundidad.
- latitud.
- longitud.
- timestamp.
- identificador del evento.

### Procesamiento
Luego se evalúa:
- si el evento supera el umbral de alerta.
- si ya fue procesado antes.
- qué canal debe usarse.
- si la alerta debe enviarse o no.

### Notificación
Actualmente Telegram es el primer canal real.  
Push y SMS quedan preparados como futuras extensiones.

## Estructura de trabajo

```text
app/
├── api/
├── core/
├── models/
├── repositories/
├── services/
└── main.py

tests/
├── conftest.py
├── test_health.py
├── test_routes.py
└── test_pipeline_edges.py

alembic/
docker-compose.yml
README.md
```

## Entorno local

### Variables generales
Usar archivos `.env` separados según contexto:
- `.env.docker` para ejecutar dentro de Docker.
- `.env.local` para migraciones y pruebas locales.
- variables de test aisladas para Pytest.

### Base de datos
En desarrollo local:
- PostgreSQL corre en `localhost:5434`.

En Docker:
- PostgreSQL se accede por el host interno `postgres`.

## Levantar el proyecto

```bash
docker compose up --build
```

La API queda disponible en:
- `http://localhost:8000`
- `http://localhost:8000/docs`

## Migraciones

Aplicar migraciones:

```bash
alembic upgrade head
```

Crear una migración nueva:

```bash
alembic revision --autogenerate -m "mensaje"
```

## Tests

Ejecutar pruebas:

```bash
pytest -q
```

Los tests usan una base de prueba aislada y no dependen de la base de datos de Docker.

## Telegram

Actualmente el sistema ya puede enviar mensajes de prueba a Telegram.  
Esto valida la salida real de alertas y confirma que el canal de notificación está operativo.

## Próximos pasos

1. Conectar la fuente real de sismos.
2. Construir un worker de consulta periódica.
3. Normalizar los datos al modelo interno.
4. Definir reglas de alerta.
5. Guardar trazabilidad por canal.
6. Convertir Telegram, push y SMS en canales reales.

## Objetivo final

Construir un sistema de alertas sísmicas capaz de:
- leer eventos reales,
- evaluar su relevancia,
- guardar el historial,
- notificar automáticamente,
- y dejar evidencia de cada alerta emitida.
```

## Qué comunica este README
Con este documento ya queda claro que el proyecto no es solo una API, sino un sistema de alertas sísmicas con una ruta de crecimiento bien definida. [earthquake.usgs](https://earthquake.usgs.gov/earthquakes/feed/v1.0/)
También deja explícito que USGS es una fuente candidata real para alimentar el flujo, y que el feed GeoJSON está pensado para uso programático. [earthquake.usgs](https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson)

## Lo que yo haría después
Yo lo subiría como base del repo y luego lo iría afinando cuando tengamos:
- el worker de consumo,
- la regla de alertas,
- y la estructura de notificación definitiva. [earthquake.usgs](https://earthquake.usgs.gov/earthquakes/feed/)

