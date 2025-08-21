"""
Modelos Swagger para el recurso de autenticación
"""
from flask_restx import fields
from app.config.api_config import api

# Namespace para autenticación
auth_ns = api.namespace('Auth', description='Operaciones de autenticación')

# Modelos de entrada
login_model = api.model('Login', {
    'email': fields.String(required=True, description='Email del usuario', example='brunonicorc@hotmail.com'),
    'password': fields.String(required=True, description='Contraseña del usuario', example='1234')
})

register_model = api.model('Register', {
    'name': fields.String(required=True, description='Nombre del usuario', example='Juan'),
    'surname': fields.String(required=True, description='Apellido del usuario', example='Pérez'),
    'email': fields.String(required=True, description='Email del usuario', example='juan.perez@ejemplo.com'),
    'password': fields.String(required=True, description='Contraseña del usuario', example='miContraseña123'),
    'phone': fields.String(required=False, description='Número de teléfono', example='+1234567890')
})

# Modelos de respuesta
login_response_model = api.model('LoginResponse', {
    'id': fields.Integer(description='ID del usuario'),
    'email': fields.String(description='Email del usuario'),
    'access_token': fields.String(description='Token JWT para autenticación')
})

user_model = api.model('User', {
    'id': fields.Integer(description='ID del usuario'),
    'name': fields.String(description='Nombre del usuario'),
    'surname': fields.String(description='Apellido del usuario'),
    'email': fields.String(description='Email del usuario'),
    'rol': fields.String(description='Rol asignado (owner o driver)', enum=['owner', 'driver']),
    'phone': fields.String(description='Número de teléfono'),
    'status': fields.String(description='Estado del usuario', example='active')
})

error_model = api.model('Error', {
    'message': fields.String(description='Mensaje de error'),
    'error': fields.String(description='Detalles del error', required=False)
})

# Modelos adicionales para respuestas específicas
register_response_model = api.model('RegisterResponse', {
    'message': fields.String(description='Mensaje de confirmación'),
    'user': fields.Nested(user_model, description='Información del usuario registrado')
})

success_message_model = api.model('SuccessMessage', {
    'message': fields.String(description='Mensaje de confirmación')
})
