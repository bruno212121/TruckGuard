from flask_restful import Resource
from flask import request, jsonify, Blueprint
from .. import db
from ..models import TripModel
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

        # Obtener la distancia y duración usando GoogleGetLocation
    google_location = GoogleGetLocation()
    distance_info = asyncio.run(google_location.get_distance(origin, destination))

        # Crear una nueva instancia de TripModel
    new_trip = TripModel(
            origin=origin,
            destination=destination,
            status=trip_json.get('status', 'Pending'),
            driver_id=trip_json.get('driver_id'),
            truck_id=trip_json.get('truck_id'),
    )

    db.session.add(new_trip)
    db.session.commit()

    # Agregar la distancia y la duración a la respuesta
    response = new_trip.to_json()
    response.update(distance_info)

    return response, 201

#listar todos los viajes
@trips.route('/all', methods=['GET'])
@jwt_required()
@role_required(['owner'])
def list_trips():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    start = (page - 1) * per_page
    end = start + per_page

    trips_query = TripModel.query

    if request.get_json():
        filters = request.get_json().items()
        for key, value in filters:
            if key == 'origin':
                trips_query = trips_query.filter(TripModel.origin.like(f'%{value}%'))
            elif key == 'destination':
                trips_query = trips_query.filter(TripModel.destination.like(f'%{value}%'))
            elif key == 'status':
                trips_query = trips_query.filter(TripModel.status.like(f'%{value}%'))
            elif key == 'driver_id':
                trips_query = trips_query.filter(TripModel.driver_id == value)
    
    trips = trips_query.slice(start, end).all()

    total_trips = trips_query.count()

    total_pages = (total_trips - 1) // per_page + 1

    return jsonify({
        'trips': [trip.to_json() for trip in trips],
        'total': total_trips,
        'pages': total_pages,
        'page': page
    }), 200


@trips.route('/<int:id>', methods=['GET'])
@jwt_required()
@role_required(['owner'])
def view_trip(id):
    trip = db.session.query(TripModel).get_or_404(id)
    trip_data = trip.to_json()
    google_location = GoogleGetLocation()
    distance_info = asyncio.run(google_location.get_distance(trip.origin, trip.destination))

    #si el estado es pending se agrega la distancia y la duracion
    if trip.status == 'Pending':
        trip_data.update(distance_info) 
    #si el estado es completed se dice solamente el origen y destino del viaje
    elif trip.status == 'Completed':
        trip_data = {
            'origin': trip.origin,
            'destination': trip.destination,
            'status': trip.status,
            'updated_at': trip.updated_at,
            'driver_id': trip.driver_id,
            'truck_id': trip.truck_id
        }
    return jsonify({'trip': trip_data}), 200


@trips.route('/<int:id>/edit', methods=['PUT'])
@jwt_required()
#solo el owner o el driver con el id del driver pueden editar el viaje
@role_required(['owner', 'driver'])
def edit_trip(id):
    trip = db.session.query(TripModel).get_or_404(id)
    if trip.driver_id != trip.driver_id and trip.owner_id != trip.owner_id:
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json() 
    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    trip.status = data.get('status', trip.status)
    trip.updated_at = datetime.now()
    db.session.commit()

    return jsonify({'message': 'Trip updated', 'trip Origin': trip.origin, 'trip Destination': trip.destination, 'status': trip.status, 'updated_at': trip.updated_at}), 200


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