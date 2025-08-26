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
    truck_ns, create_truck_model, edit_truck_model, assign_truck_model,
    truck_list_model, truck_detail_model, create_truck_response_model,
    assign_truck_response_model, drivers_list_model, success_message_model
)




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

            def next_due(current_mileage, interval):
                return ((current_mileage // interval) + 1) * interval  
            
            def last_done(current_mileage, interval):
                return ((current_mileage // interval) * interval) 

            current_mileage = new_truck.mileage 

            # Componentes por defecto si no se proporcionan
            default_components = [
                {"name": "Filtros",     "interval": 10000},
                {"name": "Aceite",      "interval":  5000},
                {"name": "Inyecciones", "interval":  8000},
                {"name": "Frenos",      "interval":  9500},
            ]

            # Si se proporcionan componentes personalizados, usarlos; si no, usar los por defecto
            components = data.get('components', default_components)

            for component in components:
                # Si el componente tiene valores personalizados, usarlos; si no, calcular automáticamente
                if 'last_maintenance_mileage' in component and 'next_maintenance_mileage' in component:
                    last_mileage = component['last_maintenance_mileage']
                    next_mileage = component['next_maintenance_mileage']
                else:
                    next_mileage = next_due(current_mileage, component['interval'])
                    last_mileage = last_done(current_mileage, component['interval'])

                # Estado del componente: personalizado o por defecto
                component_status = component.get('status', 'Excellent')

                maintenance = MaintenanceModel(
                    description=f'{component["name"]} maintenance', 
                    status=component_status, 
                    component=component['name'], 
                    cost=0, 
                    mileage_interval=component['interval'],
                    last_maintenance_mileage=last_mileage,
                    next_maintenance_mileage=next_mileage,
                    truck_id=new_truck.truck_id,
                    driver_id=driver_id,
                    maintenance_interval=component['interval']
                )
                db.session.add(maintenance)
            
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


@truck_ns.route('/<int:id>')
class TruckDetail(Resource):
    @truck_ns.response(200, 'Detalles del camión obtenidos exitosamente', truck_detail_model)
    @truck_ns.response(403, 'No autorizado')
    @truck_ns.response(404, 'Camión no encontrado')
    @jwt_required()
    @role_required(['owner'])
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


@truck_ns.route('/<int:id>/edit')
class EditTruck(Resource):
    @truck_ns.expect(edit_truck_model)
    @truck_ns.response(200, 'Camión actualizado exitosamente', success_message_model)
    @truck_ns.response(400, 'Datos inválidos')
    @truck_ns.response(403, 'No autorizado')
    @truck_ns.response(404, 'Camión no encontrado')
    @jwt_required()
    @role_required(['owner'])
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
        if truck.owner_id != truck.owner_id:
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
