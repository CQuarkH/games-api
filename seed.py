"""
Script de seeding - Carga datos de prueba en la base de datos
Ejecutar después de iniciar app.py al menos una vez (para crear la BD)
Uso: python seed.py
"""

from app import app, db, Game
from datetime import date

# Datos de juegos de ejemplo para pruebas
SAMPLE_GAMES = [
    {"nombre": "The Legend of Zelda: Tears of the Kingdom", "genero": "Aventura", "plataforma": "Nintendo Switch", "fecha_lanzamiento": date(2023, 5, 12), "precio": 59.99},
    {"nombre": "Elden Ring", "genero": "RPG", "plataforma": "PC", "fecha_lanzamiento": date(2022, 2, 25), "precio": 49.99},
    {"nombre": "God of War Ragnarok", "genero": "Acción", "plataforma": "PS5", "fecha_lanzamiento": date(2022, 11, 9), "precio": 69.99},
    {"nombre": "Hogwarts Legacy", "genero": "RPG", "plataforma": "PC", "fecha_lanzamiento": date(2023, 2, 10), "precio": 59.99},
    {"nombre": "Baldur's Gate 3", "genero": "RPG", "plataforma": "PC", "fecha_lanzamiento": date(2023, 8, 3), "precio": 59.99},
    {"nombre": "Spider-Man 2", "genero": "Acción", "plataforma": "PS5", "fecha_lanzamiento": date(2023, 10, 20), "precio": 69.99},
    {"nombre": "Starfield", "genero": "RPG", "plataforma": "Xbox Series X", "fecha_lanzamiento": date(2023, 9, 6), "precio": 69.99},
    {"nombre": "Resident Evil 4 Remake", "genero": "Terror", "plataforma": "PC", "fecha_lanzamiento": date(2023, 3, 24), "precio": 59.99},
    {"nombre": "Final Fantasy XVI", "genero": "RPG", "plataforma": "PS5", "fecha_lanzamiento": date(2023, 6, 22), "precio": 69.99},
    {"nombre": "Diablo IV", "genero": "RPG", "plataforma": "PC", "fecha_lanzamiento": date(2023, 6, 6), "precio": 69.99},
    {"nombre": "Street Fighter 6", "genero": "Lucha", "plataforma": "PC", "fecha_lanzamiento": date(2023, 6, 2), "precio": 59.99},
    {"nombre": "Mortal Kombat 1", "genero": "Lucha", "plataforma": "PS5", "fecha_lanzamiento": date(2023, 9, 19), "precio": 69.99},
    {"nombre": "Alan Wake 2", "genero": "Terror", "plataforma": "PC", "fecha_lanzamiento": date(2023, 10, 27), "precio": 59.99},
    {"nombre": "Lies of P", "genero": "Acción", "plataforma": "PC", "fecha_lanzamiento": date(2023, 9, 19), "precio": 59.99},
    {"nombre": "Sea of Stars", "genero": "RPG", "plataforma": "Nintendo Switch", "fecha_lanzamiento": date(2023, 8, 29), "precio": 34.99},
    {"nombre": "Pikmin 4", "genero": "Estrategia", "plataforma": "Nintendo Switch", "fecha_lanzamiento": date(2023, 7, 21), "precio": 59.99},
    {"nombre": "Armored Core VI", "genero": "Acción", "plataforma": "PC", "fecha_lanzamiento": date(2023, 8, 25), "precio": 59.99},
    {"nombre": "Forza Motorsport", "genero": "Carreras", "plataforma": "Xbox Series X", "fecha_lanzamiento": date(2023, 10, 10), "precio": 69.99},
    {"nombre": "Super Mario Bros Wonder", "genero": "Plataformas", "plataforma": "Nintendo Switch", "fecha_lanzamiento": date(2023, 10, 20), "precio": 59.99},
    {"nombre": "Cyberpunk 2077: Phantom Liberty", "genero": "RPG", "plataforma": "PC", "fecha_lanzamiento": date(2023, 9, 26), "precio": 29.99},
    {"nombre": "Dead Space Remake", "genero": "Terror", "plataforma": "PC", "fecha_lanzamiento": date(2023, 1, 27), "precio": 59.99},
    {"nombre": "Hi-Fi Rush", "genero": "Acción", "plataforma": "PC", "fecha_lanzamiento": date(2023, 1, 25), "precio": 29.99},
    {"nombre": "Octopath Traveler II", "genero": "RPG", "plataforma": "Nintendo Switch", "fecha_lanzamiento": date(2023, 2, 24), "precio": 59.99},
    {"nombre": "Fire Emblem Engage", "genero": "Estrategia", "plataforma": "Nintendo Switch", "fecha_lanzamiento": date(2023, 1, 20), "precio": 59.99},
    {"nombre": "Metroid Prime Remastered", "genero": "Aventura", "plataforma": "Nintendo Switch", "fecha_lanzamiento": date(2023, 2, 8), "precio": 39.99},
    {"nombre": "Star Wars Jedi: Survivor", "genero": "Acción", "plataforma": "PC", "fecha_lanzamiento": date(2023, 4, 28), "precio": 69.99},
    {"nombre": "The Last of Us Part I", "genero": "Aventura", "plataforma": "PC", "fecha_lanzamiento": date(2023, 3, 28), "precio": 59.99},
    {"nombre": "Wo Long: Fallen Dynasty", "genero": "Acción", "plataforma": "PC", "fecha_lanzamiento": date(2023, 3, 3), "precio": 59.99},
    {"nombre": "System Shock Remake", "genero": "Terror", "plataforma": "PC", "fecha_lanzamiento": date(2023, 5, 30), "precio": 39.99},
    {"nombre": "Lords of the Fallen", "genero": "RPG", "plataforma": "PC", "fecha_lanzamiento": date(2023, 10, 13), "precio": 59.99},
]


def seed_database():
    """Inserta los juegos de ejemplo en la base de datos"""
    with app.app_context():
        # Verificar si ya hay datos
        existing_count = Game.query.count()
        if existing_count > 0:
            print(f"La base de datos ya tiene {existing_count} juegos.")
            response = input("¿Desea agregar más datos de prueba? (s/n): ")
            if response.lower() != 's':
                print("Operación cancelada.")
                return
        
        # Insertar juegos
        for game_data in SAMPLE_GAMES:
            game = Game(**game_data)
            db.session.add(game)
        
        db.session.commit()
        
        total = Game.query.count()
        print(f"Seeding completado. Total de juegos en BD: {total}")


if __name__ == '__main__':
    seed_database()