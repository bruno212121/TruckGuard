from .. import db
from datetime import datetime
from .maintenance import Maintenance
from .drivers import Driver
from .truck import Truck
from .trip import Trip

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
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    maintenace_id = db.Column(db.Integer, db.ForeignKey('maintenance.id'), nullable=False)


    #trips = db.relationship('Trip', back_populates='fleetanalytics', cascade="all, delete-orphan")
    owner = db.relationship('Owner', back_populates='fleetanalytics', uselist=False, single_parent=True)
    maintenance = db.relationship('Maintenance', back_populates='fleetanalytics', uselist=False, single_parent=True)
    trucks = db.relationship('Truck', back_populates='fleetanalytics', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<FleetAnalytics: {self.id} {self.date} {self.total_trips} {self.total_maintenance} {self.total_drivers} {self.total_trucks} {self.created_at} {self.updated_at}>'



    @staticmethod
    def update_fleet_analytics(owner_id):
        fleet_analytics =  FleetAnalytics.query.filter_by(owner_id=owner_id).first()
        if fleet_analytics is None:
            truck = Truck.query.filter_by(owner_id=owner_id).first()
            if truck is None:
                raise ValueError(f"No truck found for owner_id: {owner_id}") 
        
            default_maintenance = Maintenance(description='Default maintenance', 
                                              status='Good', 
                                              component='Default', 
                                              cost=0, 
                                              mileage_interval=0, 
                                              last_maintenance_mileage=0, 
                                              next_maintenance_mileage=0, 
                                              truck_id=truck.truck_id,
                                              driver_id=None, 
                                              maintenance_interval=0)
            db.session.add(default_maintenance)
            db.session.flush()
            
            fleet_analytics = FleetAnalytics(owner_id=owner_id, maintenace_id=default_maintenance.id)
            db.session.add(fleet_analytics)
        
        total_trips = db.session.query(db.func.count(Trip.id)).join(Truck).filter(Truck.owner_id == owner_id).scalar() 
        total_maintenance_cost = db.session.query(db.func.sum(Maintenance.cost)).filter(Maintenance.owner_id == owner_id).scalar() or 0.0
        total_drivers = db.session.query(db.func.count(Driver.id)).filter(Driver.owner_id == owner_id).scalar()
        total_trucks = db.session.query(db.func.count(Truck.truck_id)).filter(Truck.owner_id == owner_id).scalar()

        fleet_analytics.total_trips = total_trips
        fleet_analytics.total_maintenance_cost = total_maintenance_cost
        fleet_analytics.total_drivers = total_drivers
        fleet_analytics.total_trucks = total_trucks

        db.session.add(fleet_analytics)
        db.session.commit()
