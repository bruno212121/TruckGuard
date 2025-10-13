"""
Rutas Flask-RESTX para el recurso de trucks
"""
from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import TruckModel, MaintenanceModel, FleetAnalyticsModel, UserModel
from ..utils.decorators import role_required
from datetime import datetime
from ..swagger_models.truck_models import (
    truck_ns, create_truck_model, edit_truck_model, assign_truck_model, unassign_truck_model,
    truck_list_model, truck_detail_model, create_truck_response_model,
    assign_truck_response_model, unassign_truck_response_model, drivers_list_model, success_message_model,
    truck_components_status_model
)
from .component_restx_routes import ComponentManager




@truck_ns.route('/new')
class CreateTruck(Resource):
    @jwt_required()
    @role_required(['owner'])
    @truck_ns.expect(create_truck_model)
    @truck_ns.response(201, 'Camión creado exitosamente', create_truck_response_model)
    @truck_ns.response(400, 'Datos inválidos')
    @truck_ns.response(500, 'Error interno del servidor')
    def post(self):
        current_user = get_jwt_identity()
        print("current_user", current_user)
        data = request.get_json()
        print("data", data)
        
        driver_id = None 
        if 'driver_id' in data and data['driver_id']:
            driver_id = data['driver_id']
            driver = UserModel.query.filter_by(id=driver_id, rol='driver').first()
            if not driver:
                truck_ns.abort(400, message='Invalid driver id or the user does not have the driver role') 
        
        fa = FleetAnalyticsModel.get_or_create_for_owner(current_user) 

        try:
            new_truck = TruckModel(
                owner_id=current_user, 
                plate=data['plate'], 
                model=data['model'], 
                brand=data['brand'], 
                year=data['year'], 
                color=data['color'], 
                mileage=data['mileage'], 
                health_status=data.get('health_status', 'Good'), 
                fleetanalytics_id=fa.id,  
                driver_id=driver_id
            )
            db.session.add(new_truck)
            db.session.flush() 

            # Crear componentes usando ComponentManager
            components_data = data.get('components', None)  # None para usar componentes por defecto
            created_components = ComponentManager.create_components_for_truck(
                new_truck, components_data, driver_id
            )
            
            db.session.commit()
            FleetAnalyticsModel.update_fleet_analytics(current_user)

            return {'message': 'Truck created', 'truck': new_truck.truck_id}, 201
        except Exception as e:
            db.session.rollback()
            truck_ns.abort(500, message='Error creating truck', error=str(e))


@truck_ns.route('/all')
class ListTrucks(Resource):
    @truck_ns.response(200, 'Lista de camiones obtenida exitosamente', truck_list_model)
    @jwt_required()
    @role_required(['owner'])
    def get(self):
        """Listar todos los camiones"""
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
                'updated_at': truck.updated_at.isoformat() if truck.updated_at else None, 
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
        return {'trucks': trucks_list}, 200


#ver detalles de un camion y si el owner o el driver es el que esta logueado
@truck_ns.route('/<int:id>')
class TruckDetail(Resource):
    @truck_ns.response(200, 'Detalles del camión obtenidos exitosamente', truck_detail_model)
    @truck_ns.response(403, 'No autorizado')
    @truck_ns.response(404, 'Camión no encontrado')
    @jwt_required()
    @role_required(['owner','driver'])
    def get(self, id):
        """Obtener detalles de un camión específico"""
        current_user_id = get_jwt_identity()
        truck = db.session.query(TruckModel).get_or_404(id)

        if isinstance(current_user_id, str):
            current_user_id = int(current_user_id)

        if truck.owner_id != current_user_id and truck.driver_id != current_user_id:
            truck_ns.abort(403, message='Unauthorized')
        
        driver = truck.driver

        truck_data = {
            'truck_id': truck.truck_id, 
            'plate': truck.plate, 
            'model': truck.model, 
            'brand': truck.brand, 
            'year': truck.year,
            'mileage': truck.mileage, 
            'color': truck.color, 
            'status': truck.status, 
            'updated_at': truck.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

        if driver:
            truck_data['driver'] = {
                'id': driver.id,
                'name': driver.name,
                'email': driver.email,
                'phone': driver.phone
            }
        else:
            truck_data['driver'] = 'No driver assigned'

        return {'truck': truck_data}, 200


#editar un camion y si el owner es el que esta logueado
@truck_ns.route('/<int:id>/edit')
class EditTruck(Resource):
    @truck_ns.expect(edit_truck_model)
    @truck_ns.response(200, 'Camión actualizado exitosamente', success_message_model)
    @truck_ns.response(400, 'Datos inválidos')
    @truck_ns.response(403, 'No autorizado')
    @truck_ns.response(404, 'Camión no encontrado')
    @jwt_required()
    @role_required(['owner','driver'])
    def put(self, id):
       
        truck = db.session.query(TruckModel).get_or_404(id)

        current_user_id = str(get_jwt_identity())
        if str(truck.owner_id) != current_user_id: 
            truck_ns.abort(403, message='Unauthorized')
        
        data = request.get_json()
        if not data:
            truck_ns.abort(400, message='No input data provided')
        
        if 'status' in data:
            truck.status = data['status']

        truck.updated_at = datetime.utcnow() 

        db.session.commit()
        return {'message': 'Truck updated', 'truck': truck.truck_id}, 200


@truck_ns.route('/<int:id>/delete')
class DeleteTruck(Resource):
    @truck_ns.response(200, 'Camión eliminado exitosamente', success_message_model)
    @truck_ns.response(403, 'No autorizado')
    @truck_ns.response(404, 'Camión no encontrado')
    @jwt_required()
    @role_required(['owner'])
    def delete(self, id):
        """Eliminar un camión"""
        truck = db.session.query(TruckModel).get_or_404(id)
        current_user = get_jwt_identity()
        
        # Verificar que el camión pertenece al owner actual
        if str(truck.owner_id) != str(current_user):
            truck_ns.abort(403, message='Unauthorized')
        
        db.session.delete(truck)
        db.session.commit()
        return {'message': 'Truck deleted', 'truck': truck.truck_id}, 200


@truck_ns.route('/<int:id>/assign')
class AssignTruck(Resource):
    @truck_ns.expect(assign_truck_model)
    @truck_ns.response(200, 'Camión asignado exitosamente', assign_truck_response_model)
    @truck_ns.response(400, 'Datos inválidos')
    @truck_ns.response(403, 'No autorizado')
    @truck_ns.response(404, 'Camión no encontrado')
    @truck_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['owner'])
    def put(self, id):
        """Asignar un camión a un conductor"""
        try:
            truck = db.session.query(TruckModel).get_or_404(id)

            if truck.owner_id != truck.owner_id:
                truck_ns.abort(403, message='Not authorized')
            
            data = request.get_json()
            if not data or 'driver_id' not in data:
                truck_ns.abort(400, message='No input data provided or driver id missing')
            
            driver_id = data.get('driver_id')
            driver = UserModel.query.filter_by(id=driver_id, rol='driver').first()
            if not driver:
                truck_ns.abort(400, message='Invalid driver id or the user does not have the driver role')
            
            if truck.driver_id == driver_id:
                truck_ns.abort(400, message='Truck already assigned to this driver')
            
            truck.driver_id = data.get('driver_id')
            truck.updated_at = datetime.now()
            db.session.commit()

            return {
                'message': 'Truck assign', 
                'truck': truck.model, 
                'Name driver': driver.name, 
                'Surname driver': driver.surname
            }, 200

        except Exception as e:
            db.session.rollback()
            truck_ns.abort(500, message='Error assigning truck', error=str(e))


@truck_ns.route('/<int:id>/unassign')
class UnassignTruck(Resource):
    @truck_ns.expect(unassign_truck_model)
    @truck_ns.response(200, 'Conductor removido exitosamente', unassign_truck_response_model)
    @truck_ns.response(400, 'Datos inválidos')
    @truck_ns.response(403, 'No autorizado')
    @truck_ns.response(404, 'Camión no encontrado')
    @truck_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['owner'])
    def put(self, id):
        """Remover el conductor asignado a un camión"""
        try:
            truck = db.session.query(TruckModel).get_or_404(id)
            current_user = get_jwt_identity()

            # Verificar que el camión pertenece al owner actual
            if str(truck.owner_id) != str(current_user):
                truck_ns.abort(403, message='Not authorized')
            
            # Verificar que el camión tiene un conductor asignado
            if not truck.driver_id:
                truck_ns.abort(400, message='Truck has no driver assigned')
            
            # Obtener información del conductor antes de removerlo
            previous_driver = UserModel.query.get(truck.driver_id)
            previous_driver_name = f"{previous_driver.name} {previous_driver.surname}" if previous_driver else "Unknown"
            
            # Remover el conductor
            truck.driver_id = None
            truck.updated_at = datetime.now()
            db.session.commit()

            return {
                'message': 'Driver unassigned successfully', 
                'truck': truck.model, 
                'previous_driver': previous_driver_name
            }, 200

        except Exception as e:
            db.session.rollback()
            truck_ns.abort(500, message='Error unassigning truck', error=str(e))




@truck_ns.route('/drivers_without_truck')
class DriversWithoutTruck(Resource):
    @truck_ns.response(200, 'Conductores sin camión obtenidos exitosamente', drivers_list_model)
    @jwt_required()
    @role_required(['owner']) 
    def get(self):
        """Obtener lista de conductores sin camión asignado"""
        drivers = UserModel.query.filter_by(rol='driver').all()
        drivers_without_truck = []
        for driver in drivers:
            truck = TruckModel.query.filter_by(driver_id=driver.id).first()
            if not truck: 
                drivers_without_truck.append({
                    'id': driver.id,
                    'name': driver.name,
                    'surname': driver.surname,
                    'phone': driver.phone,
                    'role': driver.rol
                })
        return {'drivers': drivers_without_truck}, 200
