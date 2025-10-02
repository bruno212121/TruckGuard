"""
Rutas Flask-RESTX para el recurso de componentes
"""
from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import MaintenanceModel, TruckModel, UserModel
from ..utils.decorators import role_required
from datetime import datetime, date
from ..swagger_models.component_models import (
    component_ns, component_status_model, component_list_model,
    create_component_model, component_detail_model
)


def serialize_dt(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: serialize_dt(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize_dt(x) for x in obj]
    return obj


class ComponentManager:
    """Clase para manejar la lógica de componentes de manera centralizada"""
    
    @staticmethod
    def get_default_components():
        """Retorna los componentes por defecto para un camión nuevo"""
        return [
            {"name": "Filtros",     "interval": 10000},
            {"name": "Aceite",      "interval":  5000},
            {"name": "Inyecciones", "interval":  8000},
            {"name": "Frenos",      "interval":  9500},
            {"name": "Neumático",   "interval": 12000},
        ]
    
    @staticmethod
    def calculate_next_maintenance(current_mileage, interval):
        """Calcula el próximo mantenimiento basado en el kilometraje actual"""
        return ((current_mileage // interval) + 1) * interval
    
    @staticmethod
    def calculate_last_maintenance(current_mileage, interval):
        """Calcula el último mantenimiento basado en el kilometraje actual"""
        # Para la creación inicial, siempre usar el kilometraje actual como último mantenimiento
        # Esto hace que todos los componentes se creen en estado "Excellent"
        return current_mileage
    
    @staticmethod
    def calculate_initial_status(current_mileage, last_maintenance_mileage, interval):
        """Calcula el estado inicial del componente basado en el kilometraje actual"""
        km_since_last = current_mileage - last_maintenance_mileage
        
        # Si el kilometraje actual es exactamente el último mantenimiento, está recién mantenido
        if km_since_last == 0:
            return 'Excellent'
        
        percentage = (km_since_last / interval) * 100
        
        if percentage >= 100:
            return 'Maintenance Required'
        elif percentage >= 80:
            return 'Fair'
        elif percentage >= 60:
            return 'Good'
        elif percentage >= 40:
            return 'Very Good'
        elif percentage >= 20:
            return 'Good'
        else:
            return 'Excellent'
    
    @staticmethod
    def create_components_for_truck(truck, components_data=None, driver_id=None):
        """Crea los componentes para un camión"""
        current_mileage = truck.mileage
        
        # Usar componentes por defecto si no se proporcionan
        if components_data is None:
            components_data = ComponentManager.get_default_components()
        
        created_components = []
        
        for component_data in components_data:
            # Calcular próximos mantenimientos
            if 'last_maintenance_mileage' in component_data and 'next_maintenance_mileage' in component_data:
                last_mileage = component_data['last_maintenance_mileage']
                next_mileage = component_data['next_maintenance_mileage']
            else:
                next_mileage = ComponentManager.calculate_next_maintenance(current_mileage, component_data['interval'])
                last_mileage = ComponentManager.calculate_last_maintenance(current_mileage, component_data['interval'])
            
            # Calcular estado inicial
            if 'status' in component_data:
                component_status = component_data['status']
            else:
                component_status = ComponentManager.calculate_initial_status(
                    current_mileage, last_mileage, component_data['interval']
                )
            
            # Crear el componente
            maintenance = MaintenanceModel(
                description=f'{component_data["name"]} maintenance',
                status=component_status,
                component=component_data['name'],
                cost=0,
                mileage_interval=component_data['interval'],
                last_maintenance_mileage=last_mileage,
                next_maintenance_mileage=next_mileage,
                truck_id=truck.truck_id,
                driver_id=driver_id,
                maintenance_interval=component_data['interval']
            )
            
            db.session.add(maintenance)
            created_components.append(maintenance)
        
        return created_components


@component_ns.route('/<int:truck_id>/status')
class GetTruckComponentsStatus(Resource):
    @component_ns.response(200, 'Estado de componentes obtenido exitosamente', component_status_model)
    @component_ns.response(404, 'Camión no encontrado')
    @jwt_required()
    @role_required(['owner'])
    def get(self, truck_id):
        """Obtener el estado actual de salud de todos los componentes de un camión"""
        try:
            truck = TruckModel.query.get_or_404(truck_id)
            current_user = get_jwt_identity()

            # Verificar que el camión pertenece al owner actual
            if str(truck.owner_id) != str(current_user):
                component_ns.abort(403, message='Not authorized')
            
            # Obtener todos los componentes del camión
            components = truck.maintenances
            
            # Solo actualizar el estado de los componentes si el camión ha acumulado kilómetros
            # Si el camión no ha hecho viajes, mantener el estado inicial
            if truck.mileage > 0:
                for component in components:
                    component.update_status()
            
            # Agrupar componentes por nombre y obtener el más reciente de cada uno
            components_by_name = {}
            for component in components:
                component_name = component.component
                if component_name not in components_by_name:
                    components_by_name[component_name] = component
                else:
                    # Mantener el componente con el ID más alto (más reciente)
                    if component.id > components_by_name[component_name].id:
                        components_by_name[component_name] = component
            
            components_status = []
            components_requiring_maintenance = 0
            
            for component_name, component in components_by_name.items():
                # Calcular kilómetros restantes
                km_remaining = max(0, component.next_maintenance_mileage - truck.mileage)
                
                # Calcular porcentaje de salud
                if component.maintenance_interval > 0:
                    km_since_last = truck.mileage - component.last_maintenance_mileage
                    health_percentage = max(0, 100 - (km_since_last / component.maintenance_interval) * 100)
                else:
                    health_percentage = 100
                
                # Contar componentes que requieren mantenimiento
                if component.status == 'Maintenance Required':
                    components_requiring_maintenance += 1
                
                component_data = {
                    'component_name': component.component,
                    'current_status': component.status,
                    'health_percentage': int(health_percentage),
                    'last_maintenance_mileage': component.last_maintenance_mileage,
                    'next_maintenance_mileage': component.next_maintenance_mileage,
                    'km_remaining': km_remaining,
                    'maintenance_interval': component.maintenance_interval
                }
                components_status.append(component_data)
            
            response_data = {
                'truck_id': truck.truck_id,
                'plate': truck.plate,
                'model': truck.model,
                'brand': truck.brand,
                'current_mileage': truck.mileage,
                'overall_health_status': truck.health_status,
                'components': components_status,
                'total_components': len(components_status),
                'components_requiring_maintenance': components_requiring_maintenance,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return response_data, 200
            
        except Exception as e:
            component_ns.abort(500, message='Error getting components status', error=str(e))


@component_ns.route('/<int:truck_id>/list')
class ListTruckComponents(Resource):
    @component_ns.response(200, 'Componentes del camión obtenidos exitosamente', component_list_model)
    @component_ns.response(404, 'Camión no encontrado')
    @jwt_required()
    @role_required(['owner'])
    def get(self, truck_id):
        """Listar todos los componentes de un camión"""
        try:
            truck = TruckModel.query.get_or_404(truck_id)
            current_user = get_jwt_identity()

            # Verificar que el camión pertenece al owner actual
            if str(truck.owner_id) != str(current_user):
                component_ns.abort(403, message='Not authorized')
            
            components = truck.maintenances
            components_list = []
            
            for component in components:
                component_data = {
                    'component_id': component.id,
                    'component_name': component.component,
                    'status': component.status,
                    'description': component.description,
                    'cost': component.cost,
                    'mileage_interval': component.mileage_interval,
                    'last_maintenance_mileage': component.last_maintenance_mileage,
                    'next_maintenance_mileage': component.next_maintenance_mileage,
                    'maintenance_interval': component.maintenance_interval,
                    'created_at': serialize_dt(component.created_at),
                    'updated_at': serialize_dt(component.updated_at)
                }
                components_list.append(component_data)
            
            return {
                'truck_id': truck_id,
                'components': components_list,
                'total_components': len(components_list)
            }, 200
            
        except Exception as e:
            component_ns.abort(500, message='Error listing components', error=str(e))


@component_ns.route('/<int:truck_id>/add')
class AddComponent(Resource):
    @component_ns.expect(create_component_model)
    @component_ns.response(201, 'Componente agregado exitosamente', component_detail_model)
    @component_ns.response(400, 'Datos inválidos')
    @component_ns.response(404, 'Camión no encontrado')
    @jwt_required()
    @role_required(['owner'])
    def post(self, truck_id):
        """Agregar un nuevo componente a un camión"""
        try:
            truck = TruckModel.query.get_or_404(truck_id)
            current_user = get_jwt_identity()

            # Verificar que el camión pertenece al owner actual
            if str(truck.owner_id) != str(current_user):
                component_ns.abort(403, message='Not authorized')
            
            data = request.get_json()
            
            # Calcular próximos mantenimientos
            current_mileage = truck.mileage
            interval = data.get('interval', 10000)
            
            next_mileage = ComponentManager.calculate_next_maintenance(current_mileage, interval)
            last_mileage = ComponentManager.calculate_last_maintenance(current_mileage, interval)
            
            # Calcular estado inicial
            component_status = ComponentManager.calculate_initial_status(
                current_mileage, last_mileage, interval
            )
            
            # Crear el componente
            maintenance = MaintenanceModel(
                description=data.get('description', f'{data["name"]} maintenance'),
                status=component_status,
                component=data['name'],
                cost=data.get('cost', 0),
                mileage_interval=interval,
                last_maintenance_mileage=last_mileage,
                next_maintenance_mileage=next_mileage,
                truck_id=truck.truck_id,
                driver_id=data.get('driver_id'),
                maintenance_interval=interval
            )
            
            db.session.add(maintenance)
            db.session.commit()
            
            return {
                'message': 'Component added successfully',
                'component': {
                    'component_id': maintenance.id,
                    'component_name': maintenance.component,
                    'status': maintenance.status,
                    'description': maintenance.description,
                    'cost': maintenance.cost,
                    'mileage_interval': maintenance.mileage_interval,
                    'last_maintenance_mileage': maintenance.last_maintenance_mileage,
                    'next_maintenance_mileage': maintenance.next_maintenance_mileage,
                    'maintenance_interval': maintenance.maintenance_interval
                }
            }, 201
            
        except Exception as e:
            db.session.rollback()
            component_ns.abort(500, message='Error adding component', error=str(e))


@component_ns.route('/debug/calculate-status')
class DebugCalculateStatus(Resource):
    @component_ns.response(200, 'Cálculo de estado obtenido exitosamente')
    def get(self):
        """Endpoint de debug para verificar el cálculo de estados de componentes"""
        current_mileage = 87500  # Probando con un kilometraje aleatorio
        
        default_components = ComponentManager.get_default_components()
        debug_results = []
        
        for component in default_components:
            interval = component['interval']
            last_mileage = ComponentManager.calculate_last_maintenance(current_mileage, interval)
            next_mileage = ComponentManager.calculate_next_maintenance(current_mileage, interval)
            status = ComponentManager.calculate_initial_status(current_mileage, last_mileage, interval)
            
            km_since_last = current_mileage - last_mileage
            percentage = (km_since_last / interval) * 100
            
            debug_results.append({
                'component_name': component['name'],
                'interval': interval,
                'current_mileage': current_mileage,
                'last_maintenance_mileage': last_mileage,
                'next_maintenance_mileage': next_mileage,
                'km_since_last': km_since_last,
                'percentage': round(percentage, 2),
                'calculated_status': status
            })
        
        return {
            'current_mileage': current_mileage,
            'components_debug': debug_results
        }, 200
