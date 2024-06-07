from flask_restful import Resource
from flask import request, jsonify, Blueprint
from .. import db
from ..models import FleetAnalyticsModel, TruckModel, OwnerModel, TripModel, MaintenanceModel, DriverModel
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..utils.decorators import role_required


fleet = Blueprint('fleet', __name__, url_prefix='/fleet')  


@fleet.route('/analytics', methods=['GET'])
@jwt_required()
def get_fleet_analytics():
    current_user = get_jwt_identity()
    owner = OwnerModel.query.filter_by(id=current_user).first()


    fleet_analytics = FleetAnalyticsModel.query.filter_by(owner_id=current_user).first()

    if fleet_analytics is None:
        return jsonify({'Message': 'No existing fleet analytics'}), 404


    return jsonify(fleet_analytics.to_json()), 200