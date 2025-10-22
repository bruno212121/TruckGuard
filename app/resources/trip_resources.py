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
    
    # Obtener distancia del viaje ANTES de validar componentes
    try:
        google_location = GoogleGetLocation()
        distance_info = asyncio.run(google_location.get_distance(origin, destination))
        trip_distance = distance_info.get('distance_km', 0)
    except Exception as e:
        print(f"DEBUG: Error getting distance: {str(e)}")
        trip_distance = 0  # Si no se puede obtener distancia, asumir 0
    
    fair_components = []
    risk_components = []
    
    # Validar cada componente considerando la distancia del viaje
    for maintenance in truck.maintenances: 
        if maintenance.status == 'Maintenance Required':
            return jsonify({'error': f'No se puede crear el viaje: El componente {maintenance.component} requiere mantenimiento inmediato'}), 400
        elif maintenance.status == 'Fair':
            fair_components.append(maintenance.component)
        elif maintenance.status == 'Good':
            # Calcular si el viaje pondría el componente en riesgo
            projected_km = maintenance.accumulated_km + trip_distance
            projected_percentage = (projected_km / maintenance.maintenance_interval) * 100
            
            # Si el viaje llevaría el componente a Fair o peor, es riesgo
            if projected_percentage >= 80:  # Fair threshold
                risk_components.append({
                    'component': maintenance.component,
                    'current_status': maintenance.status,
                    'current_km': maintenance.accumulated_km,
                    'projected_km': projected_km,
                    'projected_percentage': projected_percentage,
                    'maintenance_interval': maintenance.maintenance_interval
                })
    
    # Preparar advertencias para componentes en riesgo (ALTO RIESGO)
    risk_warnings = []
    if risk_components:
        for rc in risk_components:
            risk_warnings.append({
                'component': rc['component'],
                'current_status': rc['current_status'],
                'current_km': rc['current_km'],
                'projected_km': rc['projected_km'],
                'projected_percentage': rc['projected_percentage'],
                'maintenance_interval': rc['maintenance_interval'],
                'risk_level': 'HIGH' if rc['projected_percentage'] >= 100 else 'MEDIUM'
            })

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
    
    # Agregar advertencias por componentes en riesgo
    if risk_warnings:
        response['risk_warnings'] = risk_warnings
        
        # Crear mensaje de advertencia detallado
        high_risk_components = [rw for rw in risk_warnings if rw['risk_level'] == 'HIGH']
        medium_risk_components = [rw for rw in risk_warnings if rw['risk_level'] == 'MEDIUM']
        
        warning_messages = []
        
        if high_risk_components:
            high_risk_names = [rc['component'] for rc in high_risk_components]
            warning_messages.append(f"ALTO RIESGO: Los siguientes componentes llegaran al 100% o mas durante el viaje y tienen MUY ALTA probabilidad de fallar: {', '.join(high_risk_names)}")
        
        if medium_risk_components:
            medium_risk_names = [rc['component'] for rc in medium_risk_components]
            warning_messages.append(f"RIESGO MEDIO: Los siguientes componentes llegaran al 80% o mas durante el viaje y tienen probabilidad de fallar: {', '.join(medium_risk_names)}")
        
        response['risk_warning_message'] = " | ".join(warning_messages)
        response['trip_distance'] = trip_distance
        response['recommendation'] = "Se recomienda realizar mantenimiento preventivo antes del viaje para evitar fallas mecanicas."
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
        response['fair_components_warning'] = fair_components
        response['warning_message'] = f"ADVERTENCIA: Los siguientes componentes están en estado Fair y tienen alta probabilidad de fallar durante el viaje: {', '.join(fair_components)}"

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

    # Detectar si el viaje cambia de "In Course" a "Completed"
    was_in_course = trip.status == 'In Course'
    is_being_completed = new_status == 'Completed'
    
    if was_in_course and is_being_completed:
        # Cuando se completa un viaje desde "In Course", usar lógica simplificada
        try:
            origin = trip.origin
            destination = trip.destination

            google_location = GoogleGetLocation()
            distance_info = asyncio.run(google_location.get_distance(origin, destination))
            distance_km = int(distance_info['distance'].split(' ')[0].replace(',', ''))

            truck = trip.truck
            
            # Verificar estado ANTES del viaje
            components_before = []
            for maintenance in truck.maintenances:
                components_before.append({
                    'component': maintenance.component, 
                    'status': maintenance.status
                })

            # Completar viaje usando el método simplificado
            trip.complete_trip(distance_km)
            
            # Verificar cambios después del viaje
            components_reaching_limit = []
            for maintenance in truck.maintenances:
                component_before = next((c for c in components_before if c['component'] == maintenance.component), None)
                if component_before and component_before['status'] != 'Maintenance Required' and maintenance.status == 'Maintenance Required':
                    components_reaching_limit.append(maintenance.component)

            FleetAnalyticsModel.update_fleet_analytics(truck.owner_id)

            response = {
                'message': 'Trip completed and updated', 
                'trip': trip.to_json(),
                'distance_km': distance_km,
                'remaining_km_until_services': truck.calculate_remaining_km_until_services()
            }
            
            # Información sobre degradación
            if components_reaching_limit:
                response['components_reaching_maintenance_limit'] = components_reaching_limit
                response['warning_message'] = f"Los siguientes componentes alcanzaron su límite de mantenimiento: {', '.join(components_reaching_limit)}"

            return jsonify(response), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Error completing trip during status update', 'error': str(e)}), 500

    # Verificar si el viaje cambia a "In Course" - validar que los componentes puedan realizar el viaje
    is_starting_trip = new_status == 'In Course' and trip.status != 'In Course'
    components_at_risk = []
    fair_components_warning = []
    
    if is_starting_trip:
        truck = trip.truck
        maintenance_required_components = []
        fair_components = []
        
        # Verificar estado actual de componentes
        for maintenance in truck.maintenances:
            if maintenance.status == 'Maintenance Required':
                maintenance_required_components.append(maintenance.component)
            elif maintenance.status == 'Fair':
                fair_components.append(maintenance.component)
        
        # Si hay componentes que requieren mantenimiento crítico, bloquear el viaje
        if maintenance_required_components:
            components_list = ', '.join(maintenance_required_components)
            return jsonify({
                'error': 'TRIP_BLOCKED_COMPONENTS',
                'severity': 'critical',
                'reason': 'components_requiring_maintenance',
                'components': maintenance_required_components,
                'message': f'Cannot start trip: Components requiring maintenance: {components_list}'
            }), 422
        
        # Registrar componentes en estado Fair como advertencia (NO bloquear)
        if fair_components:
            fair_components_warning = fair_components.copy()
        
        # Verificar si algún componente está cerca de su límite de mantenimiento
        try:
            origin = trip.origin
            destination = trip.destination
            google_location = GoogleGetLocation()
            distance_info = asyncio.run(google_location.get_distance(origin, destination))
            distance_km = int(distance_info['distance'].split(' ')[0].replace(',', ''))
            
            for maintenance in truck.maintenances:
                # Si el componente está cerca de su límite (menos de 20% del intervalo restante)
                km_remaining = maintenance.next_maintenance_mileage - truck.mileage
                if km_remaining > 0 and distance_km >= (km_remaining * 0.8):
                    components_at_risk.append(maintenance.component)
                    
        except Exception as e:
            # Si no se puede calcular la distancia, continuar sin esta validación adicional
            pass

    # Para otros cambios de estado, solo actualizar el estado
    trip.status = new_status  # Actualizando el estado.

    try:
        db.session.commit() 
        response = {'message': 'Trip updated', 'trip': trip.to_json()}
        
        # Incluir advertencias si el viaje está iniciando
        if is_starting_trip:
            warnings = []
            
            # Advertencia sobre componentes en estado Fair (alta probabilidad de falla)
            if fair_components_warning:
                response['fair_components_warning'] = fair_components_warning
                warnings.append(f"ADVERTENCIA: Los siguientes componentes están en estado Fair y tienen alta probabilidad de fallar durante el viaje: {', '.join(fair_components_warning)}")
            
            # Advertencia sobre componentes cerca del límite
            if components_at_risk:
                response['components_at_risk'] = components_at_risk
                warnings.append(f"Los siguientes componentes están cerca de su límite de mantenimiento: {', '.join(components_at_risk)}")
            
            # Combinar todas las advertencias en un mensaje
            if warnings:
                response['warning_message'] = " | ".join(warnings)
        
        return jsonify(response), 200
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
        
        # Verificar estado ANTES del viaje
        components_before = []
        for maintenance in truck.maintenances:
            components_before.append({
                'component': maintenance.component, 
                'status': maintenance.status
            })

        # Completar viaje usando el método simplificado
        trip.complete_trip(distance_km)
        
        # Verificar cambios después del viaje
        components_reaching_limit = []
        for maintenance in truck.maintenances:
            component_before = next((c for c in components_before if c['component'] == maintenance.component), None)
            if component_before and component_before['status'] != 'Maintenance Required' and maintenance.status == 'Maintenance Required':
                components_reaching_limit.append(maintenance.component)

        FleetAnalyticsModel.update_fleet_analytics(truck.owner_id)

        response = trip.to_json() 
        response.update(distance_info) 
        response.update(truck.to_json()) 
        response['remaining_km_until_services'] = truck.calculate_remaining_km_until_services()
        
        # Información sobre degradación
        if components_reaching_limit:
            response['components_reaching_maintenance_limit'] = components_reaching_limit
            response['warning_message'] = f"Los siguientes componentes alcanzaron su límite de mantenimiento: {', '.join(components_reaching_limit)}"

        return jsonify(response), 200
    except Exception as e:
        print(f"ERROR completando viaje en trip_resources: {str(e)}")
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