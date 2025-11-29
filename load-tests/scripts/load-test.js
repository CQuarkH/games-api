/**
 * K6 Load Test - Games API
 * Simula 100 usuarios concurrentes durante 10 minutos
 * Distribuye las operaciones CRUD según un patrón realista
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Métricas personalizadas
const errorRate = new Rate('errors');

// Configuración del test de carga
export const options = {
    stages: [
        { duration: '30s', target: 20 },   // Warm-up: 20 usuarios
        { duration: '1m', target: 100 },   // Ramp-up: hasta 100 usuarios
        { duration: '8m', target: 100 },   // Carga sostenida: 100 usuarios
        { duration: '30s', target: 0 },    // Ramp-down: vuelta a 0
    ],
    thresholds: {
        http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% < 500ms, 99% < 1s
        http_req_failed: ['rate<0.01'],                  // Tasa de error < 1%
        errors: ['rate<0.01'],
    },
    // Exportar métricas a InfluxDB local
    ext: {
        loadimpact: {
            projectID: 0,
            name: 'Load Test - 100 Users'
        }
    }
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';

// Pool de datos para crear juegos
const genres = ['Acción', 'Aventura', 'RPG', 'Estrategia', 'Deportes', 'Simulación', 'Puzzle'];
const platforms = ['PC', 'PlayStation 5', 'Xbox Series X', 'Nintendo Switch', 'Multi-plataforma'];

function getRandomElement(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function generateRandomGame() {
    const randomId = Math.floor(Math.random() * 1000000);
    return {
        nombre: `Juego Test ${randomId}`,
        genero: getRandomElement(genres),
        plataforma: getRandomElement(platforms),
        fecha_lanzamiento: '2024-01-15',
        precio: (Math.random() * 60 + 10).toFixed(2)
    };
}

export default function () {
    const dice = Math.random();
    
    // GET /games - 40% de las peticiones
    if (dice < 0.40) {
        const res = http.get(`${BASE_URL}/games`);
        check(res, {
            'GET /games status 200': (r) => r.status === 200,
            'GET /games is array': (r) => {
                try {
                    return Array.isArray(JSON.parse(r.body));
                } catch {
                    return false;
                }
            }
        }) || errorRate.add(1);
    }
    // GET /games/:id - 30% de las peticiones
    else if (dice < 0.70) {
        const gameId = Math.floor(Math.random() * 100) + 1; // IDs del 1 al 100
        const res = http.get(`${BASE_URL}/games/${gameId}`);
        check(res, {
            'GET /games/:id status ok': (r) => r.status === 200 || r.status === 404,
        }) || errorRate.add(1);
    }
    // POST /games - 15% de las peticiones
    else if (dice < 0.85) {
        const game = generateRandomGame();
        const res = http.post(
            `${BASE_URL}/games`,
            JSON.stringify(game),
            { headers: { 'Content-Type': 'application/json' } }
        );
        check(res, {
            'POST /games status 201': (r) => r.status === 201,
            'POST /games returns game': (r) => {
                try {
                    const body = JSON.parse(r.body);
                    return body.id !== undefined;
                } catch {
                    return false;
                }
            }
        }) || errorRate.add(1);
    }
    // PUT /games/:id - 10% de las peticiones
    else if (dice < 0.95) {
        const gameId = Math.floor(Math.random() * 100) + 1;
        const update = {
            precio: (Math.random() * 60 + 10).toFixed(2)
        };
        const res = http.put(
            `${BASE_URL}/games/${gameId}`,
            JSON.stringify(update),
            { headers: { 'Content-Type': 'application/json' } }
        );
        check(res, {
            'PUT /games/:id status ok': (r) => r.status === 200 || r.status === 404,
        }) || errorRate.add(1);
    }
    // DELETE /games/:id - 5% de las peticiones
    else {
        const gameId = Math.floor(Math.random() * 100) + 1;
        const res = http.del(`${BASE_URL}/games/${gameId}`);
        check(res, {
            'DELETE /games/:id status ok': (r) => r.status === 200 || r.status === 404,
        }) || errorRate.add(1);
    }
    
    // Simular tiempo de "pensar" entre peticiones (1-3 segundos)
    sleep(Math.random() * 2 + 1);
}
