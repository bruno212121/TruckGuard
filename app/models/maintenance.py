from .. import db 
from datetime import datetime

class Maintenance(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    component = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Float, nullable=True)
    mileage_interval = db.Column(db.Integer, nullable=False)  # intervalo de kilometraje
    last_maintenance_mileage = db.Column(db.Integer, nullable=False)  # ultimo mantenimiento
    next_maintenance_mileage = db.Column(db.Integer, nullable=False)  # siguiente mantenimiento
    accumulated_km = db.Column(db.Integer, default=0)  # kilometraje acumulado
    maintenance_interval = db.Column(db.Integer, nullable=False)
    
    truck_id = db.Column(db.Integer, db.ForeignKey('truck.truck_id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id', use_alter=True), nullable=True)

    truck = db.relationship('Truck', back_populates='maintenances', uselist=False)
    fleetanalytics = db.relationship('FleetAnalytics', back_populates='maintenance')

    def __init__(self, description, status, component, cost, mileage_interval, last_maintenance_mileage, next_maintenance_mileage, truck_id, driver_id, maintenance_interval):
        self.description = description
        self.status = status
        self.component = component
        self.cost = cost
        self.mileage_interval = mileage_interval
        self.last_maintenance_mileage = last_maintenance_mileage
        self.next_maintenance_mileage = next_maintenance_mileage
        self.truck_id = truck_id
        self.driver_id = driver_id
        self.maintenance_interval = maintenance_interval

    def __repr__(self):
        return f'<Maintenance: {self.id} {self.description} {self.status} {self.created_at} {self.updated_at} {self.component} {self.cost} {self.mileage_interval} {self.last_maintenance_mileage} {self.next_maintenance_mileage} {self.truck_id} {self.driver_id}>'

    def to_json(self):
        return {
            'id': self.id,
            'description': self.description,
            'status': self.status,
            'component': self.component,
            'cost': self.cost,
            'mileage_interval': self.mileage_interval,
            'last_maintenance_mileage': self.last_maintenance_mileage,
            'next_maintenance_mileage': self.next_maintenance_mileage,
            'truck_id': self.truck_id,
            'driver_id': self.driver_id
        }

    @staticmethod
    def from_json(maintenance_json):
        id = maintenance_json.get('id')
        truck_id = maintenance_json.get('truck_id')
        maintenance_interval = maintenance_json.get('maintenance_interval')
        accumulated_km = maintenance_json.get('accumulated_km')
        last_maintenance_mileage = maintenance_json.get('last_maintenance_mileage')
        status = maintenance_json.get('status')

        return Maintenance(id=id, 
                           truck_id=truck_id, 
                           maintenance_interval=maintenance_interval, 
                           accumulated_km=accumulated_km, 
                           last_maintenance_mileage=last_maintenance_mileage,
                           status=status)

    def update_status(self):
        """Actualiza el estado del componente basado en el kilometraje acumulado"""
        if self.maintenance_interval == 0:
            self.status = 'Excellent'
        else:
            # Calcular el kilometraje acumulado desde el último mantenimiento
            if hasattr(self, 'truck') and self.truck:
                current_mileage = self.truck.mileage
                km_since_last = current_mileage - self.last_maintenance_mileage
                percentage_components = (km_since_last / self.maintenance_interval) * 100
            else:
                percentage_components = (self.accumulated_km / self.maintenance_interval) * 100

            # Degradación basada únicamente en kilómetros recorridos
            if percentage_components >= 100:
                self.status = 'Maintenance Required'
            elif percentage_components >= 80:
                self.status = 'Fair'
            elif percentage_components >= 60:
                self.status = 'Good'
            elif percentage_components >= 40:
                self.status = 'Very Good'
            elif percentage_components >= 20:
                self.status = 'Good'
            else:
                self.status = 'Excellent'
           
        db.session.commit()

