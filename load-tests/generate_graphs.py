"""
Generador de Reportes HTML y Gráficos para k6
Genera gráficos PNG y un reporte HTML completo desde resultados JSON de k6
"""

import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from pathlib import Path
from datetime import datetime

def load_test_summary(filename):
    """Carga el archivo JSON de resumen de k6"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error cargando {filename}: {e}")
        return None

def calculate_error_rate(metrics):
    """Calcula la tasa de error correctamente desde las métricas de k6"""
    # k6 usa http_req_failed con passes/fails
    if 'http_req_failed' in metrics:
        failed_metric = metrics['http_req_failed']
        # passes = 0 significa que las requests FALLARON
        # fails = cuenta de requests exitosas (confuso pero así es k6)
        # Actualización: revisar la estructura real
        if 'passes' in failed_metric and 'fails' in failed_metric:
            total = failed_metric['passes'] + failed_metric['fails']
            if total > 0:
                # passes en http_req_failed = requests que NO fallaron
                # fails en http_req_failed = requests que SÍ fallaron  
                error_count = failed_metric['fails']
                return (error_count / total) * 100
    
    # Fallback: checks
    if 'checks' in metrics:
        checks = metrics['checks']
        passes = checks.get('passes', 0)
        fails = checks.get('fails', 0)
        total = passes + fails
        if total > 0:
            return (fails / total) * 100
    
    return 0.0

def generate_metrics_graph(metrics, test_name, output_path):
    """Genera gráfico de métricas"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'{test_name} - Resultados', fontsize=16, fontweight='bold')
    
    # 1. Response Time
    ax1 = axes[0, 0]
    if 'http_req_duration' in metrics:
        dur = metrics['http_req_duration']
        labels = ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)']
        values = [dur.get('avg', 0), dur.get('min', 0), dur.get('med', 0), 
                  dur.get('max', 0), dur.get('p(90)', 0), dur.get('p(95)', 0)]
        bars = ax1.bar(labels, values, color=['#2196F3', '#4CAF50', '#8BC34A', 
                                                '#FF9800', '#FF5722', '#F44336'])
        ax1.set_title('Tiempos de Respuesta (ms)', fontweight='bold')
        ax1.set_ylabel('Milisegundos')
        ax1.grid(axis='y', alpha=0.3)
        for bar, val in zip(bars, values):
            ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                    f'{val:.1f}', ha='center', va='bottom', fontsize=9)
    
    # 2. Throughput
    ax2 = axes[0, 1]
    if 'http_reqs' in metrics:
        total = metrics['http_reqs'].get('count', 0)
        rate = metrics['http_reqs'].get('rate', 0)
        ax2.bar(['Total Requests', 'Rate (req/s)'], [total, rate*10], 
                color=['#3F51B5', '#009688'])
        ax2.set_title('Throughput', fontweight='bold')
        ax2.set_ylabel('Cantidad')
        ax2.grid(axis='y', alpha=0.3)
        ax2.text(0, total, f'{int(total)}', ha='center', va='bottom', fontweight='bold')
        ax2.text(1, rate*10, f'{rate:.1f} req/s', ha='center', va='bottom', fontweight='bold')
    
    # 3. Success vs Errors
    ax3 = axes[1, 0]
    error_rate = calculate_error_rate(metrics)
    success_rate = 100 - error_rate
    
    colors = ['#F44336' if error_rate > 1 else '#4CAF50', '#4CAF50']
    bars = ax3.bar(['Errores', 'Éxitos'], [error_rate, success_rate], color=colors)
    ax3.set_title('Tasa de Éxito/Error', fontweight='bold')
    ax3.set_ylabel('Porcentaje (%)')
    ax3.set_ylim([0, 105])
    ax3.grid(axis='y', alpha=0.3)
    
    # Ajustar posición del texto para evitar que quede fuera
    error_text_y = max(error_rate, 3)
    ax3.text(0, error_text_y, f'{error_rate:.1f}%', ha='center', va='bottom', fontweight='bold')
    ax3.text(1, success_rate, f'{success_rate:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 4. Virtual Users
    ax4 = axes[1, 1]
    if 'vus' in metrics:
        vus_max = metrics['vus'].get('max', 0)
        vus_min = metrics['vus'].get('min', 0)
        ax4.bar(['Max VUs', 'Min VUs'], [vus_max, vus_min], color=['#9C27B0', '#E1BEE7'])
        ax4.set_title('Usuarios Virtuales', fontweight='bold')
        ax4.set_ylabel('Cantidad')
        ax4.grid(axis='y', alpha=0.3)
        ax4.text(0, vus_max, f'{int(vus_max)}', ha='center', va='bottom', fontweight='bold')
        ax4.text(1, vus_min, f'{int(vus_min)}', ha='center', va='bottom', fontweight='bold')
    elif 'vus_max' in metrics:
        vus_val = metrics['vus_max'].get('value', 0)
        ax4.bar(['VUs'], [vus_val], color=['#9C27B0'])
        ax4.set_title('Usuarios Virtuales', fontweight='bold')
        ax4.set_ylabel('Cantidad')
        ax4.grid(axis='y', alpha=0.3)
        ax4.text(0, vus_val, f'{int(vus_val)}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Gráfico: {output_path.name}")

def generate_html_report(test_results, output_path):
    """Genera reporte HTML completo"""
    html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Pruebas de Carga - Games API</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 { font-size: 2.5em; margin-bottom: 10px; }
        .timestamp { font-size: 0.9em; opacity: 0.9; }
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .card h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        .card .value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        .card .label {
            color: #666;
            font-size: 0.9em;
        }
        .test-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .test-section h2 {
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .metrics-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .metrics-table th {
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #dee2e6;
        }
        .metrics-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #dee2e6;
        }
        .metrics-table tr:hover {
            background: #f8f9fa;
        }
        .graph {
            margin: 20px 0;
            text-align: center;
        }
        .graph img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        .status-success { background: #d4edda; color: #155724; }
        .status-warning { background: #fff3cd; color: #856404; }
        .status-error { background: #f8d7da; color: #721c24; }
        footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Reporte de Pruebas de Carga y Estrés</h1>
            <p class="timestamp">Generado: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            <p>Games API - Sistema de Gestión de Juegos</p>
        </header>
"""
    
    # Summary cards
    total_tests = len(test_results)
    total_requests = sum(r['metrics'].get('http_reqs', {}).get('count', 0) for r in test_results)
    avg_error_rate = sum(calculate_error_rate(r['metrics']) for r in test_results) / total_tests if total_tests > 0 else 0
    
    html += f"""
        <div class="summary-cards">
            <div class="card">
                <h3>Pruebas Ejecutadas</h3>
                <div class="value">{total_tests}</div>
                <div class="label">Tests completados</div>
            </div>
            <div class="card">
                <h3>Total Requests</h3>
                <div class="value">{int(total_requests)}</div>
                <div class="label">Peticiones procesadas</div>
            </div>
            <div class="card">
                <h3>Tasa de Error Promedio</h3>
                <div class="value">{avg_error_rate:.2f}%</div>
                <div class="label">Across all tests</div>
            </div>
        </div>
"""
    
    # Test sections
    for result in test_results:
        test_name = result['name']
        metrics = result['metrics']
        graph_path = result.get('graph_path', '')
        
        error_rate = calculate_error_rate(metrics)
        status_class = 'status-success' if error_rate < 1 else ('status-warning' if error_rate < 5 else 'status-error')
        status_text = 'Exitoso' if error_rate < 1 else ('Aceptable' if error_rate < 5 else 'Con Errores')
        
        html += f"""
        <div class="test-section">
            <h2>{test_name} <span class="{status_class} status-badge">{status_text}</span></h2>
"""
        
        # Metrics table
        if 'http_req_duration' in metrics:
            dur = metrics['http_req_duration']
            html += """
            <h3>Tiempos de Respuesta</h3>
            <table class="metrics-table">
                <tr>
                    <th>Métrica</th>
                    <th>Valor (ms)</th>
                </tr>
"""
            for key in ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)']:
                if key in dur:
                    html += f"""
                <tr><td>{key}</td><td>{dur[key]:.2f} ms</td></tr>
"""
            html += "</table>"
        
        if 'http_reqs' in metrics:
            reqs = metrics['http_reqs']
            html += f"""
            <h3>Throughput</h3>
            <table class="metrics-table">
                <tr><th>Métrica</th><th>Valor</th></tr>
                <tr><td>Total Requests</td><td>{reqs.get('count', 0)}</td></tr>
                <tr><td>Request Rate</td><td>{reqs.get('rate', 0):.2f} req/s</td></tr>
            </table>
"""
        
        html += f"""
            <h3>Tasa de Éxito</h3>
            <table class="metrics-table">
                <tr><th>Métrica</th><th>Valor</th></tr>
                <tr><td>Error Rate</td><td>{error_rate:.2f}%</td></tr>
                <tr><td>Success Rate</td><td>{100 - error_rate:.2f}%</td></tr>
            </table>
"""
        
        if graph_path and Path(graph_path).exists():
            html += f"""
            <div class="graph">
                <h3>Gráficos de Rendimiento</h3>
                <img src="{Path(graph_path).name}" alt="{test_name} Results">
            </div>
"""
        
        html += "</div>"
    
    html += """
        <footer>
            <p>Reporte generado automáticamente por el sistema de pruebas de carga</p>
            <p>Games API - Pruebas con k6 y Docker</p>
        </footer>
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Reporte HTML: {output_path}")

def process_all_tests():
    """Procesa todos los tests y genera gráficos + HTML"""
    reports_dir = Path('./load-tests/reports')
    
    if not reports_dir.exists():
        print(f"❌ Directorio {reports_dir} no existe")
        return
    
    summary_files = list(reports_dir.glob('*-summary.json'))
    
    if not summary_files:
        print("⚠️  No se encontraron archivos de resumen")
        return
    
    print(f"\n📊 Procesando {len(summary_files)} pruebas...\n")
    
    test_results = []
    
    for summary_file in sorted(summary_files):
        test_name = summary_file.stem.replace('-summary', '').replace('-', ' ').title()
        print(f"Procesando: {test_name}")
        
        data = load_test_summary(summary_file)
        if data is None:
            continue
        
        metrics = data.get('metrics', {})
        
        # Generar gráfico
        graph_path = reports_dir / f"{summary_file.stem.replace('-summary', '')}-graph.png"
        generate_metrics_graph(metrics, test_name, graph_path)
        
        test_results.append({
            'name': test_name,
            'metrics': metrics,
            'graph_path': str(graph_path)
        })
    
    # Generar HTML
    if test_results:
        html_path = reports_dir / 'test-results.html'
        generate_html_report(test_results, html_path)
    
    print(f"\n✅ Procesamiento completado")
    print(f"📁 Resultados en: {reports_dir}")
    print(f"🌐 Abrir: {reports_dir / 'test-results.html'}")

if __name__ == '__main__':
    process_all_tests()
