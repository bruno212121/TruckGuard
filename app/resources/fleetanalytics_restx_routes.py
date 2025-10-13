"""
Rutas Flask-RESTX para el recurso de fleetanalytics
"""
from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import FleetAnalyticsModel, TruckModel, MaintenanceModel, TripModel
from ..utils.decorators import role_required
from datetime import datetime
from ..swagger_models.fleetanalytics_models import (
    fleet_ns, fleetanalytics_detail_model, driver_assigned_trucks_response_model,
    maintenance_alerts_response_model, refresh_fleetanalytics_response_model
)


@fleet_ns.route('/analytics')
class GetFleetAnalytics(Resource):
    @fleet_ns.response(200, 'Análisis de flota obtenido exitosamente', fleetanalytics_detail_model)
    @fleet_ns.response(404, 'Análisis de flota no encontrado')
    @fleet_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['owner'])
    def get(self):
        """
        Obtener análisis de flota del usuario actual.
        
        Esta ruta devuelve las estadísticas completas de la flota del owner logueado,
        incluyendo información sobre camiones, conductores, viajes y mantenimientos.
        """
        current_user = get_jwt_identity()
        
        try:
            fleet_analytics = FleetAnalyticsModel.query.filter_by(user_id=current_user).first()

            if fleet_analytics is None:
                # Si no existe analytics, crear uno automáticamente
                FleetAnalyticsModel.update_fleet_analytics(current_user)
                fleet_analytics = FleetAnalyticsModel.query.filter_by(user_id=current_user).first()

            analytics_data = {
                'analytics_id': fleet_analytics.id,
                'owner_id': fleet_analytics.user_id,
                'total_trucks': fleet_analytics.total_trucks,
                'active_trucks': fleet_analytics.active_trucks,
                'total_drivers': fleet_analytics.total_drivers,
                'available_drivers': fleet_analytics.available_drivers,
                'total_trips': fleet_analytics.total_trips,
                'completed_trips': fleet_analytics.completed_trips,
                'pending_trips': fleet_analytics.pending_trips,
                'total_maintenance': fleet_analytics.total_maintenance,
                'pending_maintenance': fleet_analytics.pending_maintenance,
                'total_cost': fleet_analytics.total_cost,
                'average_cost_per_trip': fleet_analytics.average_cost_per_trip,
                'fleet_health_score': fleet_analytics.fleet_health_score,
                'created_at': fleet_analytics.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': fleet_analytics.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }

            return analytics_data, 200
        except Exception as e:
            fleet_ns.abort(500, message='Error fetching fleet analytics', error=str(e))


@fleet_ns.route('/analytics/refresh')
class RefreshFleetAnalytics(Resource):
    @fleet_ns.response(200, 'Métricas de flota actualizadas exitosamente', refresh_fleetanalytics_response_model)
    @fleet_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['owner'])
    def put(self):
        """
        Actualizar manualmente las métricas de flota.
        
        Este endpoint fuerza el recálculo de todas las métricas de FleetAnalytics
        para el owner actual. Útil cuando hay discrepancias en los datos o
        cuando se necesita sincronizar las métricas con el estado actual.
        """
        current_user = get_jwt_identity()
        
        try:
            # Forzar actualización de métricas
            FleetAnalyticsModel.update_fleet_analytics(current_user)
            
            # Obtener las métricas actualizadas
            fleet_analytics = FleetAnalyticsModel.query.filter_by(user_id=current_user).first()
            
            if fleet_analytics is None:
                fleet_ns.abort(500, message='Error: Fleet analytics not found after update')

            analytics_data = {
                'analytics_id': fleet_analytics.id,
                'owner_id': fleet_analytics.user_id,
                'total_trucks': fleet_analytics.total_trucks,
                'active_trucks': fleet_analytics.active_trucks,
                'total_drivers': fleet_analytics.total_drivers,
                'available_drivers': fleet_analytics.available_drivers,
                'total_trips': fleet_analytics.total_trips,
                'completed_trips': fleet_analytics.completed_trips,
                'pending_trips': fleet_analytics.pending_trips,
                'total_maintenance': fleet_analytics.total_maintenance,
                'pending_maintenance': fleet_analytics.pending_maintenance,
                'total_cost': fleet_analytics.total_cost,
                'average_cost_per_trip': fleet_analytics.average_cost_per_trip,
                'fleet_health_score': fleet_analytics.fleet_health_score,
                'created_at': fleet_analytics.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': fleet_analytics.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }

            return {
                'message': 'Fleet analytics refreshed successfully',
                'analytics': analytics_data
            }, 200
            
        except Exception as e:
            fleet_ns.abort(500, message='Error refreshing fleet analytics', error=str(e))


@fleet_ns.route('/driver/assigned-trucks')
class GetDriverAssignedTrucks(Resource):
    @fleet_ns.response(200, 'Camiones asignados obtenidos exitosamente', driver_assigned_trucks_response_model)
    @fleet_ns.response(404, 'Driver no encontrado o sin camiones asignados')
    @fleet_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['driver'])
    def get(self):
        """
        Obtener información de los camiones asignados al driver actual.
        
        Esta ruta devuelve solo los camiones que están asignados al driver logueado,
        incluyendo información básica del camión y su estado de mantenimiento.
        """
        current_user = get_jwt_identity()
        
        try:
            # Buscar camiones asignados al driver
            assigned_trucks = TruckModel.query.filter_by(driver_id=current_user).all()
            
            if not assigned_trucks:
                return {
                    'message': 'No tienes camiones asignados actualmente',
                    'assigned_trucks': [],
                    'total_assigned': 0
                }, 200
            
            trucks_data = []
            for truck in assigned_trucks:
                # Obtener mantenimientos pendientes del camión
                pending_maintenance = MaintenanceModel.query.filter_by(
                    truck_id=truck.truck_id,
                    status='Pending'
                ).count()
                
                # Obtener mantenimientos críticos
                critical_maintenance = MaintenanceModel.query.filter_by(
                    truck_id=truck.truck_id,
                    status='Critical'
                ).count()
                
                truck_info = {
                    'truck_id': truck.truck_id,
                    'plate': truck.plate,
                    'model': truck.model,
                    'brand': truck.brand,
                    'year': truck.year,
                    'color': truck.color,
                    'mileage': truck.mileage,
                    'health_status': truck.health_status,
                    'pending_maintenance_count': pending_maintenance,
                    'critical_maintenance_count': critical_maintenance,
                    'assigned_date': truck.created_at.strftime('%Y-%m-%d %H:%M:%S') if truck.created_at else None
                }
                trucks_data.append(truck_info)
            
            return {
                'message': 'Camiones asignados obtenidos exitosamente',
                'assigned_trucks': trucks_data,
                'total_assigned': len(trucks_data),
                'driver_id': current_user
            }, 200
            
        except Exception as e:
            fleet_ns.abort(500, message='Error fetching assigned trucks', error=str(e))


@fleet_ns.route('/maintenance-alerts')
class GetMaintenanceAlerts(Resource):
    @fleet_ns.response(200, 'Alertas de mantenimiento obtenidas exitosamente', maintenance_alerts_response_model)
    @fleet_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['owner'])
    def get(self):
        """
        Obtener alertas de mantenimiento para la flota del owner.
        
        Esta ruta devuelve alertas críticas sobre:
        - Mantenimientos urgentes (menos de 1000 km restantes)
        - Mantenimientos próximos (menos de 3000 km restantes)
        - Componentes en estado crítico
        - Camiones con múltiples alertas
        """
        current_user = get_jwt_identity()
        
        try:
            # Obtener todos los camiones del owner
            trucks = TruckModel.query.filter_by(owner_id=current_user).all()
            
            alerts = {
                'urgent_maintenance': [],
                'upcoming_maintenance': [],
                'critical_components': [],
                'summary': {
                    'total_alerts': 0,
                    'urgent_count': 0,
                    'upcoming_count': 0,
                    'critical_count': 0
                }
            }
            
            for truck in trucks:
                truck_maintenance = MaintenanceModel.query.filter_by(truck_id=truck.truck_id).all()
                
                for maintenance in truck_maintenance:
                    # Calcular km restantes hasta el próximo mantenimiento
                    km_remaining = maintenance.next_maintenance_mileage - truck.mileage
                    
                    # Alertas urgentes (menos de 1000 km)
                    if km_remaining <= 1000 and km_remaining > 0:
                        alerts['urgent_maintenance'].append({
                            'truck_id': truck.truck_id,
                            'plate': truck.plate,
                            'component': maintenance.component,
                            'km_remaining': km_remaining,
                            'next_maintenance_mileage': maintenance.next_maintenance_mileage,
                            'current_mileage': truck.mileage,
                            'priority': 'URGENT',
                            'estimated_days': max(1, km_remaining // 100)  # Estimación: 100 km/día
                        })
                        alerts['summary']['urgent_count'] += 1
                    
                    # Alertas próximas (menos de 3000 km)
                    elif km_remaining <= 3000 and km_remaining > 1000:
                        alerts['upcoming_maintenance'].append({
                            'truck_id': truck.truck_id,
                            'plate': truck.plate,
                            'component': maintenance.component,
                            'km_remaining': km_remaining,
                            'next_maintenance_mileage': maintenance.next_maintenance_mileage,
                            'current_mileage': truck.mileage,
                            'priority': 'UPCOMING',
                            'estimated_days': max(1, km_remaining // 100)
                        })
                        alerts['summary']['upcoming_count'] += 1
                
                # Componentes en estado crítico
                critical_maintenance = MaintenanceModel.query.filter_by(
                    truck_id=truck.truck_id,
                    status='Critical'
                ).all()
                
                for critical in critical_maintenance:
                    alerts['critical_components'].append({
                        'truck_id': truck.truck_id,
                        'plate': truck.plate,
                        'component': critical.component,
                        'status': critical.status,
                        'last_maintenance_mileage': critical.last_maintenance_mileage,
                        'current_mileage': truck.mileage,
                        'priority': 'CRITICAL'
                    })
                    alerts['summary']['critical_count'] += 1
            
            # Calcular total de alertas
            alerts['summary']['total_alerts'] = (
                alerts['summary']['urgent_count'] + 
                alerts['summary']['upcoming_count'] + 
                alerts['summary']['critical_count']
            )
            
            # Ordenar alertas por prioridad
            alerts['urgent_maintenance'].sort(key=lambda x: x['km_remaining'])
            alerts['upcoming_maintenance'].sort(key=lambda x: x['km_remaining'])
            alerts['critical_components'].sort(key=lambda x: x['truck_id'])
            
            return alerts, 200
            
        except Exception as e:
            fleet_ns.abort(500, message='Error fetching maintenance alerts', error=str(e))







