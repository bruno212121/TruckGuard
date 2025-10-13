from flask_restx import Resource
from flask import request, jsonify, Blueprint
from .. import db
from ..models import FleetAnalyticsModel, UserModel
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..utils.decorators import role_required


fleet = Blueprint('fleet', __name__, url_prefix='/fleet')  


@fleet.route('/analytics', methods=['GET'])
@jwt_required()
@role_required(['owner'])
def get_fleet_analytics():
    current_user = get_jwt_identity()
    
    try:
        fleet_analytics = FleetAnalyticsModel.query.filter_by(user_id=current_user).first()

        if fleet_analytics is None:
            return jsonify({'Message': 'No existing fleet analytics'}), 404


        return jsonify(fleet_analytics.to_json()), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching fleet analytics', 'error': str(e)}), 500


@fleet.route('/analytics/refresh', methods=['PUT'])
@jwt_required()
@role_required(['owner'])
def refresh_fleet_analytics():
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
            return jsonify({'message': 'Error: Fleet analytics not found after update'}), 500

        return jsonify({
            'message': 'Fleet analytics refreshed successfully',
            'analytics': fleet_analytics.to_json()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error refreshing fleet analytics', 'error': str(e)}), 500