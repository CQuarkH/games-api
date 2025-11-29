/**
 * Script de Seeding para Pruebas de Carga
 * Genera 1000 juegos de prueba en la base de datos
 */

import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';

export const options = {
    vus: 10,  // 10 usuarios virtuales para seed más rápido
    iterations: 100,  // Cada VU crea 10 juegos = 1000 total
};

const genres = [
    'Acción', 'Aventura', 'RPG', 'Estrategia',
    'Deportes', 'Simulación', 'Puzzle', 'Terror',
    'Plataformas', 'Carreras', 'FPS', 'MMORPG'
];

const platforms = [
    'PC', 'PlayStation 5', 'Xbox Series X', 'Nintendo Switch',
    'PlayStation 4', 'Xbox One', 'Multi-plataforma', 'Mobile',
    'Steam', 'Epic Games Store'
];

const gameNames = [
    'Shadow Warriors', 'Dragon Quest', 'Speed Racers', 'Fantasy World',
    'Battle Royale', 'Zombie Apocalypse', 'Space Invaders', 'Mario Kart Clone',
    'FIFA Clone', 'Minecraft Clone', 'Fortnite Clone', 'The Last of Us Clone',
    'God of War Clone', 'Zelda Clone', 'Pokemon Clone', 'Final Fantasy Clone'
];

function getRandomElement(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function generateRandomDate() {
    const year = 2020 + Math.floor(Math.random() * 5);
    const month = String(Math.floor(Math.random() * 12) + 1).padStart(2, '0');
    const day = String(Math.floor(Math.random() * 28) + 1).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

export default function () {
    const game = {
        nombre: `${getRandomElement(gameNames)} ${Math.floor(Math.random() * 10000)}`,
        genero: getRandomElement(genres),
        plataforma: getRandomElement(platforms),
        fecha_lanzamiento: generateRandomDate(),
        precio: parseFloat((Math.random() * 70 + 9.99).toFixed(2))
    };
    
    const res = http.post(
        `${BASE_URL}/games`,
        JSON.stringify(game),
        { headers: { 'Content-Type': 'application/json' } }
    );
    
    check(res, {
        'seed game created': (r) => r.status === 201,
    });
    
    sleep(0.1);  // Pequeña pausa para no saturar
}

export function handleSummary(data) {
    return {
        stdout: `\n✅ Seeding completado: ${data.metrics.iterations.values.count} juegos creados\n`,
    };
}
