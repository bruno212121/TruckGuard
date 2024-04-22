from .. import db 


class Truck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False, default='Activo')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)

    
    owner = db.relationship('Owner', back_populates='truck')
    driver = db.relationship('Driver', back_populates='truck')
    trip = db.relationship('Trip', back_populates='truck')