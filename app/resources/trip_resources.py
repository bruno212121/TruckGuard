from flask_restx import Resource
from flask import request, jsonify, Blueprint
from .. import db
from ..models import TripModel, TruckModel, FleetAnalyticsModel, UserModel
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..utils.decorators import role_required
from app.google.locations import GoogleGetLocation
from datetime import datetime
import asyncio

trips = Blueprint('trips', __name__, url_prefix='/trips')



#create trip
@trips.route('/new', methods=['POST'])
@jwt_required()
@role_required(['owner'])
def create_trip():
    trip_json = request.get_json()
    origin = trip_json.get('origin')
    destination = trip_json.get('destination')
    truck_id = trip_json.get('truck_id')


    truck = TruckModel.query.get(truck_id)
    driver = UserModel.query.get(trip_json.get('driver_id'))
    if truck is None:
        return jsonify({'error': 'Truck not found'}), 404
    if driver is None:
        return jsonify({'error': 'Driver not found'}), 404
    
    fair_components = []
    
    for maintenance in truck.maintenances: 
        if maintenance.status == 'Maintenance Required':
            return jsonify({'error': f'The component {maintenance.component} requires maintenance'}), 400
        elif maintenance.status == 'Fair':
            fair_components.append(maintenance.component)
        
    google_location = GoogleGetLocation()
    distance_info = asyncio.run(google_location.get_distance(origin, destination))

    new_trip = TripModel(
            origin=origin,
            destination=destination,
            status=trip_json.get('status', 'Pending'),
            driver_id=trip_json.get('driver_id'),
            truck_id=trip_json.get('truck_id'),
            date=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
    )

    db.session.add(new_trip)
    db.session.commit()

    response = new_trip.to_json()
    response.update(distance_info)
    response['truck'] = {
        'brand': truck.brand,
        'model': truck.model,
        'year': truck.year,
        'truck_id': truck.truck_id
    }

    response['driver'] = {
        'name': driver.name,
        'email': driver.email,
        'phone': driver.phone
    }

    if fair_components:
        response['Warning'] = f'The components {", ".join(fair_components)} are in fair condition'

    return response, 201

#listar todos los viajes
@trips.route('/all', methods=['GET'])
@jwt_required()
@role_required(['owner'])
def list_trips():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    origin = request.args.get('origin')
    destination = request.args.get('destination')
    status = request.args.get('status')
    driver_id = request.args.get('driver_id', type=int)

    trips_query = TripModel.query
    if origin:
        trips_query = trips_query.filter(TripModel.origin.like(f'%{origin}'))
    if destination:
        trips_query = trips_query.filter(TripModel.origin.like(f'%{destination}'))
    if status:
        trips_query = trips_query.filter(TripModel.origin.like(f'%{status}'))
    if driver_id:
        trips_query = trips_query.filter(TripModel.driver_id == driver_id)
    
    trips = trips_query.slice((page - 1) * per_page, page * per_page).all()
    total_trips = trips_query.count()

    return jsonify({
        'trips': [trip.to_json() for trip in trips],
        'total': total_trips,
        'pages': (total_trips -1) // per_page + 1,
        'page': page
    }), 200


@trips.route('/<int:id>', methods=['GET']) 
@jwt_required()
@role_required(['owner'])
def view_trip(id):
    trip = db.session.query(TripModel).get_or_404(id)
    driver = db.session.query(UserModel).get(trip.driver_id)
    truck = db.session.query(TruckModel).get(trip.truck_id)

    trip_data = {
        'id': trip.id,
        'origin': trip.origin,
        'destination': trip.destination,
        'status': trip.status,
        'updated_at': trip.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        'driver': driver.name if driver else 'No driver assigned',
        'truck_details': f'Brand: {truck.brand} Model: {truck.model} {truck.year} ID:{truck.truck_id}' if truck else 'No truck assigned',
    }

    if trip.status == 'Pending':
        google_location = GoogleGetLocation()
        distance_info = asyncio.run(google_location.get_distance(trip.origin, trip.destination))
        trip_data.update(distance_info)

    return jsonify({'trip': trip_data}), 200



@trips.route('/<int:id>/update', methods=['PATCH'])
@jwt_required()
@role_required(['owner', 'driver'])  #ambos roles pueden actualizar
def update_trip(id):
    trip = db.session.query(TripModel).get_or_404(id)
    trip_json = request.get_json()

    new_status = trip_json.get('status') 


    if new_status not in ['Pending', 'In Course', 'Completed']:
        return jsonify({'message': 'Invalid status value'}), 400

    trip.status = new_status  # Actualizando el estado.

    try:
        db.session.commit() 
        return jsonify({'message': 'Trip updated', 'trip': trip.to_json()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating the trip', 'error': str(e)}), 500
    

    

@trips.route('/<int:id>/complete', methods=['PATCH'])
@jwt_required()
@role_required(['driver', 'owner'])
def complete_trip(id):
    trip = db.session.query(TripModel).get_or_404(id)
    
    if trip.driver_id != trip.driver_id and trip.owner_id != trip.owner_id:
        return jsonify({'message': 'Unauthorized'}), 403

    try:
        origin = trip.origin
        destination = trip.destination


        google_location = GoogleGetLocation()
        distance_info = asyncio.run(google_location.get_distance(origin, destination)) 
        distance_km = int(distance_info['distance'].split(' ')[0].replace(',', '')) 

        truck = trip.truck
        truck.update_mileage(distance_km)
        truck.check_maintenance()


        remaining_km = truck.calculate_remaining_km_until_services()
    
        truck.check_maintenance()

        trip.status = 'Completed'

        db.session.commit()

        FleetAnalyticsModel.update_fleet_analytics(truck.owner_id)

        response = trip.to_json() 
        response.update(distance_info) 
        response.update(truck.to_json()) 
        response['remaining_km_until_services'] = remaining_km

        return jsonify(response), 200
    except Exception as e:
        return jsonify({'message': "Error completing the trip", 'error': str(e)}), 500



#eliminar viaje solamente el owner una vez que este en estado Completed puede eliminarlo
@trips.route('/<int:id>/delete', methods=['DELETE'])
@jwt_required()
@role_required(['owner'])
def delete_trip(id):
    trip = db.session.query(TripModel).get_or_404(id)
    if trip.status != 'Completed':
        return jsonify({'message': 'The trip has not been made yet to be eliminated'}), 403

    db.session.delete(trip)
    db.session.commit()
    return jsonify({'message': 'Trip deleted'}), 200