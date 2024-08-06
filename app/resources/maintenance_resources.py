from flask_restful import Resource
from flask import request, jsonify, Blueprint
from .. import db
from ..models import MaintenanceModel, TruckModel, FleetAnalyticsModel
from flask_jwt_extended import jwt_required
from ..utils.decorators import role_required
from datetime import datetime


maintenance = Blueprint('maintenance', __name__, url_prefix='/maintenance')


@maintenance.route('/new', methods=['POST'])
@jwt_required()
@role_required(['owner', 'driver'])
def create_maintenance():
    data = request.get_json()
    try:
        new_maintenance = MaintenanceModel(
            description=data.get('description', ''),
            component=data.get('component', ''),
            truck_id=data.get('truck_id', ''),
            driver_id=data.get('driver_id', None),  # Asegurar que se maneje el driver_id correctamente
            cost=data.get('cost', ''),
            status='Pending',
            mileage_interval=data.get('mileage_interval', 10000),
            last_maintenance_mileage=0,
            next_maintenance_mileage=data.get('next_maintenance_mileage', data.get('mileage_interval', 10000)),
            maintenance_interval=data.get('maintenance_interval', 10000)
        )
        
        new_maintenance.created_at = datetime.now()
        new_maintenance.updated_at = datetime.now()

        db.session.add(new_maintenance)
        db.session.commit()

        truck = TruckModel.query.get(data['truck_id'])
        if truck:
            FleetAnalyticsModel.update_fleet_analytics(truck.owner_id)

        return jsonify({'message': 'Maintenance created', 'component': new_maintenance.component}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating maintenance', 'error': str(e)}), 500


# #no va creo ya con el nuevo de truckid te muestra los componentes de cada camion para areglar
# @maintenance.route('/all', methods=['GET'])
# @jwt_required()
# @role_required(['owner'])
# def list_maintenances():
#     maintenances = db.session.query(MaintenanceModel).all()
#     maintenances_list = [maintenance.to_json() for maintenance in maintenances]
#     return jsonify({'maintenances': maintenances_list}), 200


# @maintenance.route('/<int:id>', methods=['GET'])
# @jwt_required()
# @role_required(['owner', 'driver'])
# def view_maintenance(id):
#     maintenance = db.session.query(MaintenanceModel).get_or_404(id)
    
#     maintenance_data = maintenance.to_json()
#     return jsonify({'maintenance': maintenance_data}), 200




@maintenance.route('/<int:id>/edit', methods=['PATCH'])
@jwt_required()
@role_required(['owner', 'driver'])
def edit_maintenance(id):
    maintenance = db.session.query(MaintenanceModel).get_or_404(id)

    
    data = request.get_json()
    
    if "description" in data:
        maintenance.description = data["description"]
    if "cost" in data:
        maintenance.cost = data["cost"]
    
    db.session.commit()

    return jsonify({'message': 'Maintenance updated', 'maintenance': maintenance.description, 'status Maintenance': maintenance.status, 'Cost': maintenance.cost}), 200
    
@maintenance.route('/<int:truck_id>/component/<int:component_id>', methods=['GET'])
@jwt_required()
@role_required(['owner'])
def add_component(truck_id, component_id):

    truck = TruckModel.query.get_or_404(truck_id)
    component = MaintenanceModel.query.get_or_404(component_id)


    if not component:
        return jsonify({'error': 'Component not found this truck'}), 404
    
    return jsonify({'component': component.to_json()}), 200
    

@maintenance.route('/<int:truck_id>/components', methods=['GET'])
@jwt_required()
@role_required(['owner'])
def list_components(truck_id):
    truck = TruckModel.query.get_or_404(truck_id)
    components = truck.maintenances
    components_list = [component.to_json() for component in components]
    return jsonify({'components': components_list}), 200


@maintenance.route('/<int:id>/approve', methods=['PATCH'])
@jwt_required()
@role_required(['owner'])
def approve_maintenance(id):
    maintenance = db.session.query(MaintenanceModel).get_or_404(id)


    data = request.get_json()
    approval_status = data.get('approval_status')
    if approval_status is None:
        return jsonify({'error': 'Approval status is required'}), 400
    try:
        if approval_status == 'Approved':
            maintenance.status = 'Completed'
            truck = maintenance.truck
            truck.update_component(maintenance.component, 'Excelent')
        
        elif approval_status == 'Rejected': 
            maintenance.status = 'Rejected'

        db.session.commit()

        if approval_status == 'Approved':
            FleetAnalyticsModel.update_fleet_analytics(truck.owner_id)

        return jsonify({'message': 'Maintenance status updated', 'status': maintenance.status}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating maintenance status', 'error': str(e)}), 500