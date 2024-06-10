from .. import db
from datetime import datetime
from .maintenance import Maintenance
from .truck import Truck
from .trip import Trip
from .user import User

class FleetAnalytics(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now())
    total_trips = db.Column(db.Integer)
    total_maintenance = db.Column(db.Integer)
    total_drivers = db.Column(db.Integer)
    total_trucks = db.Column(db.Integer)
    total_cost = db.Column(db.Float)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    maintenace_id = db.Column(db.Integer, db.ForeignKey('maintenance.id'), nullable=False)

    maintenance = db.relationship('Maintenance', back_populates='fleetanalytics', uselist=False, single_parent=True)
    trucks = db.relationship('Truck', back_populates='fleetanalytics', cascade="all, delete-orphan")

    def __init__(self, user_id, maintenace_id):
        self.user_id = user_id
        self.maintenace_id = maintenace_id

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
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'user_id': self.user_id,
            'maintenace_id': self.maintenace_id,
        }

    @staticmethod
    def from_json(fleet_analytics_json):
        return FleetAnalytics(
            user_id=fleet_analytics_json.get('user_id'),
            maintenace_id=fleet_analytics_json.get('maintenace_id')
        )

    @staticmethod
    def update_fleet_analytics(user_id):
        print(f"Starting update_fleet_analytics for user_id: {user_id}")
        
        fleet_analytics = FleetAnalytics.query.filter_by(user_id=user_id).first()
        if fleet_analytics is None:
            print(f"No existing fleet analytics for user_id: {user_id}, creating new one")
            truck = Truck.query.filter_by(owner_id=user_id).first()
            if truck is None:
                raise ValueError(f"No truck found for user_id: {user_id}")

            default_maintenance = Maintenance(
                description='Default maintenance', 
                status='Good', 
                component='Default', 
                cost=0, 
                mileage_interval=0, 
                last_maintenance_mileage=0, 
                next_maintenance_mileage=0, 
                truck_id=truck.truck_id,
                driver_id=user_id,
                maintenance_interval=0
            )
            db.session.add(default_maintenance)
            db.session.flush()
            
            fleet_analytics = FleetAnalytics(user_id=user_id, maintenace_id=default_maintenance.id)
            db.session.add(fleet_analytics)
        
        try:
            total_trips = db.session.query(db.func.count(Trip.id)).join(Truck).filter(Truck.owner_id == user_id).scalar()
            print(f"Total trips for user_id {user_id}: {total_trips}")

            total_maintenance_cost = db.session.query(db.func.sum(Maintenance.cost)).join(Truck).filter(Truck.owner_id == user_id).scalar() or 0.0
            print(f"Total maintenance cost for user_id {user_id}: {total_maintenance_cost}")

            total_drivers = db.session.query(db.func.count(User.id)).join(Truck, User.id == Truck.driver_id).filter(User.rol == 'driver', Truck.owner_id == user_id).scalar()
            print(f"Total drivers for user_id {user_id}: {total_drivers}")

            total_trucks = db.session.query(db.func.count(Truck.truck_id)).filter(Truck.owner_id == user_id).scalar()
            print(f"Total trucks for user_id {user_id}: {total_trucks}")

            print(f"Updating fleet analytics for user_id: {user_id}")
            fleet_analytics.total_trips = total_trips
            fleet_analytics.total_maintenance = total_maintenance_cost
            fleet_analytics.total_drivers = total_drivers
            fleet_analytics.total_trucks = total_trucks

            db.session.add(fleet_analytics)
            db.session.commit()
            print(f"Completed update_fleet_analytics for user_id: {user_id}")

        except Exception as e:
            print(f"Error occurred in update_fleet_analytics: {str(e)}")
            raise

