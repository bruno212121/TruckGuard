from flask_restful import Resource
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