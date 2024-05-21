from .. import db
from datetime import datetime

class FleetAnalytics(db.Model):
    

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now())
    total_trips = db.Column(db.Integer)
    total_maintenance = db.Column(db.Integer)
    total_drivers = db.Column(db.Integer)
    total_trucks = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    maintenace_id = db.Column(db.Integer, db.ForeignKey('maintenance.id'), nullable=False)


    #trips = db.relationship('Trip', back_populates='fleetanalytics', cascade="all, delete-orphan")
    owner = db.relationship('Owner', back_populates='fleetanalytics', uselist=False, single_parent=True)
    maintenance = db.relationship('Maintenance', back_populates='fleetanalytics', uselist=False, single_parent=True)


    def __repr__(self):
        return f'<FleetAnalytics: {self.id} {self.date} {self.total_trips} {self.total_maintenance} {self.total_drivers} {self.total_trucks} {self.created_at} {self.updated_at}>'
