from .. import db
from datetime import datetime

class Owner(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100))
    status = db.Column(db.String(100), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
 
  
    
    trucks = db.relationship('Truck', back_populates='owner', cascade="all, delete-orphan") 
    fleetanalytics = db.relationship('FleetAnalytics', back_populates='owner', cascade="all, delete-orphan")
    user = db.relationship('User', back_populates='owner')

    def __repr__(self):
        return f'<Owner: {self.id} {self.name} {self.surname} {self.rol} {self.phone} {self.status} {self.created_at} {self.updated_at}>'


    def to_json(self):
        owner_json = {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'rol': self.rol,
            'phone': self.phone,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'user_id': self.user_id,
        }
        return owner_json
    
    @staticmethod
    def from_json(owner_json):
        id = owner_json.get('id')
        name = owner_json.get('name')
        surname = owner_json.get('surname')
        rol = owner_json.get('rol')
        phone = owner_json.get('phone')
        status = owner_json.get('status')
        user_id = owner_json.get('user_id')
        return Owner(id=id, name=name, surname=surname, rol=rol, phone=phone, status=status, user_id=user_id)
