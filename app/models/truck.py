from .. import db 
from datetime import datetime

#falta driver_id para asignarlo 

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
        return f'<Truck: {self.truck_id} {self.plate} {self.model} {self.brand} {self.year} {self.color} {self.status} {self.created_at} {self.updated_at}>'
    

    def to_json(self):
        return {
            'truck_id': self.truck_id,
            'plate': self.plate,
            'model': self.model,
            'brand': self.brand,
            'year': self.year,
            'color': self.color,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'owner_id': self.owner_id
        }
    
    @staticmethod
    def from_json(truck_json):
        truck_id = truck_json.get('truck_id')
        plate = truck_json.get('plate')
        model = truck_json.get('model')
        brand = truck_json.get('brand')
        year = truck_json.get('year')
        color = truck_json.get('color')
        status = truck_json.get('status')
        created_at = truck_json.get('created_at')
        updated_at = truck_json.get('updated_at')
        owner_id = truck_json.get('owner_id')
        return Truck(truck_id=truck_id, 
                     plate=plate, 
                     model=model, 
                     brand=brand, 
                     year=year, 
                     color=color, 
                     status=status, 
                     created_at=created_at, 
                     updated_at=updated_at, 
                     owner_id=owner_id)