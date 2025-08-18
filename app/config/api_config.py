"""
Configuración de API para evitar importaciones circulares
"""
from flask_restx import Api

# Crear la instancia de API
api = Api(
    title='TruckGuard API',
    version='1.0',
    description='API para gestión de flota de camiones y seguimiento de viajes',
    doc='/docs',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Token en formato: Bearer <token>'
        }
    },
    security='Bearer'
)
