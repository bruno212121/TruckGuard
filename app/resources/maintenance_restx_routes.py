"""
Rutas Flask-RESTX para el recurso de maintenance
"""
from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import MaintenanceModel, TruckModel, FleetAnalyticsModel, UserModel
from ..utils.decorators import role_required
from datetime import datetime
from ..swagger_models.maintenance_models import (
    maintenance_ns, create_maintenance_model, edit_maintenance_model,
    maintenance_list_model, maintenance_detail_model, create_maintenance_response_model,
    success_message_model, maintenance_stats_model
)


@maintenance_ns.route('/new')
class CreateMaintenance(Resource):
    @maintenance_ns.expect(create_maintenance_model)
    @maintenance_ns.response(201, 'Mantenimiento creado exitosamente', create_maintenance_response_model)
    @maintenance_ns.response(400, 'Datos inválidos')
    @maintenance_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['owner', 'driver'])
    def post(self):
        """Crear un nuevo mantenimiento"""
        data = request.get_json()
        try:
            new_maintenance = MaintenanceModel(
                description=data.get('description', ''),
                component=data.get('component', ''),
                truck_id=data.get('truck_id', ''),
                driver_id=data.get('driver_id', None),
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

            return {'message': 'Maintenance created', 'maintenance': new_maintenance.id}, 201
        except Exception as e:
            db.session.rollback()
            maintenance_ns.abort(500, message='Error creating maintenance', error=str(e))


@maintenance_ns.route('/<int:id>/edit')
class EditMaintenance(Resource):
    @maintenance_ns.expect(edit_maintenance_model)
    @maintenance_ns.response(200, 'Mantenimiento actualizado exitosamente', success_message_model)
    @maintenance_ns.response(404, 'Mantenimiento no encontrado')
    @maintenance_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['owner', 'driver'])
    def patch(self, id):
        """Editar un mantenimiento"""
        maintenance = db.session.query(MaintenanceModel).get_or_404(id)
        data = request.get_json()
        
        if "description" in data:
            maintenance.description = data["description"]
        if "cost" in data:
            maintenance.cost = data["cost"]
        
        try:
            db.session.commit()
            return {
                'message': 'Maintenance updated', 
                'maintenance': maintenance.id
            }, 200
        except Exception as e:
            db.session.rollback()
            maintenance_ns.abort(500, message='Error updating maintenance', error=str(e))


@maintenance_ns.route('/<int:truck_id>/component/<int:component_id>')
class GetComponent(Resource):
    @maintenance_ns.response(200, 'Componente obtenido exitosamente', maintenance_detail_model)
    @maintenance_ns.response(404, 'Camión o componente no encontrado')
    @jwt_required()
    @role_required(['owner'])
    def get(self, truck_id, component_id):
        """Obtener un componente específico de un camión"""
        truck = TruckModel.query.get_or_404(truck_id)
        component = MaintenanceModel.query.get_or_404(component_id)

        if not component:
            maintenance_ns.abort(404, message='Component not found for this truck')
        
        driver = db.session.query(UserModel).get(component.driver_id)
        
        component_data = {
            'maintenance_id': component.id,
            'description': component.description,
            'status': component.status,
            'component': component.component,
            'cost': component.cost,
            'mileage_interval': component.mileage_interval,
            'last_maintenance_mileage': component.last_maintenance_mileage,
            'next_maintenance_mileage': component.next_maintenance_mileage,
            'created_at': component.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': component.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'truck': {
                'truck_id': truck.truck_id,
                'plate': truck.plate,
                'model': truck.model,
                'brand': truck.brand,
                'mileage': truck.mileage
            } if truck else 'No truck assigned',
            'driver': {
                'id': driver.id,
                'name': driver.name,
                'surname': driver.surname,
                'email': driver.email
            } if driver else 'No driver assigned'
        }
        
        return {'component': component_data}, 200


@maintenance_ns.route('/<int:truck_id>/components')
class ListComponents(Resource):
    @maintenance_ns.response(200, 'Componentes obtenidos exitosamente', maintenance_list_model)
    @maintenance_ns.response(404, 'Camión no encontrado')
    @jwt_required()
    @role_required(['owner'])
    def get(self, truck_id):
        """Listar todos los componentes de un camión"""
        truck = TruckModel.query.get_or_404(truck_id)
        components = truck.maintenances
        
        components_list = []
        for component in components:
            driver = db.session.query(UserModel).get(component.driver_id)
            
            component_data = {
                'maintenance_id': component.id,
                'description': component.description,
                'status': component.status,
                'component': component.component,
                'cost': component.cost,
                'mileage_interval': component.mileage_interval,
                'last_maintenance_mileage': component.last_maintenance_mileage,
                'next_maintenance_mileage': component.next_maintenance_mileage,
                'created_at': component.created_at,
                'updated_at': component.updated_at,
                'truck': {
                    'truck_id': truck.truck_id,
                    'plate': truck.plate,
                    'model': truck.model,
                    'brand': truck.brand,
                    'mileage': truck.mileage
                },
                'driver': {
                    'id': driver.id,
                    'name': driver.name,
                    'surname': driver.surname,
                    'email': driver.email
                } if driver else None
            }
            components_list.append(component_data)
        
        return {'maintenances': components_list}, 200


@maintenance_ns.route('/<int:id>/approve')
class ApproveMaintenance(Resource):
    @maintenance_ns.expect(edit_maintenance_model)
    @maintenance_ns.response(200, 'Estado de mantenimiento actualizado exitosamente')
    @maintenance_ns.response(400, 'Estado de aprobación requerido')
    @maintenance_ns.response(404, 'Mantenimiento no encontrado')
    @maintenance_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['owner'])
    def patch(self, id):
        """Aprobar o rechazar un mantenimiento"""
        maintenance = db.session.query(MaintenanceModel).get_or_404(id)
        data = request.get_json()
        approval_status = data.get('approval_status')
        
        if approval_status is None:
            maintenance_ns.abort(400, message='Approval status is required')
        
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

            return {'message': 'Maintenance status updated', 'status': maintenance.status}, 200
        
        except Exception as e:
            db.session.rollback()
            maintenance_ns.abort(500, message='Error updating maintenance status', error=str(e))


@maintenance_ns.route('/stats')
class MaintenanceStats(Resource):
    @maintenance_ns.response(200, 'Estadísticas obtenidas exitosamente', maintenance_stats_model)
    @jwt_required()
    @role_required(['owner'])
    def get(self):
        """Obtener estadísticas de mantenimiento"""
        total_maintenances = MaintenanceModel.query.count()
        pending_maintenances = MaintenanceModel.query.filter_by(status='Pending').count()
        completed_maintenances = MaintenanceModel.query.filter_by(status='Completed').count()
        
        # Calcular costos
        total_cost = db.session.query(db.func.sum(MaintenanceModel.cost)).scalar() or 0
        average_cost = total_cost / total_maintenances if total_maintenances > 0 else 0
        
        return {
            'total_maintenances': total_maintenances,
            'pending_maintenances': pending_maintenances,
            'completed_maintenances': completed_maintenances,
            'total_cost': float(total_cost),
            'average_cost': float(average_cost)
        }, 200
