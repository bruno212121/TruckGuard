from flask_restful import Resource
from flask import request, jsonify
from .. import db
from ..models import FleetAnalyticsModel, OwnerModel
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..utils.decorators import owner_required


class Fleetanalytics(Resource):

    @jwt_required
    @owner_required
    def get(self, id):
        fleet = db.session.query(FleetAnalyticsModel).get_or_404(id)
        return fleet.to_json()
    
    @jwt_required
    @owner_required
    def put(self, id):
        fleet = db.session.query(FleetAnalyticsModel).get_or_404(id)
        data = request.get_json()
        user_id = get_jwt_identity()
        claims = get_jwt()
        if claims.get('rol') == 'owner':
            owner = OwnerModel.query.filter_by(user_id=user_id).first()
            if owner:
                for key, value in data.items():
                    setattr(fleet, key, value)
                db.session.commit()
                return fleet.to_json(), 201
            return {'message': 'you do not have permission to modify this fleet'}, 403
        return {'message': 'Owner role is required'}, 401
    
    @jwt_required
    @owner_required
    def patch(self, id):
        fleet = db.session.query(FleetAnalyticsModel).get_or_404(id)
        new_status = request.get_json().get('status')
        user_id = get_jwt_identity()
        claims = get_jwt()
        if claims.get('rol') == 'owner':
            owner = OwnerModel.query.filter_by(user_id=user_id).first()
            if owner:
                if new_status:
                    fleet.status = new_status
                    db.session.commit()
                    return fleet.to_json(), 200
                return {'message': 'No new status provided'}, 400
            return {'message': 'you do not have permission to modify this fleet'}, 403
        return {'message': 'Owner role is required'}, 401
    
    @jwt_required
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        claims = get_jwt()
        if claims.get('rol') == 'owner':
            owner = OwnerModel.query.filter_by(user_id=user_id).first()
            if owner:
                fleet = FleetAnalyticsModel(**data)
                db.session.add(fleet)
                db.session.commit()
                return fleet.to_json(), 201
            return {'message': 'you do not have permission to modify this fleet'}, 403
        return {'message': 'Owner role is required'}, 401
