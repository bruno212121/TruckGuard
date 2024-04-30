from .. import db
from datetime import datetime

class FleetAnalytics(db.Model):


    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    total_trips = db.Column(db.Integer, nullable=False)
    total_maintenance = db.Column(db.Integer, nullable=False)
    total_drivers = db.Column(db.Integer, nullable=False)
    total_trucks = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    maintence_id = db.Column(db.Integer, db.ForeignKey('maintenance.id'), nullable=False)


    trip = db.relationship('Trip', back_populates='fleetanalytics')
    owner = db.relationship('Owner', back_populates='fleetanalytics')
    maintenance = db.relationship('Maintenance', back_populates='fleetanalytics')

    def __repr__(self):
        return f'<FleetAnalytics: {self.id} {self.date} {self.total_trips} {self.total_maintenance} {self.total_drivers} {self.total_trucks} {self.created_at} {self.updated_at}>'
