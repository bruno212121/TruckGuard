from .. import db
from datetime import datetime

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100))
    status = db.Column(db.String(100), nullable=False, default='active')    
    created_at = db.Column(db.DateTime, default=datetime.now()) 
    updated_at = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    truck_id = db.Column(db.Integer, db.ForeignKey('truck.truck_id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))

    truck = db.relationship('Truck', back_populates='driver', single_parent=True, cascade="all,delete-orphan")
    maintenances = db.relationship('Maintenance', back_populates='driver', cascade='all, delete-orphan')
    trips = db.relationship('Trip', back_populates='driver', cascade="all, delete-orphan")
    user = db.relationship('User', back_populates='driver', uselist=False, cascade='all, delete-orphan', single_parent=True)
    


    def __repr__(self):
        return f'<Driver: {self.id} {self.name} {self.surname} {self.rol} {self.phone} {self.status} {self.created_at} {self.updated_at}>'
    
    def to_json(self):
        driver_json = {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'rol': self.rol,
            'phone': self.phone,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        return driver_json
    
    @staticmethod
    def from_json(driver_json):
        id = driver_json.get('id')
        name = driver_json.get('name')
        surname = driver_json.get('surname')
        rol = driver_json.get('rol')
        phone = driver_json.get('phone')
        status = driver_json.get('status')
        return Driver(id=id, 
                    name=name, 
                    surname=surname, 
                    rol=rol, 
                    phone=phone, 
                    status=status,
                    )
