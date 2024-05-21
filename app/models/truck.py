from .. import db 
from datetime import datetime


class Truck(db.Model):

    truck_id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False, default='Activo')
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)

    
    owner = db.relationship('Owner', back_populates='trucks', uselist=False, single_parent=True)
    driver = db.relationship('Driver', back_populates='truck', uselist=False, cascade="all, delete-orphan",single_parent=True)
    trip = db.relationship('Trip', back_populates='truck', uselist=False, cascade="all, delete-orphan", single_parent=True)
    maintenances = db.relationship('Maintenance', back_populates='truck', cascade="all,delete-orphan")

    def __repr__(self):
        return f'<Truck: {self.id} {self.plate} {self.model} {self.brand} {self.year} {self.color} {self.status} {self.created_at} {self.updated_at}>'
    
