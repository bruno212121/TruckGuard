from .. import db 
from datetime import datetime



class Truck(db.Model):

    truck_id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False, default='Inactivo')
    mileage = db.Column(db.Integer, nullable=False, default=0) #kilometraje
    health_status = db.Column(db.String(100), nullable=False, default='Good') #estado de salud
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fleetanalytics_id = db.Column(db.Integer, db.ForeignKey('fleet_analytics.id'), nullable=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  

    owner = db.relationship('User', foreign_keys=[owner_id], back_populates='trucks_as_owner', uselist=False, single_parent=True)
    driver = db.relationship('User', foreign_keys=[driver_id], back_populates='trucks_as_driver', uselist=False, cascade="all, delete-orphan", single_parent=True)
    trip = db.relationship('Trip', back_populates='truck', uselist=False, cascade="all, delete-orphan", single_parent=True)
    maintenances = db.relationship('Maintenance', back_populates='truck', cascade="all,delete-orphan")
    fleetanalytics = db.relationship('FleetAnalytics', back_populates='trucks', uselist=False)



    def __init__(self, owner_id, plate, model, brand, year, color, mileage, health_status, fleetanalytics_id, driver_id):
        self.owner_id = owner_id
        self.plate = plate
        self.model = model
        self.brand = brand
        self.year = year
        self.color = color
        self.mileage = mileage
        self.health_status = health_status
        self.fleetanalytics_id = fleetanalytics_id
        self.driver_id = driver_id


    def __repr__(self):
        return f'<Truck: {self.truck_id} {self.plate} {self.model} {self.brand} {self.year} {self.color} {self.status} {self.created_at} {self.updated_at} {self.owner_id} {self.driver_id}>'
    
    

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
            'owner_id': self.owner_id,
            'driver_id': self.driver_id,
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
        driver_id = truck_json.get('driver_id')
        return Truck(truck_id=truck_id, 
                     plate=plate, 
                     model=model, 
                     brand=brand, 
                     year=year, 
                     color=color, 
                     status=status, 
                     created_at=created_at, 
                     updated_at=updated_at, 
                     owner_id=owner_id,
                     driver_id=driver_id)
    

    def update_mileage(self, distance):
        # clamp
        try:
            d = int(distance)
        except:
            d = 0
        if d < 0:
            d = 0

        self.mileage += d

        for m in self.maintenances:
            m.accumulated_km += d
            m.update_status()

        self.update_health_status()
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def update_health_status(self):
        statuses = [maintenance.status for maintenance in self.maintenances]
        if 'Maintenance Required' in statuses:
            self.health_status = 'Maintenance Required'
        elif 'Fair' in statuses:
            self.health_status = 'Fair'
        elif 'Good' in statuses:
            self.health_status = 'Good'
        elif 'Very Good' in statuses:
            self.health_status = 'Very Good'
        else:
            self.health_status = 'Excellent'
        db.session.commit()

    def check_maintenance(self): 
        for maintenance in self.maintenances:
            if self.mileage >= maintenance.next_maintenance_mileage: 
                maintenance.status = 'Pending'
                maintenance.last_maintenance_mileage = self.mileage
                maintenance.next_maintenance_mileage = self.mileage + maintenance.maintenance_interval
                maintenance.update_status()
                db.session.add(maintenance)
                #self.notify_owner()
        self.update_health_status()
        db.session.commit()

    def update_component(self, component_name, status): 
        # Solo actualizar componentes base (costo = 0) que representan el estado actual
        for maintenance in self.maintenances:
            if maintenance.component == component_name and maintenance.cost == 0:
                maintenance.status = status
                # Actualizar también el kilometraje del último mantenimiento
                maintenance.last_maintenance_mileage = self.mileage
                maintenance.next_maintenance_mileage = self.mileage + maintenance.maintenance_interval
                maintenance.accumulated_km = 0
                db.session.add(maintenance)
        self.update_health_status()
        db.session.commit()


    def calculate_remaining_km_until_services(self):
        remaining_km = []
        for maintenance in self.maintenances:
            if maintenance.status == 'Maintenance Required': 
                remaining_km.append(maintenance.next_maintenance_mileage - self.mileage) 
            if remaining_km:
                return min(remaining_km) 
            else:
                return 0
        
    def notify_owner(self):
        #logic for notifying owner
        print(f'Notifying owner of truck {self.truck_id} about maintenance required')
        #logic sending email to owner 