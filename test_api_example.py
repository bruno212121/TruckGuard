#!/usr/bin/env python3
"""
Ejemplo de ejecución de tests para TruckGuard API

Este script demuestra cómo ejecutar los tests de manera programática
y muestra los resultados de forma organizada.

Autor: TruckGuard Test Suite
Fecha: 2025
"""

import subprocess
import sys
import os
from datetime import datetime

def run_test_example():
    """
    Ejemplo de ejecución de tests
    """
    print("🚛 TruckGuard API - Ejemplo de Ejecución de Tests")
    print("=" * 60)
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('app.py'):
        print("❌ Error: No se encontró app.py. Asegúrate de estar en el directorio raíz del proyecto.")
        return 1
    
    # Verificar que existe el directorio de tests
    if not os.path.exists('test/api'):
        print("❌ Error: No se encontró el directorio test/api. Ejecuta primero la creación de tests.")
        return 1
    
    print("📋 Ejecutando tests de autenticación...")
    print("-" * 40)
    
    # Ejecutar tests de autenticación
    result = subprocess.run([
        'python', 'test/api/run_tests.py', '--module', 'auth', '--verbose'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Tests de autenticación completados exitosamente")
    else:
        print("❌ Tests de autenticación fallaron")
        print("Output:", result.stdout)
        print("Errores:", result.stderr)
    
    print()
    print("📋 Ejecutando tests de camiones...")
    print("-" * 40)
    
    # Ejecutar tests de camiones
    result = subprocess.run([
        'python', 'test/api/run_tests.py', '--module', 'truck', '--verbose'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Tests de camiones completados exitosamente")
    else:
        print("❌ Tests de camiones fallaron")
        print("Output:", result.stdout)
        print("Errores:", result.stderr)
    
    print()
    print("📋 Mostrando resumen de tests...")
    print("-" * 40)
    
    # Mostrar resumen
    result = subprocess.run([
        'python', 'test/api/run_tests.py', '--summary'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("❌ Error al mostrar resumen")
        print("Errores:", result.stderr)
    
    print()
    print("🎉 Ejemplo completado!")
    print()
    print("💡 Para ejecutar todos los tests:")
    print("   python test/api/run_tests.py")
    print()
    print("💡 Para ejecutar con cobertura:")
    print("   python test/api/run_tests.py --coverage")
    print()
    print("💡 Para más opciones:")
    print("   python test/api/run_tests.py --help")
    
    return 0

if __name__ == '__main__':
    exit_code = run_test_example()
    sys.exit(exit_code)
