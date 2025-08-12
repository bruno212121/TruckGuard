#!/usr/bin/env python3
"""
Script para ejecutar todos los tests de la API de TruckGuard

Este script ejecuta todos los tests de manera organizada y genera reportes
detallados de los resultados.

Uso:
    python test/api/run_tests.py
    python test/api/run_tests.py --verbose
    python test/api/run_tests.py --coverage

Autor: TruckGuard Test Suite
Fecha: 2025
"""

import sys
import os
import subprocess
import argparse
from datetime import datetime

def run_tests_with_pytest(verbose=False, coverage=False):
    """
    Ejecuta los tests usando pytest
    
    Args:
        verbose (bool): Si mostrar output detallado
        coverage (bool): Si generar reporte de cobertura
    """
    # Agregar el directorio raíz al path para importar módulos
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)
    
    # Detectar si estamos en un entorno virtual y usar la ruta correcta
    python_executable = 'python'
    if os.environ.get('VIRTUAL_ENV'):
        # Estamos en un entorno virtual, usar la ruta específica
        venv_path = os.environ['VIRTUAL_ENV']
        if os.name == 'nt':  # Windows
            python_executable = os.path.join(venv_path, 'Scripts', 'python.exe')
        else:  # Unix/Linux/Mac
            python_executable = os.path.join(venv_path, 'bin', 'python')
    
    # Configurar comandos de pytest
    cmd = [python_executable, '-m', 'pytest']
    
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=app', '--cov-report=html', '--cov-report=term'])
    
    # Agregar el directorio de tests
    cmd.append('test/api/')
    
    # Agregar opciones adicionales
    cmd.extend([
        '--tb=short',  # Formato corto de traceback
        '--strict-markers',  # Marcadores estrictos
        '--disable-warnings',  # Deshabilitar warnings
        '--color=yes'  # Colores en la salida
    ])
    
    print(f"Ejecutando tests con comando: {' '.join(cmd)}")
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    try:
        result = subprocess.run(cmd, cwd=project_root, check=False)
        return result.returncode
    except Exception as e:
        print(f"Error ejecutando tests: {e}")
        return 1

def run_specific_test_module(module_name, verbose=False):
    """
    Ejecuta un módulo específico de tests
    
    Args:
        module_name (str): Nombre del módulo a ejecutar
        verbose (bool): Si mostrar output detallado
    """
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)
    
    # Detectar si estamos en un entorno virtual y usar la ruta correcta
    python_executable = 'python'
    if os.environ.get('VIRTUAL_ENV'):
        # Estamos en un entorno virtual, usar la ruta específica
        venv_path = os.environ['VIRTUAL_ENV']
        if os.name == 'nt':  # Windows
            python_executable = os.path.join(venv_path, 'Scripts', 'python.exe')
        else:  # Unix/Linux/Mac
            python_executable = os.path.join(venv_path, 'bin', 'python')
    
    cmd = [python_executable, '-m', 'pytest']
    
    if verbose:
        cmd.append('-v')
    
    # Agregar el módulo específico
    cmd.append(f'test/api/{module_name}')
    
    cmd.extend([
        '--tb=short',
        '--strict-markers',
        '--disable-warnings',
        '--color=yes'
    ])
    
    print(f"Ejecutando módulo específico: {module_name}")
    print(f"Comando: {' '.join(cmd)}")
    print("-" * 80)
    
    try:
        result = subprocess.run(cmd, cwd=project_root, check=False)
        return result.returncode
    except Exception as e:
        print(f"Error ejecutando módulo {module_name}: {e}")
        return 1

def show_test_summary():
    """
    Muestra un resumen de los tests disponibles
    """
    print("📋 RESUMEN DE TESTS DISPONIBLES")
    print("=" * 50)
    
    test_modules = [
        ("test_auth_routes.py", "Tests de autenticación (login/register)"),
        ("test_truck_routes.py", "Tests de gestión de camiones"),
        ("test_trip_routes.py", "Tests de gestión de viajes"),
        ("test_maintenance_routes.py", "Tests de mantenimiento"),
        ("test_user_routes.py", "Tests de gestión de usuarios"),
        ("test_fleet_analytics_routes.py", "Tests de análisis de flota")
    ]
    
    for module, description in test_modules:
        print(f"🔹 {module:<30} - {description}")
    
    print("\n📊 ESTADÍSTICAS DE TESTS")
    print("=" * 30)
    
    total_tests = 0
    for module, _ in test_modules:
        module_path = os.path.join(os.path.dirname(__file__), module)
        if os.path.exists(module_path):
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
                test_count = content.count('def test_')
                total_tests += test_count
                print(f"🔸 {module:<30} - {test_count:>3} tests")
    
    print(f"\n📈 Total de tests: {total_tests}")

def main():
    """
    Función principal del script
    """
    parser = argparse.ArgumentParser(
        description='Ejecuta los tests de la API de TruckGuard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python test/api/run_tests.py                    # Ejecutar todos los tests
  python test/api/run_tests.py --verbose          # Ejecutar con output detallado
  python test/api/run_tests.py --coverage         # Ejecutar con reporte de cobertura
  python test/api/run_tests.py --module auth      # Ejecutar solo tests de auth
  python test/api/run_tests.py --summary          # Mostrar resumen de tests
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mostrar output detallado'
    )
    
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Generar reporte de cobertura'
    )
    
    parser.add_argument(
        '--module', '-m',
        type=str,
        help='Ejecutar solo un módulo específico (ej: auth, truck, trip)'
    )
    
    parser.add_argument(
        '--summary', '-s',
        action='store_true',
        help='Mostrar resumen de tests disponibles'
    )
    
    args = parser.parse_args()
    
    print("🚛 TruckGuard API Test Suite")
    print("=" * 40)
    
    if args.summary:
        show_test_summary()
        return 0
    
    if args.module:
        # Mapear nombres cortos a nombres de archivo
        module_mapping = {
            'auth': 'test_auth_routes.py',
            'truck': 'test_truck_routes.py',
            'trip': 'test_trip_routes.py',
            'maintenance': 'test_maintenance_routes.py',
            'user': 'test_user_routes.py',
            'fleet': 'test_fleet_analytics_routes.py'
        }
        
        module_file = module_mapping.get(args.module.lower())
        if not module_file:
            print(f"❌ Módulo '{args.module}' no encontrado")
            print("Módulos disponibles:", ', '.join(module_mapping.keys()))
            return 1
        
        return run_specific_test_module(module_file, args.verbose)
    else:
        return run_tests_with_pytest(args.verbose, args.coverage)

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
