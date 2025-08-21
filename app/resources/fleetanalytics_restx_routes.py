"""
Rutas Flask-RESTX para el recurso de fleetanalytics
"""
from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import FleetAnalyticsModel, UserModel, TruckModel, TripModel, MaintenanceModel
from ..utils.decorators import role_required
from datetime import datetime
from ..swagger_models.fleetanalytics_models import (
    fleet_ns, create_fleetanalytics_model, edit_fleetanalytics_model,
    fleetanalytics_list_model, fleetanalytics_detail_model, create_fleetanalytics_response_model,
    success_message_model, fleet_stats_model
)


@fleet_ns.route('/analytics')
class GetFleetAnalytics(Resource):
    @fleet_ns.response(200, 'Análisis de flota obtenido exitosamente', fleetanalytics_detail_model)
    @fleet_ns.response(404, 'Análisis de flota no encontrado')
    @fleet_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['owner'])
    def get(self):
        """Obtener análisis de flota del usuario actual"""
        current_user = get_jwt_identity()
        
        try:
            fleet_analytics = FleetAnalyticsModel.query.filter_by(user_id=current_user).first()

            if fleet_analytics is None:
                fleet_ns.abort(404, message='No existing fleet analytics')

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


@fleet_ns.route('/analytics/<int:owner_id>')
class GetFleetAnalyticsByOwner(Resource):
    @fleet_ns.response(200, 'Análisis de flota obtenido exitosamente', fleetanalytics_detail_model)
    @fleet_ns.response(404, 'Análisis de flota no encontrado')
    @fleet_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['owner'])
    def get(self, owner_id):
        """Obtener análisis de flota por ID de propietario"""
        try:
            fleet_analytics = FleetAnalyticsModel.query.filter_by(user_id=owner_id).first()

            if fleet_analytics is None:
                fleet_ns.abort(404, message='No existing fleet analytics for this owner')

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


@fleet_ns.route('/analytics/update')
class UpdateFleetAnalytics(Resource):
    @fleet_ns.response(200, 'Análisis de flota actualizado exitosamente', success_message_model)
    @fleet_ns.response(404, 'Análisis de flota no encontrado')
    @fleet_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['owner'])
    def post(self):
        """Actualizar análisis de flota manualmente"""
        current_user = get_jwt_identity()
        
        try:
            # Llamar al método estático para actualizar
            FleetAnalyticsModel.update_fleet_analytics(current_user)
            
            return {'message': 'Fleet analytics updated successfully', 'analytics': current_user}, 200
        except Exception as e:
            fleet_ns.abort(500, message='Error updating fleet analytics', error=str(e))


@fleet_ns.route('/stats')
class FleetStats(Resource):
    @fleet_ns.response(200, 'Estadísticas de flota obtenidas exitosamente', fleet_stats_model)
    @jwt_required()
    @role_required(['owner'])
    def get(self):
        """Obtener estadísticas generales de todas las flotas"""
        try:
            # Obtener estadísticas generales
            total_fleets = UserModel.query.filter_by(rol='owner').count()
            total_analytics = FleetAnalyticsModel.query.count()
            
            # Calcular salud promedio de flotas
            health_scores = db.session.query(db.func.avg(FleetAnalyticsModel.fleet_health_score)).scalar() or 0
            
            # Calcular costo operacional total
            total_cost = db.session.query(db.func.sum(FleetAnalyticsModel.total_cost)).scalar() or 0
            
            # Encontrar la flota más activa (con más viajes)
            most_active_fleet = db.session.query(
                FleetAnalyticsModel.user_id
            ).order_by(FleetAnalyticsModel.total_trips.desc()).first()
            
            most_active_id = most_active_fleet[0] if most_active_fleet else None
            
            return {
                'total_fleets': total_fleets,
                'total_analytics': total_analytics,
                'average_fleet_health': float(health_scores),
                'total_operational_cost': float(total_cost),
                'most_active_fleet': most_active_id
            }, 200
        except Exception as e:
            fleet_ns.abort(500, message='Error fetching fleet stats', error=str(e))


@fleet_ns.route('/analytics/all')
class ListAllFleetAnalytics(Resource):
    @fleet_ns.response(200, 'Lista de análisis de flota obtenida exitosamente', fleetanalytics_list_model)
    @jwt_required()
    @role_required(['owner'])
    def get(self):
        """Listar todos los análisis de flota (solo para propietarios)"""
        try:
            all_analytics = FleetAnalyticsModel.query.all()
            
            analytics_list = []
            for analytics in all_analytics:
                analytics_data = {
                    'analytics_id': analytics.id,
                    'owner_id': analytics.user_id,
                    'total_trucks': analytics.total_trucks,
                    'active_trucks': analytics.active_trucks,
                    'total_drivers': analytics.total_drivers,
                    'available_drivers': analytics.available_drivers,
                    'total_trips': analytics.total_trips,
                    'completed_trips': analytics.completed_trips,
                    'pending_trips': analytics.pending_trips,
                    'total_maintenance': analytics.total_maintenance,
                    'pending_maintenance': analytics.pending_maintenance,
                    'total_cost': analytics.total_cost,
                    'average_cost_per_trip': analytics.average_cost_per_trip,
                    'fleet_health_score': analytics.fleet_health_score,
                    'created_at': analytics.created_at,
                    'updated_at': analytics.updated_at
                }
                analytics_list.append(analytics_data)
            
            return {'fleetanalytics': analytics_list}, 200
        except Exception as e:
            fleet_ns.abort(500, message='Error fetching all fleet analytics', error=str(e))
