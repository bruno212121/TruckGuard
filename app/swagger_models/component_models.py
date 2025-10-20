"""
Modelos Swagger para el recurso de componentes
"""
from flask_restx import fields
from .. import api

# Namespace para componentes
component_ns = api.namespace('components', description='Operaciones relacionadas con componentes de camiones')

# Modelo para crear un componente
create_component_model = component_ns.model('CreateComponent', {
    'name': fields.String(required=True, description='Nombre del componente', example='Filtros'),
    'description': fields.String(required=False, description='Descripción del componente', example='Filtros de aire'),
    'interval': fields.Integer(required=True, description='Intervalo de mantenimiento en km', example=10000),
    'cost': fields.Float(required=False, description='Costo estimado del mantenimiento', example=150.0),
    'driver_id': fields.Integer(required=False, description='ID del conductor asignado')
})

# Modelo para el estado de un componente
component_status_item_model = component_ns.model('ComponentStatusItem', {
    'component_name': fields.String(description='Nombre del componente', example='Filtros'),
    'current_status': fields.String(description='Estado actual del componente', example='Excellent'),
    'health_percentage': fields.Integer(description='Porcentaje de salud del componente (100-80: Excellent, 80-60: Very Good, 60-40: Good, 40-20: Fair, 20-0: Maintenance Required)', example=90),
    'last_maintenance_mileage': fields.Integer(description='Kilometraje del último mantenimiento', example=150000),
    'next_maintenance_mileage': fields.Integer(description='Próximo kilometraje de mantenimiento', example=160000),
    'km_remaining': fields.Integer(description='Kilómetros restantes hasta el próximo mantenimiento', example=8000),
    'maintenance_interval': fields.Integer(description='Intervalo de mantenimiento', example=10000)
})

# Modelo para el estado completo de componentes del camión
component_status_model = component_ns.model('ComponentStatus', {
    'truck_id': fields.Integer(description='ID del camión'),
    'plate': fields.String(description='Matrícula del camión'),
    'model': fields.String(description='Modelo del camión'),
    'brand': fields.String(description='Marca del camión'),
    'current_mileage': fields.Integer(description='Kilometraje actual'),
    'overall_health_status': fields.String(description='Estado general de salud del camión'),
    'components': fields.List(fields.Nested(component_status_item_model), description='Lista de componentes'),
    'total_components': fields.Integer(description='Total de componentes'),
    'components_requiring_maintenance': fields.Integer(description='Componentes que requieren mantenimiento'),
    'last_updated': fields.String(description='Última actualización')
})

# Modelo para un componente individual
component_detail_model = component_ns.model('ComponentDetail', {
    'component_id': fields.Integer(description='ID del componente'),
    'component_name': fields.String(description='Nombre del componente'),
    'status': fields.String(description='Estado del componente'),
    'description': fields.String(description='Descripción del componente'),
    'cost': fields.Float(description='Costo del mantenimiento'),
    'mileage_interval': fields.Integer(description='Intervalo de kilometraje'),
    'last_maintenance_mileage': fields.Integer(description='Último mantenimiento'),
    'next_maintenance_mileage': fields.Integer(description='Próximo mantenimiento'),
    'maintenance_interval': fields.Integer(description='Intervalo de mantenimiento'),
    'created_at': fields.String(description='Fecha de creación'),
    'updated_at': fields.String(description='Fecha de actualización')
})

# Modelo para la lista de componentes
component_list_model = component_ns.model('ComponentList', {
    'truck_id': fields.Integer(description='ID del camión'),
    'components': fields.List(fields.Nested(component_detail_model), description='Lista de componentes'),
    'total_components': fields.Integer(description='Total de componentes')
})

# Modelo para respuesta de creación de componente
create_component_response_model = component_ns.model('CreateComponentResponse', {
    'message': fields.String(description='Mensaje de respuesta'),
    'component': fields.Nested(component_detail_model, description='Componente creado')
})

# Modelo para request bulk de componentes
bulk_components_request_model = component_ns.model('BulkComponentsRequest', {
    'truck_ids': fields.List(fields.Integer, required=True, description='Lista de IDs de camiones', example=[1, 2, 3, 4, 5])
})

# Modelo para respuesta bulk de componentes
truck_components_bulk_model = component_ns.model('TruckComponentsBulk', {
    'truck_id': fields.Integer(description='ID del camión'),
    'plate': fields.String(description='Matrícula del camión'),
    'model': fields.String(description='Modelo del camión'),
    'brand': fields.String(description='Marca del camión'),
    'current_mileage': fields.Integer(description='Kilometraje actual'),
    'overall_health_status': fields.String(description='Estado general de salud'),
    'components': fields.List(fields.Nested(component_status_item_model), description='Componentes del camión'),
    'total_components': fields.Integer(description='Total de componentes'),
    'components_requiring_maintenance': fields.Integer(description='Componentes que requieren mantenimiento'),
    'last_updated': fields.String(description='Última actualización'),
    'error': fields.String(description='Error si no se pudo obtener el estado del camión')
})

bulk_components_response_model = component_ns.model('BulkComponentsResponse', {
    'successful_trucks': fields.List(fields.Nested(truck_components_bulk_model), description='Camiones procesados exitosamente'),
    'failed_trucks': fields.List(fields.Nested(truck_components_bulk_model), description='Camiones que fallaron'),
    'total_requested': fields.Integer(description='Total de camiones solicitados'),
    'total_successful': fields.Integer(description='Total de camiones procesados exitosamente'),
    'total_failed': fields.Integer(description='Total de camiones que fallaron'),
    'processing_time_ms': fields.Float(description='Tiempo de procesamiento en milisegundos')
})