/**
 * K6 Stress Test - Games API
 * Escala progresivamente hasta encontrar el punto de ruptura
 * Etapas: 100 → 200 → 500 → 1000 → 1500 usuarios
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
    stages: [
        { duration: '1m', target: 100 },    // Warmup
        { duration: '2m', target: 100 },    // Estabilizar
        { duration: '1m', target: 200 },    // Incremento a 200
        { duration: '2m', target: 200 },    // Mantener 200
        { duration: '1m', target: 500 },    // Incremento a 500
        { duration: '2m', target: 500 },    // Mantener 500
        { duration: '1m', target: 1000 },   // Incremento a 1000
        { duration: '2m', target: 1000 },   // Mantener 1000
        { duration: '1m', target: 1500 },   // Push to failure
        { duration: '2m', target: 1500 },   // Mantener 1500
        { duration: '1m', target: 0 },      // Recovery
    ],
    thresholds: {
        http_req_duration: ['p(95)<2000'],  // Más permisivo para stress
        errors: ['rate<0.05'],               // Aceptar hasta 5% de errores
    },
    ext: {
        loadimpact: {
            projectID: 0,
            name: 'Stress Test - Progressive Scaling'
        }
    }
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';

const genres = ['Acción', 'Aventura', 'RPG', 'Estrategia', 'Deportes', 'Simulación'];
const platforms = ['PC', 'PlayStation 5', 'Xbox Series X', 'Nintendo Switch'];

function getRandomElement(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function generateRandomGame() {
    const randomId = Math.floor(Math.random() * 1000000);
    return {
        nombre: `Stress Game ${randomId}`,
        genero: getRandomElement(genres),
        plataforma: getRandomElement(platforms),
        fecha_lanzamiento: '2024-01-01',
        precio: (Math.random() * 60 + 10).toFixed(2)
    };
}

export default function () {
    const dice = Math.random();
    
    if (dice < 0.40) {
        const res = http.get(`${BASE_URL}/games`);
        check(res, { 'GET /games OK': (r) => r.status === 200 }) || errorRate.add(1);
    }
    else if (dice < 0.70) {
        const gameId = Math.floor(Math.random() * 100) + 1;
        const res = http.get(`${BASE_URL}/games/${gameId}`);
        check(res, { 'GET /games/:id OK': (r) => r.status === 200 || r.status === 404 }) || errorRate.add(1);
    }
    else if (dice < 0.85) {
        const game = generateRandomGame();
        const res = http.post(
            `${BASE_URL}/games`,
            JSON.stringify(game),
            { headers: { 'Content-Type': 'application/json' } }
        );
        check(res, { 'POST /games OK': (r) => r.status === 201 }) || errorRate.add(1);
    }
    else if (dice < 0.95) {
        const gameId = Math.floor(Math.random() * 100) + 1;
        const update = { precio: (Math.random() * 60 + 10).toFixed(2) };
        const res = http.put(
            `${BASE_URL}/games/${gameId}`,
            JSON.stringify(update),
            { headers: { 'Content-Type': 'application/json' } }
        );
        check(res, { 'PUT /games/:id OK': (r) => r.status === 200 || r.status === 404 }) || errorRate.add(1);
    }
    else {
        const gameId = Math.floor(Math.random() * 100) + 1;
        const res = http.del(`${BASE_URL}/games/${gameId}`);
        check(res, { 'DELETE /games/:id OK': (r) => r.status === 200 || r.status === 404 }) || errorRate.add(1);
    }
    
    sleep(Math.random() * 2 + 1);
}
