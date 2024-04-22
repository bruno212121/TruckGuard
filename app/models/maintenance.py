from .. import db 

class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    truck_id = db.Column(db.Integer, db.ForeignKey('truck.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
                                                    

    truck = db.relationship('Truck', back_populates='maintenance')
    driver = db.relationship('Driver', back_populates='maintenance')