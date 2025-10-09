"""
Rutas Flask-RESTX para el recurso de trips
"""
from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import TripModel, TruckModel, FleetAnalyticsModel, UserModel
from ..utils.decorators import role_required
from app.google.locations import GoogleGetLocation
from datetime import datetime, date
import asyncio
from ..swagger_models.trip_models import (
    trip_ns, create_trip_model, edit_trip_model, trip_list_model,
    trip_detail_model, create_trip_response_model, success_message_model,
    trip_filter_model
)

# ---- Helper: serialización segura de datetime/date a ISO8601 ----
def serialize_dt(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: serialize_dt(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize_dt(x) for x in obj]
    return obj


@trip_ns.route('/new')
class CreateTrip(Resource):
    @trip_ns.expect(create_trip_model)
    @trip_ns.response(201, 'Viaje creado exitosamente', create_trip_response_model)
    @trip_ns.response(409, 'Componentes en estado Fair requieren atención')
    @trip_ns.response(422, 'Componentes requieren mantenimiento crítico')
    @trip_ns.response(404, 'Camión o conductor no encontrado')
    @trip_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['owner'])
    def post(self):
        """Crear un nuevo viaje"""
        trip_json = request.get_json()
        origin = trip_json.get('origin')
        destination = trip_json.get('destination')
        truck_id = trip_json.get('truck_id')
        
        print(f"DEBUG: Creating trip with data: {trip_json}")
        print(f"DEBUG: Origin: {origin}, Destination: {destination}, Truck ID: {truck_id}")

        truck = TruckModel.query.get(truck_id)
        driver = UserModel.query.get(trip_json.get('driver_id'))

        if truck is None:
            trip_ns.abort(404, 
                error="RESOURCE_NOT_FOUND",
                severity="error",
                reason="truck_not_found",
                resource_id=truck_id,
                message="Truck not found"
            )
            
        if driver is None:
            trip_ns.abort(404, 
                error="RESOURCE_NOT_FOUND",
                severity="error",
                reason="driver_not_found",
                resource_id=trip_json.get('driver_id'),
                message="Driver not found"
            )

        fair_components = []
        maintenance_required_components = []
        
        for maintenance in truck.maintenances:
            if maintenance.status == 'Maintenance Required':
                maintenance_required_components.append(maintenance.component)
            elif maintenance.status == 'Fair':
                fair_components.append(maintenance.component)
        
        # Bloquear viaje si hay componentes que requieren mantenimiento (CRÍTICO)
        if maintenance_required_components:
            print(f"DEBUG: Blocking trip - components requiring maintenance: {maintenance_required_components}")
            components_list = ', '.join(maintenance_required_components)
            trip_ns.abort(422, 
                error="TRIP_BLOCKED_COMPONENTS",
                severity="critical",
                reason="components_requiring_maintenance",
                components=maintenance_required_components,
                message=f"Cannot create trip: Components requiring maintenance: {components_list}"
            )
        
        # Bloquear viaje si hay componentes en estado Fair (ADVERTENCIA)
        if fair_components:
            print(f"DEBUG: Blocking trip - components in Fair condition: {fair_components}")
            components_list = ', '.join(fair_components)
            trip_ns.abort(409, 
                error="TRIP_BLOCKED_COMPONENTS",
                severity="warning",
                reason="components_fair_condition",
                components=fair_components,
                message=f"Cannot create trip: Components in Fair condition need attention: {components_list}"
            )

        try:
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

            return {'message': 'Trip created', 'trip': new_trip.id}, 201

        except Exception as e:
            db.session.rollback()
            print(f"DEBUG: Error creating trip: {str(e)}")
            trip_ns.abort(500, 
                error="INTERNAL_SERVER_ERROR",
                severity="critical",
                reason="trip_creation_failed",
                message="Error creating trip",
                details=str(e)
            )


@trip_ns.route('/all')
class ListTrips(Resource):
    @trip_ns.response(200, 'Lista de viajes obtenida exitosamente', trip_list_model)
    @jwt_required()
    @role_required(['owner'])
    def get(self):
        """Listar todos los viajes con filtros opcionales"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        origin = request.args.get('origin')
        destination = request.args.get('destination')
        status = request.args.get('status')
        driver_id = request.args.get('driver_id', type=int)

        trips_query = TripModel.query
        if origin:
            trips_query = trips_query.filter(TripModel.origin.like(f'%{origin}%'))
        if destination:
            trips_query = trips_query.filter(TripModel.destination.like(f'%{destination}%'))
        if status:
            trips_query = trips_query.filter(TripModel.status.like(f'%{status}%'))
        if driver_id:
            trips_query = trips_query.filter(TripModel.driver_id == driver_id)

        trips = trips_query.slice((page - 1) * per_page, page * per_page).all()
        total_trips = trips_query.count()

        trips_list = []
        for trip in trips:
            driver = db.session.query(UserModel).get(trip.driver_id)
            truck = db.session.query(TruckModel).get(trip.truck_id)

            trip_data = {
                'trip_id': trip.id,
                'origin': trip.origin,
                'destination': trip.destination,
                'status': trip.status,
                'date': trip.date.isoformat() if trip.date else None,
                'created_at': trip.created_at.isoformat() if trip.created_at else None,
                'updated_at': trip.updated_at.isoformat() if trip.updated_at else None,
                'truck': {
                    'truck_id': truck.truck_id,
                    'plate': truck.plate,
                    'model': truck.model,
                    'brand': truck.brand
                } if truck else None,
                'driver': {
                    'id': driver.id,
                    'name': driver.name,
                    'surname': driver.surname,
                    'email': driver.email,
                    'phone': driver.phone
                } if driver else None
            }
            trips_list.append(trip_data)

        return serialize_dt({
            'trips': trips_list,
            'total': total_trips,
            'pages': (total_trips - 1) // per_page + 1,
            'page': page
        }), 200


@trip_ns.route('/<int:id>')
class TripDetail(Resource):
    @trip_ns.response(200, 'Detalles del viaje obtenidos exitosamente', trip_detail_model)
    @trip_ns.response(404, 'Viaje no encontrado')
    @jwt_required()
    @role_required(['owner'])
    def get(self, id):
        """Obtener detalles de un viaje específico"""
        trip = db.session.query(TripModel).get_or_404(id)
        driver = db.session.query(UserModel).get(trip.driver_id)
        truck = db.session.query(TruckModel).get(trip.truck_id)

        trip_data = {
            'trip_id': trip.id,
            'origin': trip.origin,
            'destination': trip.destination,
            'status': trip.status,
            'date': trip.date.strftime('%Y-%m-%d %H:%M:%S') if trip.date else None,
            'created_at': trip.created_at.strftime('%Y-%m-%d %H:%M:%S') if trip.created_at else None,
            'updated_at': trip.updated_at.strftime('%Y-%m-%d %H:%M:%S') if trip.updated_at else None,
            'driver': {
                'id': driver.id,
                'name': driver.name,
                'surname': driver.surname,
                'email': driver.email,
                'phone': driver.phone
            } if driver else 'No driver assigned',
            'truck': {
                'truck_id': truck.truck_id,
                'plate': truck.plate,
                'model': truck.model,
                'brand': truck.brand
            } if truck else 'No truck assigned'
        }

        if trip.status == 'Pending':
            try:
                google_location = GoogleGetLocation()
                distance_info = asyncio.run(google_location.get_distance(trip.origin, trip.destination))
                trip_data.update(distance_info)
            except Exception as e:
                trip_data['distance_error'] = str(e)

        return {'trip': trip_data}, 200


@trip_ns.route('/<int:id>/update')
class UpdateTrip(Resource):
    @trip_ns.expect(edit_trip_model)
    @trip_ns.response(200, 'Viaje actualizado exitosamente', success_message_model)
    @trip_ns.response(400, 'Estado inválido')
    @trip_ns.response(404, 'Viaje no encontrado')
    @trip_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['owner', 'driver'])
    def patch(self, id):
        """Actualizar un viaje (ambos roles pueden actualizar)"""
        trip = db.session.query(TripModel).get_or_404(id)
        trip_json = request.get_json()

        new_status = trip_json.get('status')
        if new_status and new_status not in ['Pending', 'In Course', 'Completed']:
            trip_ns.abort(400, message='Invalid status value')

        if new_status:
            trip.status = new_status

        try:
            db.session.commit()
            return {'message': 'Trip updated', 'trip': trip.id}, 200
        except Exception as e:
            db.session.rollback()
            trip_ns.abort(500, message='Error updating the trip', error=str(e))


@trip_ns.route('/<int:id>/complete')
class CompleteTrip(Resource):
    @trip_ns.response(200, 'Viaje completado exitosamente')
    @trip_ns.response(403, 'No autorizado')
    @trip_ns.response(404, 'Viaje no encontrado')
    @trip_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['driver', 'owner'])
    def patch(self, id):
        """Completar un viaje"""
        trip = db.session.query(TripModel).get_or_404(id)

        # ---- Autorización: owner siempre puede; driver solo si es su viaje ----
        user_id = int(get_jwt_identity())
        user = UserModel.query.get(user_id)
        if user is None:
            trip_ns.abort(403, message='Unauthorized')
        if user.rol != 'owner' and trip.driver_id != user_id:
            trip_ns.abort(403, message='Unauthorized')

        try:
            origin = trip.origin
            destination = trip.destination

            google_location = GoogleGetLocation()
            distance_info = asyncio.run(google_location.get_distance(origin, destination))
            distance_km = int(distance_info['distance'].split(' ')[0].replace(',', ''))

            # Usar la nueva función complete_trip que actualiza automáticamente el kilometraje y degrada componentes
            trip.complete_trip(distance_km)

            # Verificar el estado de salud después del viaje
            truck = trip.truck
            remaining_km = truck.calculate_remaining_km_until_services()

            FleetAnalyticsModel.update_fleet_analytics(truck.owner_id)

            response = trip.to_json()
            response.update(distance_info)
            response.update(truck.to_json())
            response['remaining_km_until_services'] = remaining_km

            return serialize_dt(response), 200
        except Exception as e:
            trip_ns.abort(500, message='Error completing the trip', error=str(e))


@trip_ns.route('/<int:id>/delete')
class DeleteTrip(Resource):
    @trip_ns.response(200, 'Viaje eliminado exitosamente', success_message_model)
    @trip_ns.response(403, 'Viaje no completado o no autorizado')
    @trip_ns.response(404, 'Viaje no encontrado')
    @jwt_required()
    @role_required(['owner'])
    def delete(self, id):
        """Eliminar un viaje (solo owner, solo si está completado)"""
        trip = db.session.query(TripModel).get_or_404(id)

        if trip.status != 'Completed':
            trip_ns.abort(403, message='The trip has not been completed yet to be eliminated')

        db.session.delete(trip)
        db.session.commit()
        return {'message': 'Trip deleted', 'trip': trip.id}, 200
