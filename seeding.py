"""
seeding.py
Script para poblar la base de datos con 50 juegos de prueba iniciales.
"""
import random
from datetime import date, timedelta
from app import app, db, Game

NOMBRES = ["Super", "Mega", "Ultra", "Hyper", "The Legend of", "Final", "Dark", "Cyber", "Elden", "Call of"]
SUFIJOS = ["Warrior", "Quest", "Saga", "Souls", "Kart", "Fighter", "Survivor", "Revenge", "Mission", "World"]
GENEROS = ["Acción", "Aventura", "RPG", "Estrategia", "Deportes", "Carreras", "Shooter", "Terror"]
PLATAFORMAS = ["PC", "PS5", "Xbox Series X", "Nintendo Switch"]

def generar_datos_prueba():
    with app.app_context():
        print("--- Iniciando Seeding ---")

        # Limpiar tabla para evitar duplicados en pruebas
        try:
            db.session.query(Game).delete()
        except Exception:
            pass # Si la tabla no existe o falla, continuar

        juegos_lista = []
        CANTIDAD = 50

        print(f"Generando {CANTIDAD} juegos de prueba...")

        for i in range(CANTIDAD):
            nombre_juego = f"{random.choice(NOMBRES)} {random.choice(SUFIJOS)} {random.randint(1, 999)}"

            nuevo_juego = Game(
                nombre=nombre_juego,
                genero=random.choice(GENEROS),
                plataforma=random.choice(PLATAFORMAS),
                fecha_lanzamiento=date(2020, 1, 1) + timedelta(days=random.randint(0, 1000)),
                precio=round(random.uniform(9.99, 79.99), 2)
            )
            juegos_lista.append(nuevo_juego)

        db.session.bulk_save_objects(juegos_lista)
        db.session.commit()

        total = Game.query.count()
        print(f"✅ ÉXITO: Base de datos poblada con {total} juegos.")

if __name__ == '__main__':
    generar_datos_prueba()