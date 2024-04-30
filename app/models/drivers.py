from .. import db
from datetime import datetime

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(100), nullable=False)
#    license = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False, default='active')    
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False) 
    updated_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    truck_id = db.Column(db.Integer, db.ForeignKey('truck.id'), nullable=False)
    maintenance_id = db.Column(db.Integer, db.ForeignKey('maintenance.id'), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)

    
    user = db.relationship('User', back_populates='driver')
    truck = db.relationship('Truck', back_populates='driver')
    maintenance = db.relationship('Maintenance', back_populates='driver')
    trip = db.relationship('Trip', back_populates='driver')


    def __repr__(self):
        return f'<Driver: {self.id} {self.name} {self.surname} {self.rol} {self.phone} {self.status} {self.created_at} {self.updated_at}>'
    