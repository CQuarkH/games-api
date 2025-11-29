/**
 * K6 Spike Test - Games API
 * Prueba repentina de carga: picos súbitos de tráfico
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
    stages: [
        { duration: '2m', target: 50 },     // Tráfico normal
        { duration: '10s', target: 500 },   // SPIKE! Súbito incremento
        { duration: '2m', target: 500 },    // Mantener spike
        { duration: '10s', target: 50 },    // Vuelta a normal
        { duration: '2m', target: 50 },     // Recuperación
        { duration: '10s', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<1500'],
        errors: ['rate<0.05'],
    },
    ext: {
        loadimpact: {
            projectID: 0,
            name: 'Spike Test - Sudden Traffic'
        }
    }
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';

const genres = ['Acción', 'Aventura', 'RPG'];
const platforms = ['PC', 'PlayStation 5', 'Xbox Series X'];

function getRandomElement(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

export default function () {
    const dice = Math.random();
    
    if (dice < 0.50) {
        const res = http.get(`${BASE_URL}/games`);
        check(res, { 'GET /games': (r) => r.status === 200 }) || errorRate.add(1);
    } else {
        const gameId = Math.floor(Math.random() * 100) + 1;
        const res = http.get(`${BASE_URL}/games/${gameId}`);
        check(res, { 'GET /games/:id': (r) => r.status === 200 || r.status === 404 }) || errorRate.add(1);
    }
    
    sleep(Math.random() + 0.5);
}
