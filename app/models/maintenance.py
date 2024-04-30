from .. import db 
from datetime import datetime

class Maintenance(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    truck_id = db.Column(db.Integer, db.ForeignKey('truck.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
                                                    

    truck = db.relationship('Truck', back_populates='maintenance')
    driver = db.relationship('Driver', back_populates='maintenance')

    def __repr__(self):
        return f'<Maintenance: {self.id} {self.description} {self.status} {self.created_at} {self.updated_at}>'
    
