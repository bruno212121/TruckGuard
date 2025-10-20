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
    create_component_model, component_detail_model, bulk_components_request_model,
    bulk_components_response_model
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
                
                # Calcular porcentaje de salud basado en el estado del componente
                if component.status == 'Excellent':
                    health_percentage = 90  # 100% a 80%
                elif component.status == 'Very Good':
                    health_percentage = 70  # 80% a 60%
                elif component.status == 'Good':
                    health_percentage = 50  # 60% a 40%
                elif component.status == 'Fair':
                    health_percentage = 30  # 40% a 20%
                elif component.status == 'Maintenance Required':
                    health_percentage = 10  # 20% a 0%
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
    @component_ns.response(200, 'Componentes actuales del camión obtenidos exitosamente', component_list_model)
    @component_ns.response(404, 'Camión no encontrado')
    @jwt_required()
    @role_required(['owner'])
    def get(self, truck_id):
        """Listar solo los componentes base actuales del camión (costo = 0)"""
        try:
            truck = TruckModel.query.get_or_404(truck_id)
            current_user = get_jwt_identity()

            # Verificar que el camión pertenece al owner actual
            if str(truck.owner_id) != str(current_user):
                component_ns.abort(403, message='Not authorized')
            
            # Filtrar solo componentes base (costo = 0) que representan el estado actual
            base_components = [comp for comp in truck.maintenances if comp.cost == 0]
            components_list = []
            
            for component in base_components:
                # Actualizar el estado del componente basado en el kilometraje actual
                component.update_status()
                
                component_data = {
                    'component_id': component.id,
                    'component_name': component.component,
                    'status': component.status,  # Estado actual calculado
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
                'total_components': len(components_list),
                'note': 'Solo componentes base del camión (costo = 0)'
            }, 200
            
        except Exception as e:
            component_ns.abort(500, message='Error listing components', error=str(e))


@component_ns.route('/<int:truck_id>/history')
class ListTruckMaintenanceHistory(Resource):
    @component_ns.response(200, 'Historial de mantenimientos obtenido exitosamente', component_list_model)
    @component_ns.response(404, 'Camión no encontrado')
    @jwt_required()
    @role_required(['owner'])
    def get(self, truck_id):
        """Listar el historial de mantenimientos realizados (costo > 0)"""
        try:
            truck = TruckModel.query.get_or_404(truck_id)
            current_user = get_jwt_identity()

            # Verificar que el camión pertenece al owner actual
            if str(truck.owner_id) != str(current_user):
                component_ns.abort(403, message='Not authorized')
            
            # Filtrar solo mantenimientos realizados (costo > 0)
            maintenance_history = [comp for comp in truck.maintenances if comp.cost > 0]
            maintenance_list = []
            
            # Ordenar por fecha de creación (más reciente primero)
            maintenance_history.sort(key=lambda x: x.created_at, reverse=True)
            
            for maintenance in maintenance_history:
                maintenance_data = {
                    'maintenance_id': maintenance.id,
                    'component_name': maintenance.component,
                    'status': maintenance.status,
                    'description': maintenance.description,
                    'cost': maintenance.cost,
                    'mileage_interval': maintenance.mileage_interval,
                    'last_maintenance_mileage': maintenance.last_maintenance_mileage,
                    'next_maintenance_mileage': maintenance.next_maintenance_mileage,
                    'maintenance_interval': maintenance.maintenance_interval,
                    'created_at': serialize_dt(maintenance.created_at),
                    'updated_at': serialize_dt(maintenance.updated_at)
                }
                maintenance_list.append(maintenance_data)
            
            return {
                'truck_id': truck_id,
                'maintenance_history': maintenance_list,
                'total_maintenances': len(maintenance_list),
                'note': 'Historial de mantenimientos realizados (costo > 0)'
            }, 200
            
        except Exception as e:
            component_ns.abort(500, message='Error listing maintenance history', error=str(e))


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


@component_ns.route('/bulk/status')
class GetBulkComponentsStatus(Resource):
    @component_ns.expect(bulk_components_request_model)
    @component_ns.response(200, 'Estados de componentes obtenidos exitosamente', bulk_components_response_model)
    @component_ns.response(400, 'Datos inválidos')
    @component_ns.response(500, 'Error interno del servidor')
    @jwt_required()
    @role_required(['owner'])
    def post(self):
        """
        Obtener el estado de componentes de múltiples camiones en una sola llamada.
        
        OPTIMIZADO: Una sola query con JOIN para obtener todos los datos necesarios.
        Elimina bucles anidados y operaciones pesadas.
        
        Ejemplo de uso:
        POST /components/bulk/status
        {
            "truck_ids": [1, 2, 3, 4, 5]
        }
        """
        import time
        from collections import defaultdict
        start_time = time.time()
        
        try:
            data = request.get_json()
            if not data or 'truck_ids' not in data:
                component_ns.abort(400, message='truck_ids es requerido')
            
            truck_ids = data['truck_ids']
            if not isinstance(truck_ids, list) or len(truck_ids) == 0:
                component_ns.abort(400, message='truck_ids debe ser una lista no vacía')
            
            # Validar límite
            if len(truck_ids) > 50:
                component_ns.abort(400, message='Máximo 50 camiones por request')
            
            current_user = get_jwt_identity()
            
            # OPTIMIZACIÓN CLAVE: Una sola query con JOIN para obtener solo componentes base (costo = 0)
            query = db.session.query(
                TruckModel.truck_id,
                TruckModel.plate,
                TruckModel.model,
                TruckModel.brand,
                TruckModel.mileage,
                TruckModel.health_status,
                MaintenanceModel.id.label('component_id'),
                MaintenanceModel.component,
                MaintenanceModel.status,
                MaintenanceModel.last_maintenance_mileage,
                MaintenanceModel.next_maintenance_mileage,
                MaintenanceModel.maintenance_interval,
                MaintenanceModel.mileage_interval
            ).join(
                MaintenanceModel, TruckModel.truck_id == MaintenanceModel.truck_id
            ).filter(
                TruckModel.truck_id.in_(truck_ids),
                TruckModel.owner_id == current_user,
                MaintenanceModel.cost == 0  # Solo componentes base (estado actual)
            )
            
            # Ejecutar la query una sola vez
            results = query.all()
            
            # Procesar resultados usando diccionarios para agrupación eficiente
            trucks_data = defaultdict(lambda: {
                'truck_id': None,
                'plate': None,
                'model': None,
                'brand': None,
                'current_mileage': 0,
                'overall_health_status': None,
                'components': {},
                'components_requiring_maintenance': 0
            })
            
            # Procesar resultados y agrupar por truck_id
            for row in results:
                truck_id = row.truck_id
                component_name = row.component
                
                # Si es la primera vez que vemos este camión, guardar datos básicos
                if trucks_data[truck_id]['truck_id'] is None:
                    trucks_data[truck_id].update({
                        'truck_id': truck_id,
                        'plate': row.plate,
                        'model': row.model,
                        'brand': row.brand,
                        'current_mileage': row.mileage,
                        'overall_health_status': row.health_status
                    })
                
                # Solo procesar una vez cada componente (son únicos por truck_id + component + cost=0)
                if component_name not in trucks_data[truck_id]['components']:
                    # Simular update_status() - misma lógica que en MaintenanceModel
                    current_mileage = row.mileage
                    maintenance_interval = row.maintenance_interval
                    last_mileage = row.last_maintenance_mileage
                    
                    # Usar la misma lógica que MaintenanceModel.update_status()
                    if maintenance_interval == 0:
                        calculated_status = 'Excellent'
                        km_remaining = 0
                        health_percentage = 100
                    else:
                        km_since_last = current_mileage - last_mileage
                        degradation_percentage = (km_since_last / maintenance_interval) * 100
                        
                        # Degradación basada únicamente en kilómetros recorridos (como en MaintenanceModel)
                        if degradation_percentage >= 100:
                            calculated_status = 'Maintenance Required'
                            health_percentage = 10  # 20% a 0%
                        elif degradation_percentage >= 80:
                            calculated_status = 'Fair'
                            health_percentage = 30  # 40% a 20%
                        elif degradation_percentage >= 60:
                            calculated_status = 'Good'
                            health_percentage = 50  # 60% a 40%
                        elif degradation_percentage >= 40:
                            calculated_status = 'Very Good'
                            health_percentage = 70  # 80% a 60%
                        elif degradation_percentage >= 20:
                            calculated_status = 'Good'
                            health_percentage = 50  # 60% a 40%
                        else:
                            calculated_status = 'Excellent'
                            health_percentage = 90  # 100% a 80%
                        
                        km_remaining = max(0, maintenance_interval - km_since_last)
                    
                    trucks_data[truck_id]['components'][component_name] = {
                        'component_name': component_name,
                        'current_status': calculated_status,
                        'health_percentage': int(health_percentage),
                        'last_maintenance_mileage': row.last_maintenance_mileage,
                        'next_maintenance_mileage': row.next_maintenance_mileage,
                        'km_remaining': km_remaining,
                        'maintenance_interval': maintenance_interval
                    }
                    
                    # Contar componentes que requieren mantenimiento
                    if calculated_status == 'Maintenance Required':
                        trucks_data[truck_id]['components_requiring_maintenance'] += 1
            
            # Convertir a formato de respuesta
            successful_trucks = []
            failed_truck_ids = set(truck_ids)
            
            for truck_id, data in trucks_data.items():
                if data['truck_id'] is not None:
                    failed_truck_ids.discard(truck_id)
                    
                    truck_response = {
                        'truck_id': data['truck_id'],
                        'plate': data['plate'],
                        'model': data['model'],
                        'brand': data['brand'],
                        'current_mileage': data['current_mileage'],
                        'overall_health_status': data['overall_health_status'],
                        'components': list(data['components'].values()),
                        'total_components': len(data['components']),
                        'components_requiring_maintenance': data['components_requiring_maintenance'],
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    successful_trucks.append(truck_response)
            
            # Crear lista de fallos
            failed_trucks = [
                {
                    'truck_id': truck_id,
                    'error': f'Camión {truck_id} no encontrado o no autorizado'
                }
                for truck_id in failed_truck_ids
            ]
            
            processing_time = (time.time() - start_time) * 1000
            
            response_data = {
                'successful_trucks': successful_trucks,
                'failed_trucks': failed_trucks,
                'total_requested': len(truck_ids),
                'total_successful': len(successful_trucks),
                'total_failed': len(failed_trucks),
                'processing_time_ms': round(processing_time, 2),
                'optimization_note': 'Una sola query con JOIN, solo componentes base (costo=0), usando misma lógica que /list'
            }
            
            return response_data, 200
            
        except Exception as e:
            component_ns.abort(500, message='Error procesando request bulk', error=str(e))
