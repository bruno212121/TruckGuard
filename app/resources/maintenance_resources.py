from flask_restful import Resource
from flask import request 
from .. import db
from ..models import MaintenanceModel
from flask_jwt_extended import jwt_required
from ..utils.decorators import owner_required , driver_required
from datetime import datetime

class Maintenance(Resource):

    @jwt_required
    def get(self, id):
        maintenance = db.session.query(MaintenanceModel).get_or_404(id)
        return maintenance.to_json()

    @jwt_required
    @driver_required
    @owner_required
    def put(self, id):
        data = request.get_json()
        maintenance = db.session.query(MaintenanceModel).get_or_404(id)
        if "status" in data:
            maintenance.status = data["status"]
        maintenance.updated_at = datetime.now()
        db.session.commit()
        return maintenance.to_json(), 200
    

    @jwt_required
    @driver_required
    @owner_required
    def patch(self, id):
        maintenance = db.session.query(MaintenanceModel).get_or_404(id)
        data = request.get_json()
        if "status" in data:
            maintenance.status = data["status"]
        if "description" in data:
            maintenance.description = data["description"]
        db.session.commit()
        return maintenance.to_json(), 200

    
    @jwt_required
    @driver_required
    @owner_required
    def post(self):
        data = request.get_json()
        if not all(key in data for key in ['description', 'status', 'truck_id', 'driver_id']):
            return {'message': 'Missing required fields'}, 400
        
        maintenance = MaintenanceModel(
            description=data['description'],
            status=data['status'],
            truck_id=data['truck_id'],
            driver_id=data['driver_id']
        )

        maintenance.created_at = datetime.now()

        db.session.add(maintenance)
        db.session.commit()
        return maintenance.to_json(), 201
