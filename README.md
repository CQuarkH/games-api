# API REST - Gestión de Juegos

API REST para la gestión de un repositorio de juegos con operaciones CRUD.

## Requisitos

- Python 3.8+
- pip

## Instalación

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
```

## Ejecutar la API

```bash
# Iniciar el servidor (crea la BD automáticamente)
python app.py

# La API estará disponible en http://localhost:5000
```

## Cargar datos de prueba

```bash
# Ejecutar script de seeding (después de iniciar app.py al menos una vez)
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

Para pruebas de rendimiento con k6, modificar en `app.py`:

```python
# Ya configurado: debug=False para mejor rendimiento
app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
```

(Seba) Para usar PostgreSQL o MySQL, cambiar la URI en `app.py`:

```python
# PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost:5432/games_db'

# MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost:3306/games_db'

