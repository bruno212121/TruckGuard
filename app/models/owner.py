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
    user = db.relationship('User', back_populates='owner', uselist=False, cascade='all, delete-orphan', single_parent=True)

    def __repr__(self):
        return f'<Owner: {self.id} {self.name} {self.surname} {self.rol} {self.phone} {self.status} {self.created_at} {self.updated_at}>'
