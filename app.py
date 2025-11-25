"""
API REST para gestión de juegos
Implementa operaciones CRUD sobre una colección de juegos
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuración de base de datos
# SQLite para desarrollo local, cambiar URI para PostgreSQL/MySQL en producción
# PostgreSQL: 'postgresql://user:password@localhost:5432/games_db'
# MySQL: 'mysql://user:password@localhost:3306/games_db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///games.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ============================================
# MODELO DE DATOS
# ============================================
class Game(db.Model):
    """
    Modelo que representa un juego en la base de datos.
    Atributos:
        - id: Identificador único autoincremental
        - nombre: Nombre del juego
        - genero: Género del juego (Aventura, RPG, etc.)
        - plataforma: Plataforma del juego (PC, PS5, etc.)
        - fecha_lanzamiento: Fecha de lanzamiento del juego
        - precio: Precio del juego en formato decimal
    """
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    genero = db.Column(db.String(100), nullable=False)
    plataforma = db.Column(db.String(100), nullable=False)
    fecha_lanzamiento = db.Column(db.Date, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        """Convierte el objeto Game a diccionario para serialización JSON"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'genero': self.genero,
            'plataforma': self.plataforma,
            'fecha_lanzamiento': self.fecha_lanzamiento.isoformat(),
            'precio': self.precio
        }


# ============================================
# ENDPOINTS CRUD
# ============================================

# GET /games - Obtener todos los juegos
@app.route('/games', methods=['GET'])
def get_all_games():
    """
    Retorna la lista completa de juegos almacenados.
    Response: 200 OK con array de juegos
    """
    games = Game.query.all()
    return jsonify([game.to_dict() for game in games]), 200


# GET /games/<id> - Obtener un juego por ID
@app.route('/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    """
    Retorna un juego específico por su ID.
    Response: 200 OK con el juego, o 404 si no existe
    """
    game = Game.query.get(game_id)
    
    if game is None:
        return jsonify({'error': 'Juego no encontrado'}), 404
    
    return jsonify(game.to_dict()), 200


# POST /games - Crear un nuevo juego
@app.route('/games', methods=['POST'])
def create_game():
    """
    Crea un nuevo juego en la base de datos.
    Body esperado (JSON):
        - nombre: string (requerido)
        - genero: string (requerido)
        - plataforma: string (requerido)
        - fecha_lanzamiento: string ISO date "YYYY-MM-DD" (requerido)
        - precio: float (requerido)
    Response: 201 Created con el juego creado, o 400 si hay error de validación
    """
    data = request.get_json()
    
    # Validar que se recibió JSON
    if data is None:
        return jsonify({'error': 'Se requiere body JSON'}), 400
    
    # Validar campos requeridos
    required_fields = ['nombre', 'genero', 'plataforma', 'fecha_lanzamiento', 'precio']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    try:
        # Parsear fecha desde string ISO (YYYY-MM-DD)
        fecha = datetime.strptime(data['fecha_lanzamiento'], '%Y-%m-%d').date()
        
        new_game = Game(
            nombre=data['nombre'],
            genero=data['genero'],
            plataforma=data['plataforma'],
            fecha_lanzamiento=fecha,
            precio=float(data['precio'])
        )
        
        db.session.add(new_game)
        db.session.commit()
        
        return jsonify(new_game.to_dict()), 201
        
    except ValueError as e:
        return jsonify({'error': f'Error en formato de datos: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


# PUT /games/<id> - Actualizar un juego existente
@app.route('/games/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    """
    Actualiza un juego existente por su ID.
    Permite actualización parcial (solo los campos enviados).
    Response: 200 OK con el juego actualizado, o 404 si no existe
    """
    game = Game.query.get(game_id)
    
    if game is None:
        return jsonify({'error': 'Juego no encontrado'}), 404
    
    data = request.get_json()
    
    if data is None:
        return jsonify({'error': 'Se requiere body JSON'}), 400
    
    try:
        # Actualizar solo los campos proporcionados
        if 'nombre' in data:
            game.nombre = data['nombre']
        if 'genero' in data:
            game.genero = data['genero']
        if 'plataforma' in data:
            game.plataforma = data['plataforma']
        if 'fecha_lanzamiento' in data:
            game.fecha_lanzamiento = datetime.strptime(data['fecha_lanzamiento'], '%Y-%m-%d').date()
        if 'precio' in data:
            game.precio = float(data['precio'])
        
        db.session.commit()
        
        return jsonify(game.to_dict()), 200
        
    except ValueError as e:
        return jsonify({'error': f'Error en formato de datos: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


# DELETE /games/<id> - Eliminar un juego
@app.route('/games/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    """
    Elimina un juego de la base de datos por su ID.
    Response: 200 OK con mensaje de confirmación, o 404 si no existe
    """
    game = Game.query.get(game_id)
    
    if game is None:
        return jsonify({'error': 'Juego no encontrado'}), 404
    
    try:
        db.session.delete(game)
        db.session.commit()
        
        return jsonify({'message': f'Juego {game_id} eliminado correctamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


# ============================================
# INICIALIZACIÓN
# ============================================

# Crear las tablas al iniciar la aplicación
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    # host='0.0.0.0' permite conexiones externas (necesario para JMeter)
    # debug=True para desarrollo, cambiar a False para pruebas de rendimiento
    app.run(host='0.0.0.0', port=5000, debug=True)