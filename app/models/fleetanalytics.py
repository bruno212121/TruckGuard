from .. import db
from datetime import datetime
from .maintenance import Maintenance
from .truck import Truck
from .trip import Trip
from .user import User

class FleetAnalytics(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now())
    total_trips = db.Column(db.Integer, default=0)
    total_maintenance = db.Column(db.Integer, default=0)
    total_drivers = db.Column(db.Integer, default=0)
    total_trucks = db.Column(db.Integer, default=0)
    total_cost = db.Column(db.Float, default=0.0)
    active_trucks = db.Column(db.Integer, default=0)
    available_drivers = db.Column(db.Integer, default=0)
    completed_trips = db.Column(db.Integer, default=0)
    pending_trips = db.Column(db.Integer, default=0)
    pending_maintenance = db.Column(db.Integer, default=0)
    average_cost_per_trip = db.Column(db.Float, default=0.0)
    fleet_health_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    maintenance_id = db.Column(db.Integer, db.ForeignKey('maintenance.id'), nullable=True)

    maintenance = db.relationship('Maintenance', back_populates='fleetanalytics', uselist=False)
    trucks = db.relationship('Truck', back_populates='fleetanalytics')

    def __init__(self, user_id, maintenance_id):
        self.user_id = user_id
        self.maintenance_id = maintenance_id

    def __repr__(self):
        return f'<FleetAnalytics: {self.id} {self.date} {self.total_trips} {self.total_maintenance} {self.total_drivers} {self.total_trucks} {self.created_at} {self.updated_at}>'

    def to_json(self):
        return {
            'id': self.id,
            'date': self.date,
            'total_trips': self.total_trips,
            'total_maintenance': self.total_maintenance,
            'total_drivers': self.total_drivers,
            'total_trucks': self.total_trucks,
            'total_cost': self.total_cost,
            'active_trucks': self.active_trucks,
            'available_drivers': self.available_drivers,
            'completed_trips': self.completed_trips,
            'pending_trips': self.pending_trips,
            'pending_maintenance': self.pending_maintenance,
            'average_cost_per_trip': self.average_cost_per_trip,
            'fleet_health_score': self.fleet_health_score,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'user_id': self.user_id,
            'maintenance_id': self.maintenance_id,
        }

    @staticmethod
    def from_json(fleet_analytics_json):
        return FleetAnalytics(
            user_id=fleet_analytics_json.get('user_id'),
            maintenance_id=fleet_analytics_json.get('maintenance_id')
        )

    @staticmethod
    def get_or_create_for_owner(user_id):
        """Obtener o crear FleetAnalytics para un owner específico"""
        fleet_analytics = FleetAnalytics.query.filter_by(user_id=user_id).first()
        if fleet_analytics is None:
            fleet_analytics = FleetAnalytics(user_id=user_id, maintenance_id=None)
            db.session.add(fleet_analytics)
            db.session.flush()
        return fleet_analytics

    @staticmethod
    def update_fleet_analytics(user_id):
        print(f"Starting update_fleet_analytics for user_id: {user_id}")
        
        fleet_analytics = FleetAnalytics.query.filter_by(user_id=user_id).first()
        if fleet_analytics is None:
            print(f"No existing fleet analytics for user_id: {user_id}, creating new one")
            # Crear fleet analytics sin depender de un camión existente
            fleet_analytics = FleetAnalytics(user_id=user_id, maintenance_id=None)
            db.session.add(fleet_analytics)
            db.session.flush()
        
        try:
            # Calcular totales básicos
            total_trips = db.session.query(db.func.count(Trip.id)).join(Truck).filter(Truck.owner_id == user_id).scalar() or 0
            
            total_maintenance_cost = db.session.query(db.func.sum(Maintenance.cost)).join(Truck).filter(Truck.owner_id == user_id).scalar() or 0.0

            total_drivers = db.session.query(db.func.count(User.id)).join(Truck, User.id == Truck.driver_id).filter(User.rol == 'driver', Truck.owner_id == user_id).scalar() or 0

            total_trucks = db.session.query(db.func.count(Truck.truck_id)).filter(Truck.owner_id == user_id).scalar() or 0

            # Calcular camiones activos (con estado 'Activo' según el modelo Truck)
            active_trucks = db.session.query(db.func.count(Truck.truck_id)).filter(
                Truck.owner_id == user_id,
                Truck.status == 'Activo'
            ).scalar() or 0

            # Calcular conductores disponibles (conductores asignados a camiones activos)
            available_drivers = db.session.query(db.func.count(User.id)).join(Truck, User.id == Truck.driver_id).filter(
                User.rol == 'driver', 
                Truck.owner_id == user_id,
                Truck.status == 'Activo'
            ).scalar() or 0

            # Calcular viajes completados y pendientes
            completed_trips = db.session.query(db.func.count(Trip.id)).join(Truck).filter(
                Truck.owner_id == user_id,
                Trip.status == 'completed'
            ).scalar() or 0

            pending_trips = db.session.query(db.func.count(Trip.id)).join(Truck).filter(
                Truck.owner_id == user_id,
                Trip.status.in_(['pending', 'in_progress'])
            ).scalar() or 0

            # Calcular mantenimientos pendientes (Maintenance Required según el modelo)
            pending_maintenance = db.session.query(db.func.count(Maintenance.id)).join(Truck).filter(
                Truck.owner_id == user_id,
                Maintenance.status == 'Maintenance Required'
            ).scalar() or 0

            # Calcular costo promedio por viaje
            average_cost_per_trip = total_maintenance_cost / total_trips if total_trips > 0 else 0.0

            # Calcular score de salud de la flota (0-100)
            # Basado en: mantenimientos pendientes, estado de camiones, etc.
            health_factors = []
            if total_trucks > 0:
                health_factors.append((active_trucks / total_trucks) * 40)  # 40% peso por camiones activos
            if total_trips > 0:
                health_factors.append((completed_trips / total_trips) * 30)  # 30% peso por viajes completados
            if total_maintenance_cost > 0:
                maintenance_ratio = 1 - (pending_maintenance / (total_maintenance_cost + 1))
                health_factors.append(maintenance_ratio * 30)  # 30% peso por mantenimiento
            
            fleet_health_score = sum(health_factors) if health_factors else 0.0
            fleet_health_score = min(100.0, max(0.0, fleet_health_score))  # Asegurar rango 0-100

            # Actualizar todos los campos
            fleet_analytics.total_trips = total_trips
            fleet_analytics.total_maintenance = total_maintenance_cost
            fleet_analytics.total_drivers = total_drivers
            fleet_analytics.total_trucks = total_trucks
            fleet_analytics.active_trucks = active_trucks
            fleet_analytics.available_drivers = available_drivers
            fleet_analytics.completed_trips = completed_trips
            fleet_analytics.pending_trips = pending_trips
            fleet_analytics.pending_maintenance = pending_maintenance
            fleet_analytics.average_cost_per_trip = average_cost_per_trip
            fleet_analytics.fleet_health_score = fleet_health_score
            fleet_analytics.total_cost = total_maintenance_cost

            db.session.add(fleet_analytics)
            db.session.commit()
            
            print(f"Completed update_fleet_analytics for user_id: {user_id}")

        except Exception as e:
            print(f"Error occurred in update_fleet_analytics: {str(e)}")
            raise

