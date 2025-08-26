"""
Modelos Swagger para el recurso de maintenance
"""
from flask_restx import fields
from app.config.api_config import api

# Namespace para maintenance
maintenance_ns = api.namespace('Maintenance', description='Operaciones de gestión de mantenimiento')

# Modelos de entrada
create_maintenance_model = api.model('CreateMaintenance', {
    'description': fields.String(required=True, description='Descripción del mantenimiento', example='Cambio de aceite'),
    'status': fields.String(required=True, description='Estado del mantenimiento', example='Pending'),
    'component': fields.String(required=True, description='Componente a mantener', example='Aceite'),
    'cost': fields.Float(required=True, description='Costo del mantenimiento', example=150.50),
    'mileage_interval': fields.Integer(required=True, description='Intervalo de kilometraje', example=5000),
    'last_maintenance_mileage': fields.Integer(required=False, description='Último kilometraje de mantenimiento', example=45000),
    'next_maintenance_mileage': fields.Integer(required=False, description='Próximo kilometraje de mantenimiento', example=50000),
    'truck_id': fields.Integer(required=True, description='ID del camión', example=1),
    'driver_id': fields.Integer(required=True, description='ID del conductor', example=1),
    'maintenance_interval': fields.Integer(required=True, description='Intervalo de mantenimiento', example=5000)
})

edit_maintenance_model = api.model('EditMaintenance', {
    'description': fields.String(required=False, description='Descripción del mantenimiento'),
    'status': fields.String(required=False, description='Estado del mantenimiento'),
    'component': fields.String(required=False, description='Componente a mantener'),
    'cost': fields.Float(required=False, description='Costo del mantenimiento'),
    'mileage_interval': fields.Integer(required=False, description='Intervalo de kilometraje'),
    'last_maintenance_mileage': fields.Integer(required=False, description='Último kilometraje de mantenimiento'),
    'next_maintenance_mileage': fields.Integer(required=False, description='Próximo kilometraje de mantenimiento'),
    'maintenance_interval': fields.Integer(required=False, description='Intervalo de mantenimiento')
})

approve_maintenance_model = api.model('ApproveMaintenance', {
    'approval_status': fields.String(required=True, description='Estado de aprobación', 
                                   enum=['Approved', 'Rejected'], example='Approved')
})

# Modelos de respuesta
truck_info_model = api.model('TruckInfo', {
    'truck_id': fields.Integer(description='ID del camión'),
    'plate': fields.String(description='Matrícula del camión'),
    'model': fields.String(description='Modelo del camión'),
    'brand': fields.String(description='Marca del camión'),
    'mileage': fields.Integer(description='Kilometraje actual')
})

driver_info_model = api.model('DriverInfo', {
    'id': fields.Integer(description='ID del conductor'),
    'name': fields.String(description='Nombre del conductor'),
    'surname': fields.String(description='Apellido del conductor'),
    'email': fields.String(description='Email del conductor')
})

maintenance_response_model = api.model('MaintenanceResponse', {
    'maintenance_id': fields.Integer(description='ID del mantenimiento'),
    'description': fields.String(description='Descripción del mantenimiento'),
    'status': fields.String(description='Estado del mantenimiento'),
    'component': fields.String(description='Componente a mantener'),
    'cost': fields.Float(description='Costo del mantenimiento'),
    'mileage_interval': fields.Integer(description='Intervalo de kilometraje'),
    'last_maintenance_mileage': fields.Integer(description='Último kilometraje de mantenimiento'),
    'next_maintenance_mileage': fields.Integer(description='Próximo kilometraje de mantenimiento'),
    'created_at': fields.DateTime(description='Fecha de creación'),
    'updated_at': fields.DateTime(description='Fecha de última actualización'),
    'truck': fields.Nested(truck_info_model, description='Información del camión'),
    'driver': fields.Nested(driver_info_model, description='Información del conductor')
})

maintenance_detail_model = api.model('MaintenanceDetail', {
    'maintenance_id': fields.Integer(description='ID del mantenimiento'),
    'description': fields.String(description='Descripción del mantenimiento'),
    'status': fields.String(description='Estado del mantenimiento'),
    'component': fields.String(description='Componente a mantener'),
    'cost': fields.Float(description='Costo del mantenimiento'),
    'mileage_interval': fields.Integer(description='Intervalo de kilometraje'),
    'last_maintenance_mileage': fields.Integer(description='Último kilometraje de mantenimiento'),
    'next_maintenance_mileage': fields.Integer(description='Próximo kilometraje de mantenimiento'),
    'created_at': fields.String(description='Fecha de creación'),
    'updated_at': fields.String(description='Fecha de última actualización'),
    'truck': fields.Raw(description='Información del camión o "No truck assigned"'),
    'driver': fields.Raw(description='Información del conductor o "No driver assigned"')
})

maintenance_list_model = api.model('MaintenanceList', {
    'maintenances': fields.List(fields.Nested(maintenance_response_model), description='Lista de mantenimientos')
})

create_maintenance_response_model = api.model('CreateMaintenanceResponse', {
    'message': fields.String(description='Mensaje de confirmación'),
    'maintenance': fields.Integer(description='ID del mantenimiento creado')
})

success_message_model = api.model('SuccessMessage', {
    'message': fields.String(description='Mensaje de confirmación'),
    'maintenance': fields.Integer(description='ID del mantenimiento')
})

# Modelos para filtros y búsquedas
maintenance_filter_model = api.model('MaintenanceFilter', {
    'status': fields.String(required=False, description='Filtrar por estado', example='Pending'),
    'component': fields.String(required=False, description='Filtrar por componente', example='Aceite'),
    'truck_id': fields.Integer(required=False, description='Filtrar por camión', example=1),
    'driver_id': fields.Integer(required=False, description='Filtrar por conductor', example=1)
})

# Modelos para estadísticas
maintenance_stats_model = api.model('MaintenanceStats', {
    'total_maintenances': fields.Integer(description='Total de mantenimientos'),
    'pending_maintenances': fields.Integer(description='Mantenimientos pendientes'),
    'completed_maintenances': fields.Integer(description='Mantenimientos completados'),
    'total_cost': fields.Float(description='Costo total de mantenimientos'),
    'average_cost': fields.Float(description='Costo promedio por mantenimiento')
})

# Modelo para respuesta de actualización de estado
update_status_response_model = api.model('UpdateStatusResponse', {
    'message': fields.String(description='Mensaje de confirmación'),
    'truck_id': fields.Integer(description='ID del camión actualizado'),
    'health_status': fields.String(description='Nuevo estado de salud del camión'),
    'components_updated': fields.Integer(description='Número de componentes actualizados')
})
