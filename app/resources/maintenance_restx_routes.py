"""
Rutas Flask-RESTX para el recurso de maintenance
"""
from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import MaintenanceModel, TruckModel, FleetAnalyticsModel, UserModel
from ..utils.decorators import role_required
from datetime import datetime, date
from ..swagger_models.maintenance_models import (
    maintenance_ns, create_maintenance_model, edit_maintenance_model, approve_maintenance_model,
    maintenance_list_model, maintenance_detail_model, create_maintenance_response_model,
    success_message_model, maintenance_stats_model, update_status_response_model
)


def serialize_dt(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: serialize_dt(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize_dt(x) for x in obj]
    return obj





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
            # Obtener el camión para calcular el kilometraje actual
            truck = TruckModel.query.get(data.get('truck_id'))
            if not truck:
                maintenance_ns.abort(404, message='Truck not found')
            
            mileage_interval = data.get('mileage_interval', 10000)
            current_mileage = truck.mileage
            
            new_maintenance = MaintenanceModel(
                description=data.get('description', ''),
                component=data.get('component', ''),
                truck_id=data.get('truck_id', ''),
                driver_id=data.get('driver_id', None),
                cost=data.get('cost', ''),
                status='Pending',
                mileage_interval=mileage_interval,
                last_maintenance_mileage=current_mileage,
                next_maintenance_mileage=current_mileage + mileage_interval,
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
class ListCompletedMaintenances(Resource):
    @maintenance_ns.response(200, 'Historial de mantenimientos completados obtenido exitosamente', maintenance_list_model)
    @maintenance_ns.response(404, 'Camión no encontrado')
    @jwt_required()
    @role_required(['owner'])
    def get(self, truck_id):
        """Listar el historial de mantenimientos completados de un camión"""
        truck = TruckModel.query.get_or_404(truck_id)
        
        # Primero, vamos a ver todos los mantenimientos para diagnosticar
        all_maintenances = MaintenanceModel.query.filter_by(truck_id=truck_id).all()
        
        # Debug: imprimir estados para diagnosticar
        print(f"Total mantenimientos para truck {truck_id}: {len(all_maintenances)}")
        for maint in all_maintenances:
            print(f"Maintenance ID: {maint.id}, Status: '{maint.status}', Component: {maint.component}")
        
        # Mostrar solo los mantenimientos completados para el historial
        completed_maintenances_ordered = MaintenanceModel.query.filter_by(
            truck_id=truck_id,
            status='Completed'
        ).order_by(MaintenanceModel.updated_at.desc()).all()
        
        print(f"Total mantenimientos completados para historial: {len(completed_maintenances_ordered)}")
        
        maintenances_list = []
        for maintenance in completed_maintenances_ordered:
            driver = db.session.query(UserModel).get(maintenance.driver_id)
            
            maintenance_data = {
                'maintenance_id': maintenance.id,
                'description': maintenance.description,
                'status': maintenance.status,
                'component': maintenance.component,
                'cost': maintenance.cost,
                'mileage_interval': maintenance.mileage_interval,
                'last_maintenance_mileage': maintenance.last_maintenance_mileage,
                'next_maintenance_mileage': maintenance.next_maintenance_mileage,
                'created_at': serialize_dt(maintenance.created_at),
                'updated_at': serialize_dt(maintenance.updated_at), 
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
            maintenances_list.append(maintenance_data)
        
        return {'maintenances': maintenances_list}, 200


@maintenance_ns.route('/<int:id>/approve')
class ApproveMaintenance(Resource):
    @maintenance_ns.expect(approve_maintenance_model)
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
                # Actualizar el kilometraje del último mantenimiento y el próximo
                maintenance.last_maintenance_mileage = truck.mileage
                maintenance.next_maintenance_mileage = truck.mileage + maintenance.maintenance_interval
                maintenance.accumulated_km = 0
                # Actualizar solo el componente base (costo = 0) que representa el estado actual
                truck.update_component(maintenance.component, 'Excellent')
            
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


@maintenance_ns.route('/<int:truck_id>/update-status')
class UpdateMaintenanceStatus(Resource):
    @maintenance_ns.response(200, 'Estados de mantenimiento actualizados exitosamente', update_status_response_model)
    @maintenance_ns.response(404, 'Camión no encontrado')
    @jwt_required()
    @role_required(['owner'])
    def post(self, truck_id):
        """
        Forzar la actualización del estado de todos los componentes de un camión.
        
        Esta ruta recalcula automáticamente:
        - El estado de cada componente basado en el kilometraje actual
        - El health_status del camión basado en los componentes
        - Los próximos mantenimientos programados
        
        No requiere JSON en el body, solo el truck_id en la URL.
        Útil para sincronizar datos después de correcciones manuales.
        """
        truck = TruckModel.query.get_or_404(truck_id)
        
        try:
            components_count = len(truck.maintenances)
            
            # Actualizar el estado de todos los componentes
            for maintenance in truck.maintenances:
                maintenance.update_status()
            
            # Actualizar el estado de salud del camión
            truck.update_health_status()
            
            db.session.commit()
            
            return {
                'message': 'Maintenance statuses updated successfully',
                'truck_id': truck_id,
                'health_status': truck.health_status,
                'components_updated': components_count
            }, 200
            
        except Exception as e:
            db.session.rollback()
            maintenance_ns.abort(500, message='Error updating maintenance statuses', error=str(e))


@maintenance_ns.route('/pending')
class ListPendingMaintenances(Resource):
    @maintenance_ns.response(200, 'Mantenimientos pendientes obtenidos exitosamente', maintenance_list_model)
    @maintenance_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['owner'])
    def get(self):
        """Listar todos los mantenimientos pendientes de aprobación"""
        try:
            current_user = get_jwt_identity()
            
            # Obtener todos los mantenimientos pendientes
            pending_maintenances = MaintenanceModel.query.filter_by(status='Pending').order_by(MaintenanceModel.created_at.desc()).all()
            
            maintenances_list = []
            for maintenance in pending_maintenances:
                # Obtener información del camión
                truck = TruckModel.query.get(maintenance.truck_id)
                
                # Obtener información del driver
                driver = UserModel.query.get(maintenance.driver_id) if maintenance.driver_id else None
                
                # Verificar que el camión pertenece al owner actual
                if truck and str(truck.owner_id) == str(current_user):
                    maintenance_data = {
                        'maintenance_id': maintenance.id,
                        'description': maintenance.description,
                        'status': maintenance.status,
                        'component': maintenance.component,
                        'cost': maintenance.cost,
                        'mileage_interval': maintenance.mileage_interval,
                        'last_maintenance_mileage': maintenance.last_maintenance_mileage,
                        'next_maintenance_mileage': maintenance.next_maintenance_mileage,
                        'created_at': serialize_dt(maintenance.created_at),
                        'updated_at': serialize_dt(maintenance.updated_at),
                        'truck': {
                            'truck_id': truck.truck_id,
                            'plate': truck.plate,
                            'model': truck.model,
                            'brand': truck.brand,
                            'mileage': truck.mileage
                        } if truck else None,
                        'driver': {
                            'id': driver.id,
                            'name': driver.name,
                            'surname': driver.surname,
                            'email': driver.email
                        } if driver else None
                    }
                    maintenances_list.append(maintenance_data)
            
            return {
                'pending_maintenances': maintenances_list,
                'total_pending': len(maintenances_list)
            }, 200
            
        except Exception as e:
            maintenance_ns.abort(500, message='Error getting pending maintenances', error=str(e))