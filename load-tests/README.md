# Pruebas de Carga y Estrés - Games API 🚀

Sistema automatizado de pruebas de rendimiento para la API de gestión de juegos usando **k6**, **Docker**.

## 📋 Tabla de Contenidos

- [Inicio Rápido](#inicio-rápido)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Tipos de Pruebas](#tipos-de-pruebas)
- [Interpretación de Resultados](#interpretación-de-resultados)

---

## ⚡ Inicio Rápido

### 🐳 Método 1: 100% Docker (RECOMENDADO)

```bash
# 1. Iniciar servicios base
docker-compose up -d

# 2. Ejecutar TODAS las pruebas (seeding + load + stress + spike)
docker-compose --profile tests run --rm k6-tests

# 3. Generar gráficos PNG
docker-compose --profile tools run --rm generate-graphs
```

---

## 📊 Resultados Generados

Después de ejecutar las pruebas:
1. ✅ Levantamiento de servicios Docker
2. ✅ Verificación de health checks
3. ✅ Seeding de 1000 juegos de prueba
4. ✅ **Load Test** (100 usuarios concurrentes)
5. ✅ **Stress Test** (escalado hasta 1500 usuarios)
6. ✅ **Spike Test** (picos súbitos de tráfico)
7. ✅ Generación de reportes HTML con gráficos

### Ver resultados

- **Reporte HTML**: `.\load-tests\reports\test-results.html`
- **API Health**: http://localhost:5000/health

---

## 📁 Estructura del Proyecto

```
load-tests/
├── scripts/
│   ├── load-test.js           # Prueba de carga (100 VUs)
│   ├── stress-test.js         # Prueba de estrés (hasta 1500 VUs)
│   ├── spike-test.js          # Prueba de picos súbitos
│   └── seed-data.js           # Generación de datos de prueba
├── reports/                    # Resultados generados automáticamente
│   ├── test-results.html      # Reporte HTML con gráficos
│   ├── *-summary.json         # Métricas en JSON
│   ├── *-log.txt              # Logs detallados
│   └── *-graph.png            # Gráficos generados
├── generate_graphs.py         # Script Python para gráficos
├── run-tests.ps1              # Script de automatización principal
└── README.md                  # Este archivo
```

---

## 🎯 Tipos de Pruebas

### 1. Load Test - Prueba de Carga Normal

**Objetivo**: Validar que el sistema maneje carga normal sin degradación.

**Configuración**:
- **Usuarios**: 100 concurrentes
- **Duración**: 10 minutos
- **Distribución de peticiones**:
  - 40% - GET /games (listar todos)
  - 30% - GET /games/:id (obtener uno)
  - 15% - POST /games (crear)
  - 10% - PUT /games/:id (actualizar)
  - 5% - DELETE /games/:id (eliminar)

**Criterios de éxito**:
- ✅ p95 < 500ms
- ✅ p99 < 1000ms
- ✅ Tasa de error < 1%

**Comando manual**:
```bash
k6 run --out influxdb=http://localhost:8086/k6 .\load-tests\scripts\load-test.js
```

---

### 2. Stress Test - Prueba de Estrés Progresivo

**Objetivo**: Encontrar el punto de ruptura del sistema.

**Configuración**:
- **Etapas**:
  - 100 usuarios → 2 min
  - 200 usuarios → 2 min
  - 500 usuarios → 2 min
  - 1000 usuarios → 2 min
  - 1500 usuarios → 2 min (push to failure)

**Observar**:
- ¿En qué punto aumenta drásticamente el tiempo de respuesta?
- ¿Cuándo empiezan a aparecer errores (>5%)?
- ¿El sistema se recupera al bajar la carga?

**Comando manual**:
```bash
k6 run --out influxdb=http://localhost:8086/k6 .\load-tests\scripts\stress-test.js
```

---

### 3. Spike Test - Prueba de Picos Súbitos

**Objetivo**: Validar comportamiento ante tráfico repentino.

**Configuración**:
- **Tráfico normal**: 50 usuarios
- **SPIKE**: Salto a 500 usuarios en 10 segundos
- **Duración del spike**: 2 minutos
- **Recuperación**: Vuelta a 50 usuarios

**Observar**:
- ¿El sistema maneja el spike sin caídas?
- ¿Se recupera rápidamente?

**Comando manual**:
```bash
k6 run --out influxdb=http://localhost:8086/k6 .\load-tests\scripts\spike-test.js
```

---

## 📊 Interpretación de Resultados

### Métricas Clave

#### 1. **Response Time (Tiempo de Respuesta)**
- **p50 (mediana)**: 50% de las peticiones son más rápidas que este valor
- **p95**: 95% de las peticiones son más rápidas
- **p99**: 99% de las peticiones son más rápidas
- **max**: Tiempo de respuesta máximo

**Valores deseables**:
- p95 < 500ms → ✅ Excelente
- p95 entre 500-1000ms → ⚠️ Aceptable
- p95 > 1000ms → ❌ Degradación

#### 2. **Request Rate (Throughput)**
- Peticiones por segundo que el sistema puede manejar
- **Ejemplo**: 150 req/s significa que el sistema procesa 150 peticiones cada segundo

#### 3. **Error Rate (Tasa de Errores)**
- Porcentaje de peticiones que fallan (4xx, 5xx)
- **Meta**: < 1% en load test, < 5% en stress test

#### 4. **Virtual Users (VUs)**
- Número de usuarios concurrentes simulados

### Ejemplo de Análisis

```
Load Test Results:
├─ p95: 320ms  ✅ Excelente
├─ Request Rate: 180 req/s
├─ Error Rate: 0.3%  ✅ Muy bajo
└─ Max VUs: 100

Conclusión: El sistema maneja 100 usuarios concurrentes sin problemas.
```

```
Stress Test Results:
├─ Breaking point: ~800 usuarios
├─ p95 at 800 VUs: 1850ms  ⚠️
├─ Error rate at 800 VUs: 8%  ❌
└─ Sistema degradado significativamente

Conclusión: El sistema soporta hasta ~500-600 usuarios antes de degradarse.
```

---