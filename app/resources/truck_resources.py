from flask import request, jsonify, Blueprint, render_template, redirect, url_for
from .. import db
from ..models import TruckModel, OwnerModel
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..utils.decorators import role_required
from datetime import datetime

trucks = Blueprint('trucks', __name__, url_prefix='/trucks')

#Terminar con el decorado de owner
#Terminar con asignar un unico driver a truck


#create truck
@trucks.route('/new', methods=['POST'])
@jwt_required()
@role_required(['owner'])
def create_truck():
    current_user = get_jwt_identity()
    if request.method == 'POST':
        data = request.get_json()
        new_truck = TruckModel(owner_id=current_user, plate=data['plate'], model=data['model'], brand=data['brand'], year=data['year'], color=data['color'])
        db.session.add(new_truck)
        db.session.commit()
        return jsonify({'message': 'Truck created', 'truck': new_truck.truck_id}), 201

#listar todos los camiones
@trucks.route('/all', methods=['GET'])
@jwt_required()
@role_required(['owner'])
def list_trucks():
    trucks = db.session.query(TruckModel).all()
    trucks_list = [{'truck_id': truck.truck_id, 'model': truck.model, 'status': truck.status, 'owner_id': truck.owner_id,'brand': truck.brand} for truck in trucks]
    return jsonify({'trucks': trucks_list}), 200


@trucks.route('/<int:id>', methods=['GET'])
@jwt_required()
@role_required(['owner'])
def view_truck(id):
    truck = db.session.query(TruckModel).get_or_404(id)
    if truck.owner_id != truck.owner_id and truck.driver_id != truck.owner_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    truck_data = {'truck_id': truck.truck_id, 'plate': truck.plate, 'model': truck.model, 'brand': truck.brand, 'year': truck.year, 'color': truck.color, 'status': truck.status, 'updated_at': truck.updated_at}
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


#ver si lo puedo poner en la ruta de owner 
#asignar camion a driver
@trucks.route('/<int:id>/assign', methods=['PUT'])
@jwt_required()
@role_required(['owner'])
def assign_truck(id):
    truck = db.session.query(TruckModel).get_or_404(id)
    if truck.owner_id != truck.owner_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400
    
    truck.driver_id = data.get('driver_id', truck.driver_id)
    truck.updated_at = datetime.now()
    db.session.commit()
    return jsonify({'message': 'Truck assigned', 'truck': truck.truck_id}), 200
