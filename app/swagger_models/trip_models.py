"""
Modelos Swagger para el recurso de trips
"""
from flask_restx import fields
from app.config.api_config import api


trip_ns = api.namespace('Trips', description='Operaciones de gestión de viajes')


# Modelos de entrada
create_trip_model = api.model('CreateTrip', {
    'origin': fields.String(required=True, description='Origen del viaje', example='Madrid'),
    'destination': fields.String(required=True, description='Destino del viaje', example='Barcelona'),
    'truck_id': fields.Integer(required=True, description='ID del camión', example=1),
    'driver_id': fields.Integer(required=True, description='ID del conductor', example=1),
    'status': fields.String(required=True, description='Estado del viaje', example='Active'),
    'date': fields.DateTime(required=True, description='Fecha del viaje', example='2024-01-15T10:00:00'),
    'updated_at': fields.DateTime(required=False, description='Fecha de actualización del viaje'),
    'created_at': fields.DateTime(required=False, description='Fecha de creación del viaje')
})

edit_trip_model = api.model('EditTrip', {
    'origin': fields.String(required=False, description='Origen del viaje', example='Madrid'),
    'destination': fields.String(required=False, description='Destino del viaje', example='Barcelona'),
    'truck_id': fields.Integer(required=False, description='ID del camión', example=1),
    'driver_id': fields.Integer(required=False, description='ID del conductor', example=1),
    'status': fields.String(required=False, description='Estado del viaje', example='Completed'),
    'date': fields.DateTime(required=False, description='Fecha del viaje', example='2024-01-15T10:00:00')
})

# Modelos de respuesta
truck_info_model = api.model('TruckInfo', {
    'truck_id': fields.Integer(description='ID del camión'),
    'plate': fields.String(description='Matrícula del camión'),
    'model': fields.String(description='Modelo del camión'),
    'brand': fields.String(description='Marca del camión')
})

driver_info_model = api.model('DriverInfo', {
    'id': fields.Integer(description='ID del conductor'),
    'name': fields.String(description='Nombre del conductor'),
    'surname': fields.String(description='Apellido del conductor'),
    'email': fields.String(description='Email del conductor'),
    'phone': fields.String(description='Teléfono del conductor')
})

trip_response_model = api.model('TripResponse', {
    'trip_id': fields.Integer(description='ID del viaje'),
    'origin': fields.String(description='Origen del viaje'),
    'destination': fields.String(description='Destino del viaje'),
    'status': fields.String(description='Estado del viaje'),
    'date': fields.DateTime(description='Fecha del viaje'),
    'created_at': fields.DateTime(description='Fecha de creación'),
    'updated_at': fields.DateTime(description='Fecha de última actualización'),
    'truck': fields.Nested(truck_info_model, description='Información del camión'),
    'driver': fields.Nested(driver_info_model, description='Información del conductor')
})

trip_detail_model = api.model('TripDetail', {
    'trip_id': fields.Integer(description='ID del viaje'),
    'origin': fields.String(description='Origen del viaje'),
    'destination': fields.String(description='Destino del viaje'),
    'status': fields.String(description='Estado del viaje'),
    'date': fields.String(description='Fecha del viaje'),
    'created_at': fields.String(description='Fecha de creación'),
    'updated_at': fields.String(description='Fecha de última actualización'),
    'truck': fields.Raw(description='Información del camión o "No truck assigned"'),
    'driver': fields.Raw(description='Información del conductor o "No driver assigned"')
})

trip_list_model = api.model('TripList', {
    'trips': fields.List(fields.Nested(trip_response_model), description='Lista de viajes')
})

create_trip_response_model = api.model('CreateTripResponse', {
    'message': fields.String(description='Mensaje de confirmación'),
    'trip': fields.Integer(description='ID del viaje creado')
})

success_message_model = api.model('SuccessMessage', {
    'message': fields.String(description='Mensaje de confirmación'),
    'trip': fields.Integer(description='ID del viaje')
})

# Modelos para filtros y búsquedas
trip_filter_model = api.model('TripFilter', {
    'status': fields.String(required=False, description='Filtrar por estado', example='Active'),
    'driver_id': fields.Integer(required=False, description='Filtrar por conductor', example=1),
    'truck_id': fields.Integer(required=False, description='Filtrar por camión', example=1),
    'date_from': fields.DateTime(required=False, description='Fecha desde', example='2024-01-01T00:00:00'),
    'date_to': fields.DateTime(required=False, description='Fecha hasta', example='2024-12-31T23:59:59')
})