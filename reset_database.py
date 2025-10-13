#!/usr/bin/env python3
"""
Script para resetear la base de datos de TruckGuard
⚠️  ADVERTENCIA: Este script eliminará TODOS los datos de la base de datos
"""

import os
import sys
from dotenv import load_dotenv
from app import create_app, db
from app.models import *

def confirm_reset():
    """Solicita confirmación del usuario antes de resetear"""
    print("⚠️  ADVERTENCIA: Este script eliminará TODOS los datos de la base de datos")
    print("📊 Base de datos actual:", os.getenv('DATABASE_URL', 'No configurada'))
    
    response = input("\n¿Estás seguro de que quieres resetear la base de datos? (escribe 'RESET' para confirmar): ")
    
    if response != 'RESET':
        print("❌ Operación cancelada")
        return False
    
    print("\n🔄 Iniciando reset de la base de datos...")
    return True

def reset_database():
    """Resetea completamente la base de datos"""
    try:
        # Crear la aplicación
        app = create_app()
        
        with app.app_context():
            print("🗑️  Eliminando todas las tablas...")
            db.drop_all()
            
            print("🏗️  Recreando todas las tablas...")
            db.create_all()
            
            print("✅ Base de datos reseteada exitosamente!")
            print("📝 Todas las tablas han sido recreadas con la estructura actual")
            
    except Exception as e:
        print(f"❌ Error al resetear la base de datos: {str(e)}")
        sys.exit(1)

def main():
    """Función principal"""
    print("🚛 TruckGuard - Reset de Base de Datos")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Verificar que esté configurada la base de datos
    if not os.getenv('DATABASE_URL'):
        print("❌ Error: DATABASE_URL no está configurada en el archivo .env")
        sys.exit(1)
    
    # Confirmar antes de proceder
    if not confirm_reset():
        sys.exit(0)
    
    # Resetear la base de datos
    reset_database()

if __name__ == '__main__':
    main()
