#!/bin/bash
# Script para ejecutar todas las pruebas k6 dentro de Docker
# Se ejecuta automáticamente en el contenedor k6-tests

set -e

echo "=========================================="
echo "  PRUEBAS DE CARGA Y ESTRÉS - GAMES API"
echo "  Ejecutando con k6 en Docker"
echo "=========================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para esperar que la API esté lista
wait_for_api() {
    echo "${CYAN}==> Esperando a que la API esté lista...${NC}"
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if wget -q --spider http://api:5000/health 2>/dev/null; then
            echo "${GREEN}✓ API está lista${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    echo "${RED}✗ API no respondió a tiempo${NC}"
    return 1
}

# Función para ejecutar una prueba k6
run_k6_test() {
    test_script=$1
    test_name=$2
    output_file=$3
    
    echo ""
    echo "${CYAN}==> Ejecutando: $test_name${NC}"
    
    k6 run \
        --summary-export=/reports/${output_file}-summary.json \
        /scripts/${test_script} | tee /reports/${output_file}-log.txt
    
    if [ $? -eq 0 ]; then
        echo "${GREEN}✓ $test_name completado${NC}"
    else
        echo "${RED}✗ Error en $test_name${NC}"
    fi
}

# Esperar a que la API esté lista
wait_for_api || exit 1

echo ""
echo "${YELLOW}=========================================="
echo "  FASE 1: SEEDING DE DATOS"
echo "==========================================${NC}"

run_k6_test "seed-data.js" "Data Seeding (1000 juegos)" "seed"

echo ""
echo "${YELLOW}=========================================="
echo "  FASE 2: LOAD TEST (100 usuarios)"
echo "==========================================${NC}"

run_k6_test "load-test.js" "Load Test" "load-test"

echo ""
echo "${YELLOW}Esperando 30 segundos antes del Stress Test...${NC}"
sleep 30

echo ""
echo "${YELLOW}=========================================="
echo "  FASE 3: STRESS TEST (hasta 1500 usuarios)"
echo "==========================================${NC}"

run_k6_test "stress-test.js" "Stress Test" "stress-test"

echo ""
echo "${YELLOW}Esperando 30 segundos antes del Spike Test...${NC}"
sleep 30

echo ""
echo "${YELLOW}=========================================="
echo "  FASE 4: SPIKE TEST (picos súbitos)"
echo "==========================================${NC}"

run_k6_test "spike-test.js" "Spike Test" "spike-test"

echo ""
echo "${GREEN}=========================================="
echo "  ✓ TODAS LAS PRUEBAS COMPLETADAS"
echo "==========================================${NC}"
echo ""
echo "${CYAN}Resultados disponibles en:${NC}"
echo "  - Reportes JSON: ./load-tests/reports/"
echo "  - Grafana Dashboard: http://localhost:3000 (admin/admin)"
echo "  - InfluxDB: http://localhost:8086"
echo ""
echo "${YELLOW}Para generar gráficos PNG, ejecuta:${NC}"
echo "  docker-compose run --rm generate-graphs"
echo ""
echo "${GREEN}¡Listo! 🚀${NC}"
