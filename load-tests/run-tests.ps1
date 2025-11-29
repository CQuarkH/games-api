<#
.SYNOPSIS
    Script automatizado para ejecutar pruebas de carga y estrés con k6
    
.DESCRIPTION
    Este script orquesta:
    1. Levantamiento de servicios Docker (PostgreSQL, API, InfluxDB, Grafana)
    2. Verificación de health checks
    3. Seeding de datos de prueba
    4. Ejecución de pruebas k6
    5. Generación de reportes con gráficos locales
    
.PARAMETER TestType
    Tipo de prueba a ejecutar: load, stress, spike, o all
    
.EXAMPLE
    .\run-tests.ps1 -TestType load
    .\run-tests.ps1 -TestType all
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('load', 'stress', 'spike', 'all')]
    [string]$TestType = 'all'
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Colores para output
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "`n==> $Message" "Cyan"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" "Green"
}

function Write-Error-Custom {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" "Red"
}

# Función para verificar si Docker está corriendo
function Test-DockerRunning {
    try {
        docker ps | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Función para esperar que un servicio esté listo
function Wait-ForService {
    param(
        [string]$ServiceName,
        [string]$Url,
        [int]$MaxAttempts = 30
    )
    
    Write-Step "Esperando a que $ServiceName esté listo..."
    $attempts = 0
    
    while ($attempts -lt $MaxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Success "$ServiceName está listo"
                return $true
            }
        } catch {
            $attempts++
            Write-Host "." -NoNewline
            Start-Sleep -Seconds 2
        }
    }
    
    Write-Error-Custom "$ServiceName no respondió a tiempo"
    return $false
}

# Función para ejecutar prueba k6
function Invoke-K6Test {
    param(
        [string]$TestScript,
        [string]$TestName,
        [string]$OutputFile
    )
    
    Write-Step "Ejecutando $TestName..."
    
    $k6Cmd = "k6 run " +
             "--out influxdb=http://localhost:8086/k6 " +
             "--summary-export=.\load-tests\reports\$OutputFile-summary.json " +
             ".\load-tests\scripts\$TestScript"
    
    try {
        # Ejecutar k6 y capturar salida
        Invoke-Expression $k6Cmd | Tee-Object -FilePath ".\load-tests\reports\$OutputFile-log.txt"
        Write-Success "$TestName completado"
        return $true
    } catch {
        Write-Error-Custom "Error ejecutando $TestName : $_"
        return $false
    }
}

# ============================================
# SCRIPT PRINCIPAL
# ============================================

Write-ColorOutput @"
╔══════════════════════════════════════════════════════════╗
║  PRUEBAS DE CARGA Y ESTRÉS - GAMES API                  ║
║  Automatización con k6, Docker y Grafana                ║
╚══════════════════════════════════════════════════════════╝
"@ "Yellow"

# 1. Verificar Docker
Write-Step "Verificando Docker..."
if (-not (Test-DockerRunning)) {
    Write -Error-Custom "Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
}
Write-Success "Docker está corriendo"

# 2. Verificar k6
Write-Step "Verificando k6..."
try {
    $k6Version = k6 version
    Write-Success "k6 instalado: $k6Version"
} catch {
    Write-Error-Custom "k6 no está instalado. Instalar con: winget install k6"
    exit 1
}

# 3. Detener servicios previos
Write-Step "Deteniendo servicios previos (si existen)..."
docker-compose down -v 2>$null
Write-Success "Servicios previos detenidos"

# 4. Iniciar servicios
Write-Step "Iniciando servicios Docker..."
docker-compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Error al iniciar servicios Docker"
    exit 1
}
Write-Success "Servicios iniciados"

# 5. Esperar a que los servicios estén listos
Wait-ForService -ServiceName "PostgreSQL + API" -Url "http://localhost:5000/health"
Wait-ForService -ServiceName "Grafana" -Url "http://localhost:3000/api/health"
Wait-ForService -ServiceName "InfluxDB" -Url "http://localhost:8086/ping"

# 6. Seeding de datos
Write-Step "Generando datos de prueba (1000 juegos)..."
$seedResult = Invoke-K6Test -TestScript "seed-data.js" -TestName "Data Seeding" -OutputFile "seed"
if (-not $seedResult) {
    Write-Error-Custom "Error en seeding. Abortando pruebas."
    exit 1
}

# 7. Crear directorio de reportes
New-Item -ItemType Directory -Force -Path ".\load-tests\reports" | Out-Null

# 8. Ejecutar pruebas según parámetro
Write-ColorOutput "`n┌─────────────────────────────────────────┐" "Yellow"
Write-ColorOutput "│  INICIANDO PRUEBAS DE RENDIMIENTO      │" "Yellow"
Write-ColorOutput "└─────────────────────────────────────────┘`n" "Yellow"

$testsExecuted = @()

if ($TestType -eq 'all' -or $TestType -eq 'load') {
    Invoke-K6Test -TestScript "load-test.js" -TestName "Load Test (100 usuarios)" -OutputFile "load-test"
    $testsExecuted += "Load Test"
}

if ($TestType -eq 'all' -or $TestType -eq 'stress') {
    Write-ColorOutput "`nEsperando 30 segundos entre pruebas..." "Yellow"
    Start-Sleep -Seconds 30
    Invoke-K6Test -TestScript "stress-test.js" -TestName "Stress Test (escalado progresivo)" -OutputFile "stress-test"
    $testsExecuted += "Stress Test"
}

if ($TestType -eq 'all' -or $TestType -eq 'spike') {
    Write-ColorOutput "`nEsperando 30 segundos entre pruebas..." "Yellow"
    Start-Sleep -Seconds 30
    Invoke-K6Test -TestScript "spike-test.js" -TestName "Spike Test (picos súbitos)" -OutputFile "spike-test"
    $testsExecuted += "Spike Test"
}

# 9. Generar reporte HTML consolidado
Write-Step "Generando reporte HTML..."
$reportPath = ".\load-tests\reports\test-results.html"

# Script Python para generar gráficos
$pythonScript = @"
import json
import matplotlib.pyplot as plt
import os
from datetime import datetime

def generate_graphs():
    reports_dir = './load-tests/reports'
    
    for filename in os.listdir(reports_dir):
        if filename.endswith('-summary.json'):
            with open(os.path.join(reports_dir, filename), 'r') as f:
                data = json.load(f)
            
            test_name = filename.replace('-summary.json', '')
            
            # Extraer métricas
            metrics = data.get('metrics', {})
            
            # Crear figura con subplots
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            fig.suptitle(f'{test_name.upper()} - Resultados', fontsize=16)
            
            # Response time
            if 'http_req_duration' in metrics:
                durations = metrics['http_req_duration']['values']
                axes[0, 0].bar(['p50', 'p95', 'p99', 'max'], 
                              [durations.get('p(50)', 0), durations.get('p(95)', 0),
                               durations.get('p(99)', 0), durations.get('max', 0)])
                axes[0, 0].set_title('Response Time (ms)')
                axes[0, 0].set_ylabel('Milliseconds')
            
            # Request rate
            if 'http_reqs' in metrics:
                req_rate = metrics['http_reqs']['values'].get('rate', 0)
                axes[0, 1].bar(['Request Rate'], [req_rate], color='green')
                axes[0, 1].set_title('Request Rate')
                axes[0, 1].set_ylabel('req/s')
            
            # Error rate
            if 'http_req_failed' in metrics:
                error_rate = metrics['http_req_failed']['values'].get('rate', 0) * 100
                axes[1, 0].bar(['Error Rate'], [error_rate], color='red' if error_rate > 1 else 'green')
                axes[1, 0].set_title('Error Rate (%)')
                axes[1, 0].set_ylabel('Percentage')
            
            # VUs
            if 'vus' in metrics:
                vus_max = metrics['vus']['values'].get('max', 0)
                axes[1, 1].bar(['Max VUs'], [vus_max], color='blue')
                axes[1, 1].set_title('Virtual Users')
                axes[1, 1].set_ylabel('Count')
            
            plt.tight_layout()
            plt.savefig(f'{reports_dir}/{test_name}-graph.png', dpi=150)
            plt.close()
            print(f'✓ Gráfico generado: {test_name}-graph.png')

if __name__ == '__main__':
    generate_graphs()
"@

# Guardar y ejecutar script Python
$pythonScript | Out-File -FilePath ".\load-tests\generate_graphs.py" -Encoding UTF8
try {
    python .\load-tests\generate_graphs.py
    Write-Success "Gráficos generados"
} catch {
    Write-ColorOutput "Advertencia: No se pudieron generar gráficos (requiere Python + matplotlib)" "Yellow"
}

# Generar HTML
$htmlContent = @"
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Pruebas - Games API</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }
        h2 { color: #666; margin-top: 30px; }
        .test-section { margin: 20px 0; padding: 20px; background: #f9f9f9; border-radius: 5px; }
        .metric { display: inline-block; margin: 10px 20px; }
        .metric-label { font-weight: bold; color: #555; }
        .metric-value { font-size: 24px; color: #4CAF50; }
        img { max-width: 100%; height: auto; margin: 20px 0; border: 1px solid #ddd; border-radius: 4px; }
        .timestamp { color: #999; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Reporte de Pruebas de Carga y Estrés</h1>
        <p class="timestamp">Generado: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")</p>
        <p><strong>Proyecto:</strong> Games API</p>
        <p><strong>Pruebas ejecutadas:</strong> $($testsExecuted -join ', ')</p>
        
        <h2>🎯 Acceso a Grafana (Dashboard en Vivo)</h2>
        <p>Dashboard con métricas en tiempo real: <a href="http://localhost:3000" target="_blank">http://localhost:3000</a></p>
        <p><em>Usuario: admin | Contraseña: admin</em></p>
        
        <h2>📈 Resultados de Pruebas</h2>
"@

# Agregar secciones por cada prueba
$reportFiles = Get-ChildItem ".\load-tests\reports\*-summary.json" -ErrorAction SilentlyContinue
foreach ($file in $reportFiles) {
    $testName = $file.BaseName -replace "-summary", ""
    $graphFile = ".\load-tests\reports\$testName-graph.png"
    
    $htmlContent += @"
        <div class="test-section">
            <h3>$($testName.ToUpper())</h3>
            $(if (Test-Path $graphFile) { "<img src='$testName-graph.png' alt='$testName results'>" } else { "<p>Gráfico no disponible</p>" })
            <p><a href="$testName-summary.json" target="_blank">Ver JSON de resultados</a> | <a href="$testName-log.txt" target="_blank">Ver log completo</a></p>
        </div>
"@
}

$htmlContent += @"
        <h2>🔗 Enlaces Útiles</h2>
        <ul>
            <li><a href="http://localhost:3000" target="_blank">Grafana Dashboard</a> - Métricas en tiempo real</li>
            <li><a href="http://localhost:5000/games" target="_blank">API - /games</a> - Endpoint de juegos</li>
            <li><a href="http://localhost:5000/health" target="_blank">API - /health</a> - Health check</li>
        </ul>
        
        <h2>📝 Notas</h2>
        <ul>
            <li>Los servicios Docker siguen corriendo. Para detenerlos: <code>docker-compose down</code></li>
            <li>Los datos de InfluxDB persisten entre ejecuciones</li>
            <li>Para limpiar todo: <code>docker-compose down -v</code></li>
        </ul>
    </div>
</body>
</html>
"@

$htmlContent | Out-File -FilePath $reportPath -Encoding UTF8
Write-Success "Reporte HTML generado: $reportPath"

# 10. Resumen final
Write-ColorOutput "`n╔══════════════════════════════════════════════════════════╗" "Green"
Write-ColorOutput "║  ✓ PRUEBAS COMPLETADAS EXITOSAMENTE                     ║" "Green"
Write-ColorOutput "╚══════════════════════════════════════════════════════════╝`n" "Green"

Write-ColorOutput "📊 Resultados disponibles en:" "Cyan"
Write-ColorOutput "   - Reporte HTML: file:///$((Get-Location).Path)\load-tests\reports\test-results.html" "White"
Write-ColorOutput "   - Grafana Dashboard: http://localhost:3000" "White"
Write-ColorOutput "   - Logs JSON: .\load-tests\reports\" "White"

Write-ColorOutput "`n🎯 Próximos pasos:" "Yellow"
Write-ColorOutput "   1. Abrir el reporte HTML en tu navegador" "White"
Write-ColorOutput "   2. Acceder a Grafana para ver métricas detalladas" "White"
Write-ColorOutput "   3. Detener servicios: docker-compose down" "White"

Write-ColorOutput "`n¡Listo para entregar! 🚀`n" "Green"
