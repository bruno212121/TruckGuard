from flask import request, jsonify, Blueprint
from .. import db
from ..models import TruckModel, MaintenanceModel, FleetAnalyticsModel, UserModel
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..utils.decorators import role_required
from datetime import datetime

trucks = Blueprint('trucks', __name__, url_prefix='/trucks')




#create truck
@trucks.route('/new', methods=['POST'])
@jwt_required()
@role_required(['owner'])
def create_truck():
    current_user = get_jwt_identity()
    if request.method == 'POST':
        data = request.get_json()
        if 'driver_id' not in data:
            return jsonify({'message': 'Driver id is required'}), 400
        driver_id = data['driver_id'] 
        driver = UserModel.query.filter_by(id=driver_id, rol='driver').first()
        if not driver:
            return jsonify({'message': 'Invalid driver id or the user does not have the driver role'}), 400
        try:
            new_truck = TruckModel(owner_id=current_user, 
                                plate=data['plate'], 
                                model=data['model'], 
                                brand=data['brand'], 
                                year=data['year'], 
                                color=data['color'], 
                                mileage=data['mileage'], 
                                health_status=data['health_status'], 
                                fleetanalytics_id=data['fleetanalytics_id'],
                                driver_id=driver_id)
            db.session.add(new_truck)
            db.session.commit()

            components = data.get('components', [
                {"name": "Filtros", "interval": 10000, "last_replacement": 0, "next_replacement": 10000}, 
                {"name": "aceite", "interval": 5000, "last_replacement": 0, "next_replacement": 5000}, 
                {"name": "injecciones", "interval": 8000, "last_replacement": 0, "next_replacement": 8000},
                {"name": "frenos", "interval": 9500, "last_replacement": 0, "next_replacement": 9500},
            ])

            for component in components: 
                maintenance = MaintenanceModel(  
                    description=f'{component["name"]} maintenance', 
                    status='Excelent', 
                    component=component['name'], 
                    cost=0, 
                    mileage_interval=component['interval'],
                    last_maintenance_mileage=0,
                    next_maintenance_mileage=component['interval'],
                    truck_id=new_truck.truck_id,
                    driver_id=driver_id,
                    maintenance_interval=component['interval']
                )
                db.session.add(maintenance)
            
            db.session.commit()

            FleetAnalyticsModel.update_fleet_analytics(current_user)

            return jsonify({'message': 'Truck created', 'truck': new_truck.truck_id}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Error creating truck', 'error': str(e)}), 500

#listar todos los camiones
@trucks.route('/all', methods=['GET'])
@jwt_required()
@role_required(['owner'])
def list_trucks():
    trucks = db.session.query(TruckModel).all()
    trucks_list = []
    for truck in trucks:
        driver = db.session.query(UserModel).get(truck.driver_id)
        truck_data = {
            'truck_id': truck.truck_id, 
            'plate': truck.plate, 
            'model': truck.model, 
            'brand': truck.brand, 
            'year': truck.year, 
            'mileage': truck.mileage, 
            'color': truck.color, 
            'status': truck.status, 
            'updated_at': truck.updated_at, 
            'driver': {
                'id': driver.id, 
                'name': driver.name, 
                'surname': driver.surname, 
                'email': driver.email, 
                'phone': driver.phone,
                'role': driver.rol
            } if driver else None
        }
        trucks_list.append(truck_data)
    return jsonify({'trucks': trucks_list}), 200

@trucks.route('/<int:id>', methods=['GET'])
@jwt_required()
@role_required(['owner'])
def view_truck(id):
    truck = db.session.query(TruckModel).get_or_404(id)
    if truck.owner_id != truck.owner_id and truck.driver_id != truck.owner_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    truck_data = {'truck_id': truck.truck_id, 'plate': truck.plate, 'model': truck.model, 'brand': truck.brand, 'year': truck.year,'mileage': truck.mileage, 'color': truck.color, 'status': truck.status, 'updated_at': truck.updated_at}
    return jsonify({'truck': truck_data}), 200


@trucks.route('/<int:id>/edit', methods=['PUT'])
@jwt_required()
@role_required(['owner'])
def edit_truck(id):
    truck = db.session.query(TruckModel).get_or_404(id)
    if truck.owner_id != truck.owner_id and truck.driver_id != truck.owner_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400
    
    truck.status = data.get('status', truck.status)
    truck.updated_at = datetime.now()
    truck.created_at = data.get('created_at', truck.created_at)
    db.session.commit()

    return jsonify({'message': 'Truck updated', 'truck': truck.truck_id}), 200


@trucks.route('/<int:id>/delete', methods=['DELETE'])
@jwt_required()
@role_required(['owner'])
def delete_truck(id):
    truck = db.session.query(TruckModel).get_or_404(id)
    if truck.owner_id != truck.owner_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    db.session.delete(truck)
    db.session.commit()
    return jsonify({'message': 'Truck deleted'}), 200



#asignar camion ya asignado a otro driver
@trucks.route('/<int:id>/assign', methods=['PUT'])
@jwt_required()
@role_required(['owner'])
def assign_truck(id):
    truck = db.session.query(TruckModel).get_or_404(id)
    if truck.owner_id != truck.owner_id:
        return jsonify({'message': 'Not anaothorized'}), 403
    
    data = request.get_json()
    if not data or 'driver_id' not in data:
        return jsonify({'message': 'No input data provided or driver id missing'}), 400
    
    truck.driver_id = data.get('driver_id')
    truck.updated_at = datetime.now()
    db.session.commit()

    return jsonify({'message': 'Truck assign', 'truck': truck.model, 'brand': truck.bran }), 200
