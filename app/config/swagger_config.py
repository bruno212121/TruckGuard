"""
Configuración de Swagger para TruckGuard API
"""

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "TruckGuard API",
        "description": "API for Truck Fleet Management and Trip Tracking",
        "version": "1.0.0",
        "contact": {
            "name": "TruckGuard Team",
            "email": "support@truckguard.com"
        }
    },
    "host": "localhost:8000",
    "basePath": "/",
    "schemes": ["http", "https"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Token en formato: Bearer <token>"
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ],
    "tags": [
        {
            "name": "Auth",
            "description": "Operaciones de autenticación"
        },
        {
            "name": "Trucks",
            "description": "Gestión de camiones"
        },
        {
            "name": "Trips",
            "description": "Gestión de viajes"
        },
        {
            "name": "Maintenance",
            "description": "Gestión de mantenimiento"
        },
        {
            "name": "Analytics",
            "description": "Análisis de flota"
        }
    ]
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}
