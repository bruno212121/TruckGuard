from .. import db


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    truck_id = db.Column(db.Integer, db.ForeignKey('truck.id'), nullable=False)
  
    
    
    driver = db.relationship('Driver', back_populates='trip')
    truck = db.relationship('Truck', back_populates='trip')
