"""
Modelos Swagger para el recurso de fleetanalytics
"""
from flask_restx import fields
from app.config.api_config import api

# Namespace para fleetanalytics
fleet_ns = api.namespace('Fleetanalytics', description='Operaciones de análisis de flota')

# Modelos de entrada
create_fleetanalytics_model = api.model('CreateFleetAnalytics', {
    'owner_id': fields.Integer(required=True, description='ID del propietario', example=1),
    'total_trucks': fields.Integer(required=False, description='Total de camiones', example=5),
    'active_trucks': fields.Integer(required=False, description='Camiones activos', example=4),
    'total_drivers': fields.Integer(required=False, description='Total de conductores', example=6),
    'available_drivers': fields.Integer(required=False, description='Conductores disponibles', example=2),
    'total_trips': fields.Integer(required=False, description='Total de viajes', example=25),
    'completed_trips': fields.Integer(required=False, description='Viajes completados', example=20),
    'pending_trips': fields.Integer(required=False, description='Viajes pendientes', example=3),
    'total_maintenance': fields.Integer(required=False, description='Total de mantenimientos', example=15),
    'pending_maintenance': fields.Integer(required=False, description='Mantenimientos pendientes', example=5),
    'total_cost': fields.Float(required=False, description='Costo total', example=15000.50),
    'average_cost_per_trip': fields.Float(required=False, description='Costo promedio por viaje', example=600.20),
    'fleet_health_score': fields.Float(required=False, description='Puntuación de salud de la flota', example=85.5),
    'created_at': fields.DateTime(required=False, description='Fecha de creación'),
    'updated_at': fields.DateTime(required=False, description='Fecha de actualización')
})

edit_fleetanalytics_model = api.model('EditFleetAnalytics', {
    'total_trucks': fields.Integer(required=False, description='Total de camiones'),
    'active_trucks': fields.Integer(required=False, description='Camiones activos'),
    'total_drivers': fields.Integer(required=False, description='Total de conductores'),
    'available_drivers': fields.Integer(required=False, description='Conductores disponibles'),
    'total_trips': fields.Integer(required=False, description='Total de viajes'),
    'completed_trips': fields.Integer(required=False, description='Viajes completados'),
    'pending_trips': fields.Integer(required=False, description='Viajes pendientes'),
    'total_maintenance': fields.Integer(required=False, description='Total de mantenimientos'),
    'pending_maintenance': fields.Integer(required=False, description='Mantenimientos pendientes'),
    'total_cost': fields.Float(required=False, description='Costo total'),
    'average_cost_per_trip': fields.Float(required=False, description='Costo promedio por viaje'),
    'fleet_health_score': fields.Float(required=False, description='Puntuación de salud de la flota')
})

# Modelos de respuesta
fleetanalytics_response_model = api.model('FleetAnalyticsResponse', {
    'analytics_id': fields.Integer(description='ID del análisis'),
    'owner_id': fields.Integer(description='ID del propietario'),
    'total_trucks': fields.Integer(description='Total de camiones'),
    'active_trucks': fields.Integer(description='Camiones activos'),
    'total_drivers': fields.Integer(description='Total de conductores'),
    'available_drivers': fields.Integer(description='Conductores disponibles'),
    'total_trips': fields.Integer(description='Total de viajes'),
    'completed_trips': fields.Integer(description='Viajes completados'),
    'pending_trips': fields.Integer(description='Viajes pendientes'),
    'total_maintenance': fields.Integer(description='Total de mantenimientos'),
    'pending_maintenance': fields.Integer(description='Mantenimientos pendientes'),
    'total_cost': fields.Float(description='Costo total'),
    'average_cost_per_trip': fields.Float(description='Costo promedio por viaje'),
    'fleet_health_score': fields.Float(description='Puntuación de salud de la flota'),
    'created_at': fields.DateTime(description='Fecha de creación'),
    'updated_at': fields.DateTime(description='Fecha de actualización')
})

fleetanalytics_detail_model = api.model('FleetAnalyticsDetail', {
    'analytics_id': fields.Integer(description='ID del análisis'),
    'owner_id': fields.Integer(description='ID del propietario'),
    'total_trucks': fields.Integer(description='Total de camiones'),
    'active_trucks': fields.Integer(description='Camiones activos'),
    'total_drivers': fields.Integer(description='Total de conductores'),
    'available_drivers': fields.Integer(description='Conductores disponibles'),
    'total_trips': fields.Integer(description='Total de viajes'),
    'completed_trips': fields.Integer(description='Viajes completados'),
    'pending_trips': fields.Integer(description='Viajes pendientes'),
    'total_maintenance': fields.Integer(description='Total de mantenimientos'),
    'pending_maintenance': fields.Integer(description='Mantenimientos pendientes'),
    'total_cost': fields.Float(description='Costo total'),
    'average_cost_per_trip': fields.Float(description='Costo promedio por viaje'),
    'fleet_health_score': fields.Float(description='Puntuación de salud de la flota'),
    'created_at': fields.String(description='Fecha de creación'),
    'updated_at': fields.String(description='Fecha de actualización')
})

fleetanalytics_list_model = api.model('FleetAnalyticsList', {
    'fleetanalytics': fields.List(fields.Nested(fleetanalytics_response_model), description='Lista de análisis de flota')
})

create_fleetanalytics_response_model = api.model('CreateFleetAnalyticsResponse', {
    'message': fields.String(description='Mensaje de confirmación'),
    'analytics': fields.Integer(description='ID del análisis creado')
})

success_message_model = api.model('SuccessMessage', {
    'message': fields.String(description='Mensaje de confirmación'),
    'analytics': fields.Integer(description='ID del análisis')
})

# Modelos para estadísticas y reportes
fleet_stats_model = api.model('FleetStats', {
    'total_fleets': fields.Integer(description='Total de flotas'),
    'total_analytics': fields.Integer(description='Total de análisis'),
    'average_fleet_health': fields.Float(description='Salud promedio de flotas'),
    'total_operational_cost': fields.Float(description='Costo operacional total'),
    'most_active_fleet': fields.Integer(description='ID de la flota más activa')
})

# Modelo para camiones asignados a drivers
assigned_truck_model = api.model('AssignedTruck', {
    'truck_id': fields.Integer(description='ID del camión'),
    'plate': fields.String(description='Matrícula del camión'),
    'model': fields.String(description='Modelo del camión'),
    'brand': fields.String(description='Marca del camión'),
    'year': fields.Integer(description='Año del camión'),
    'color': fields.String(description='Color del camión'),
    'mileage': fields.Integer(description='Kilometraje actual'),
    'health_status': fields.String(description='Estado de salud del camión'),
    'pending_maintenance_count': fields.Integer(description='Cantidad de mantenimientos pendientes'),
    'critical_maintenance_count': fields.Integer(description='Cantidad de mantenimientos críticos'),
    'assigned_date': fields.String(description='Fecha de asignación')
})

driver_assigned_trucks_response_model = api.model('DriverAssignedTrucksResponse', {
    'message': fields.String(description='Mensaje de respuesta'),
    'assigned_trucks': fields.List(fields.Nested(assigned_truck_model), description='Lista de camiones asignados'),
    'total_assigned': fields.Integer(description='Total de camiones asignados'),
    'driver_id': fields.Integer(description='ID del driver')
})

# Modelos para alertas de mantenimiento
maintenance_alert_model = api.model('MaintenanceAlert', {
    'truck_id': fields.Integer(description='ID del camión'),
    'plate': fields.String(description='Matrícula del camión'),
    'component': fields.String(description='Componente que necesita mantenimiento'),
    'km_remaining': fields.Integer(description='Kilómetros restantes hasta el mantenimiento'),
    'next_maintenance_mileage': fields.Integer(description='Próximo kilometraje de mantenimiento'),
    'current_mileage': fields.Integer(description='Kilometraje actual'),
    'priority': fields.String(description='Prioridad de la alerta', enum=['URGENT', 'UPCOMING', 'CRITICAL']),
    'estimated_days': fields.Integer(description='Días estimados hasta el mantenimiento'),
    'status': fields.String(description='Estado del componente (solo para críticos)')
})

alerts_summary_model = api.model('AlertsSummary', {
    'total_alerts': fields.Integer(description='Total de alertas'),
    'urgent_count': fields.Integer(description='Cantidad de alertas urgentes'),
    'upcoming_count': fields.Integer(description='Cantidad de alertas próximas'),
    'critical_count': fields.Integer(description='Cantidad de componentes críticos')
})

maintenance_alerts_response_model = api.model('MaintenanceAlertsResponse', {
    'urgent_maintenance': fields.List(fields.Nested(maintenance_alert_model), description='Mantenimientos urgentes'),
    'upcoming_maintenance': fields.List(fields.Nested(maintenance_alert_model), description='Mantenimientos próximos'),
    'critical_components': fields.List(fields.Nested(maintenance_alert_model), description='Componentes críticos'),
    'summary': fields.Nested(alerts_summary_model, description='Resumen de alertas')
})

# Modelos para filtros
fleet_filter_model = api.model('FleetFilter', {
    'owner_id': fields.Integer(required=False, description='Filtrar por propietario', example=1),
    'min_health_score': fields.Float(required=False, description='Puntuación mínima de salud', example=70.0),
    'max_health_score': fields.Float(required=False, description='Puntuación máxima de salud', example=100.0),
    'date_from': fields.DateTime(required=False, description='Fecha desde', example='2024-01-01T00:00:00'),
    'date_to': fields.DateTime(required=False, description='Fecha hasta', example='2024-12-31T23:59:59')
})
