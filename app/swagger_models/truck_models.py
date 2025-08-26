"""
Modelos Swagger para el recurso de trucks
"""
from flask_restx import fields
from app.config.api_config import api

# Namespace para trucks
truck_ns = api.namespace('Trucks', description='Operaciones de gestión de camiones')

# Modelo para componentes de mantenimiento
component_model = api.model('Component', {
    'name': fields.String(required=True, description='Nombre del componente', example='Filtros'),
    'interval': fields.Integer(required=True, description='Intervalo de mantenimiento en km', example=10000),
    'status': fields.String(required=False, description='Estado del componente', example='Excellent', enum=['Excellent', 'Good', 'Fair', 'Poor', 'Critical']),
    'last_maintenance_mileage': fields.Integer(required=False, description='Último kilometraje de mantenimiento', example=40000),
    'next_maintenance_mileage': fields.Integer(required=False, description='Próximo kilometraje de mantenimiento', example=50000)
})

# Modelos de entrada
create_truck_model = api.model('CreateTruck', {
    'driver_id': fields.Integer(required=False, description='ID del conductor asignado', example=1),
    'plate': fields.String(required=True, description='Matrícula del camión', example='ABC123'),
    'model': fields.String(required=True, description='Modelo del camión', example='FH16'),
    'brand': fields.String(required=True, description='Marca del camión', example='Volvo'),
    'year': fields.Integer(required=True, description='Año del camión', example=2020),
    'color': fields.String(required=True, description='Color del camión', example='Blanco'),
    'mileage': fields.Integer(required=True, description='Kilometraje actual', example=50000),
    'health_status': fields.String(required=False, description='Estado de salud del camión', example='Excellent'),
    'fleetanalytics_id': fields.Integer(required=False, description='ID de análisis de flota', example=1),
    'components': fields.List(fields.Nested(component_model), required=False, description='Lista de componentes con estado personalizado')
})

edit_truck_model = api.model('EditTruck', {
    'status': fields.String(required=False, description='Estado del camión', example='Active'),
    'created_at': fields.DateTime(required=False, description='Fecha de creación')
})

assign_truck_model = api.model('AssignTruck', {
    'driver_id': fields.Integer(required=True, description='ID del conductor a asignar', example=1)
})

# Modelos de respuesta
driver_model = api.model('Driver', {
    'id': fields.Integer(description='ID del conductor'),
    'name': fields.String(description='Nombre del conductor'),
    'surname': fields.String(description='Apellido del conductor'),
    'email': fields.String(description='Email del conductor'),
    'phone': fields.String(description='Teléfono del conductor'),
    'role': fields.String(description='Rol del conductor')
})

truck_response_model = api.model('TruckResponse', {
    'truck_id': fields.Integer(description='ID del camión'),
    'plate': fields.String(description='Matrícula del camión'),
    'model': fields.String(description='Modelo del camión'),
    'brand': fields.String(description='Marca del camión'),
    'year': fields.Integer(description='Año del camión'),
    'mileage': fields.Integer(description='Kilometraje actual'),
    'color': fields.String(description='Color del camión'),
    'status': fields.String(description='Estado del camión'),
    'updated_at': fields.DateTime(description='Fecha de última actualización'),
    'driver': fields.Nested(driver_model, description='Información del conductor')
})

truck_detail_model = api.model('TruckDetail', {
    'truck_id': fields.Integer(description='ID del camión'),
    'plate': fields.String(description='Matrícula del camión'),
    'model': fields.String(description='Modelo del camión'),
    'brand': fields.String(description='Marca del camión'),
    'year': fields.Integer(description='Año del camión'),
    'mileage': fields.Integer(description='Kilometraje actual'),
    'color': fields.String(description='Color del camión'),
    'status': fields.String(description='Estado del camión'),
    'updated_at': fields.String(description='Fecha de última actualización'),
    'driver': fields.Raw(description='Información del conductor o "No driver assigned"')
})

truck_list_model = api.model('TruckList', {
    'trucks': fields.List(fields.Nested(truck_response_model), description='Lista de camiones')
})

create_truck_response_model = api.model('CreateTruckResponse', {
    'message': fields.String(description='Mensaje de confirmación'),
    'truck': fields.Integer(description='ID del camión creado')
})

assign_truck_response_model = api.model('AssignTruckResponse', {
    'message': fields.String(description='Mensaje de confirmación'),
    'truck': fields.String(description='Modelo del camión'),
    'Name driver': fields.String(description='Nombre del conductor'),
    'Surname driver': fields.String(description='Apellido del conductor')
})

drivers_without_truck_model = api.model('DriversWithoutTruck', {
    'id': fields.Integer(description='ID del conductor'),
    'name': fields.String(description='Nombre del conductor'),
    'surname': fields.String(description='Apellido del conductor'),
    'phone': fields.String(description='Teléfono del conductor'),
    'role': fields.String(description='Rol del conductor')
})

drivers_list_model = api.model('DriversList', {
    'drivers': fields.List(fields.Nested(drivers_without_truck_model), description='Lista de conductores sin camión')
})

success_message_model = api.model('SuccessMessage', {
    'message': fields.String(description='Mensaje de confirmación'),
    'truck': fields.Integer(description='ID del camión')
})
