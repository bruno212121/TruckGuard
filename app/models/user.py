from .. import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False) #password_hash
    rol = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100))
    status = db.Column(db.String(100), nullable=False, default='active')


    trucks_as_owner = db.relationship('Truck', foreign_keys='Truck.owner_id', primaryjoin='User.id==Truck.owner_id', back_populates='owner')
    trucks_as_driver = db.relationship('Truck', foreign_keys='Truck.driver_id', primaryjoin='User.id==Truck.driver_id', back_populates='driver')
    trips_as_driver = db.relationship('Trip', foreign_keys='Trip.driver_id', primaryjoin='User.id==Trip.driver_id', back_populates='driver')  


    @property
    def plain_password(self):
        raise AttributeError('Password is not a readable attribute')
    
    @plain_password.setter
    def plain_password(self, password):
        self.password = generate_password_hash(password)


    def validate_password(self, password):
        return check_password_hash(self.password, password)


    def __repr__(self):
        return f'<User: {self.id} {self.name} {self.surname} {self.email} {self.rol} {self.phone} {self.status}>'
    


    def to_json(self):
        user_json = {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'rol': self.rol,
            'phone': self.phone,
            'status': self.status,
        }
        return user_json
    
    @staticmethod
    def from_json(user_json):
        id = user_json.get('id')
        name = user_json.get('name')
        surname = user_json.get('surname')
        email = user_json.get('email')
        password = user_json.get('password')
        
        # Normalizar el rol: aceptar tanto 'role' como 'rol', convertir a minúsculas y limpiar espacios
        rol = user_json.get('rol') or user_json.get('role')
        if rol:
            rol = rol.lower().strip()
        
        phone = user_json.get('phone')
        status = user_json.get('status')
        return User(id=id, 
                    name=name, 
                    surname=surname, 
                    email=email, 
                    plain_password=password, 
                    rol=rol, 
                    phone=phone, 
                    status=status,
                    )
