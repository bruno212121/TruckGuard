from .. import db 
from datetime import datetime


class Maintenance(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    truck_id = db.Column(db.Integer, db.ForeignKey('truck.truck_id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)


    truck = db.relationship('Truck', back_populates='maintenances', uselist=False, single_parent=True)
    driver = db.relationship('Driver', back_populates='maintenances', uselist=False, single_parent=True)
    fleetanalytics = db.relationship('FleetAnalytics', back_populates='maintenance', cascade='all, delete-orphan')


    def __repr__(self):
        return f'<Maintenance: {self.id} {self.description} {self.status} {self.created_at} {self.updated_at}>'
