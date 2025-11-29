"""
API REST para gestión de juegos
Implementa operaciones CRUD sobre una colección de juegos
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuración para PostgreSQL
# Formato: postgresql://usuario:password@host:puerto/nombre_bd
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/games_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Game(db.Model):
    """
    Modelo que representa un juego en la base de datos.
    """
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    genero = db.Column(db.String(100), nullable=False)
    plataforma = db.Column(db.String(100), nullable=False)
    fecha_lanzamiento = db.Column(db.Date, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
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

@app.route('/games', methods=['GET'])
def get_all_games():
    try:
        games = Game.query.all()
        return jsonify([game.to_dict() for game in games]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    game = Game.query.get(game_id)
    
    if game is None:
        return jsonify({'error': 'Juego no encontrado'}), 404
    
    return jsonify(game.to_dict()), 200

@app.route('/games', methods=['POST'])
def create_game():
    data = request.get_json()
    
    if data is None:
        return jsonify({'error': 'Se requiere body JSON'}), 400
    
    required_fields = ['nombre', 'genero', 'plataforma', 'fecha_lanzamiento', 'precio']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    try:
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

@app.route('/games/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    game = Game.query.get(game_id)
    
    if game is None:
        return jsonify({'error': 'Juego no encontrado'}), 404
    
    data = request.get_json()
    
    try:
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
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@app.route('/games/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
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

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Base de datos PostgreSQL inicializada correctamente.")
        except Exception as e:
            print(f"Error al conectar con PostgreSQL: {e}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)