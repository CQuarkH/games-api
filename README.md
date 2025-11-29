# API REST - Gestión de Juegos

API REST para la gestión de un repositorio de juegos con operaciones CRUD y pruebas de carga automatizadas.

## Requisitos

- Docker & Docker Compose (Recomendado)
- Python 3.8+ (Para ejecución local)
- pip

## Inicio Rápido con Docker (RECOMENDADO)

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd games-api

# Crear entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# 1. Iniciar servicios (PostgreSQL + API)
docker-compose up -d

# 2. Verificar que los servicios estén funcionando
docker-compose ps

# La API estará disponible en http://localhost:5000
# Health check: http://localhost:5000/health
```

## Ejecutar Pruebas de Carga

```bash
# Ejecutar TODAS las pruebas de rendimiento (seeding + load + stress + spike)
docker-compose --profile tests run --rm k6-tests

# Generar gráficos PNG de los resultados
docker-compose --profile tools run --rm generate-graphs

# Ver reportes en: ./load-tests/reports/test-results.html
```

## Tipos de Pruebas Disponibles

- **Load Test**: 100 usuarios concurrentes (10 min)
- **Stress Test**: Escalamiento progresivo hasta 1500 usuarios
- **Spike Test**: Picos súbitos de tráfico
- **Seeding**: 1000 juegos de prueba

## Cargar datos de prueba

```bash
# Opción 1: Usando Docker (automático en las pruebas)
docker-compose --profile tests run --rm k6-tests

# Opción 2: Manual con script local (requiere API ejecutándose)
python seed.py
```

## Endpoints

| Método | Endpoint      | Descripción              |
| ------ | ------------- | ------------------------ |
| GET    | `/games`      | Obtener todos los juegos |
| GET    | `/games/<id>` | Obtener un juego por ID  |
| POST   | `/games`      | Crear un nuevo juego     |
| PUT    | `/games/<id>` | Actualizar un juego      |
| DELETE | `/games/<id>` | Eliminar un juego        |

## Formato de datos

```json
{
  "id": 1,
  "nombre": "The Legend of Zelda",
  "genero": "Aventura",
  "plataforma": "Nintendo Switch",
  "fecha_lanzamiento": "2023-05-12",
  "precio": 59.99
}
```

## Ejemplos con curl

```bash
# Obtener todos los juegos
curl http://localhost:5000/games

# Obtener juego por ID
curl http://localhost:5000/games/1

# Crear nuevo juego
curl -X POST http://localhost:5000/games \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Nuevo Juego","genero":"Acción","plataforma":"PC","fecha_lanzamiento":"2024-01-15","precio":49.99}'

# Actualizar juego
curl -X PUT http://localhost:5000/games/1 \
  -H "Content-Type: application/json" \
  -d '{"precio":39.99}'

# Eliminar juego
curl -X DELETE http://localhost:5000/games/1
```

## Configuración para producción

El sistema está optimizado para pruebas de rendimiento:

```python
# Configuración actual en app.py
app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

# Pool de conexiones PostgreSQL optimizado
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
```

## Resultados de Pruebas

Después de ejecutar las pruebas, revisa:

- **Reporte HTML**: `./load-tests/reports/test-results.html`
- **Métricas JSON**: `./load-tests/reports/*-summary.json`
- **Gráficos PNG**: `./load-tests/reports/*-graph.png`
- **Logs detallados**: `./load-tests/reports/*-log.txt`

## Alternativas de Base de Datos

Para cambiar de PostgreSQL, modificar en `app.py`:

```python
# MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost:3306/games_db'

# SQLite (para desarrollo)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///games.db'
```

