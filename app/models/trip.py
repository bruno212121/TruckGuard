from .. import db
from datetime import datetime


class Trip(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    truck_id = db.Column(db.Integer, db.ForeignKey('truck.truck_id'), nullable=False)
    #fleetanalytics_id = db.Column(db.Integer, db.ForeignKey('fleetanalytics.id'))
    
    driver = db.relationship('Driver', back_populates='trips', uselist=False, single_parent=True)
    truck = db.relationship('Truck', back_populates='trip', single_parent=True, cascade="all,delete-orphan")
    #fleetanalytics = db.relationship('FleetAnalytics', back_populates='trips', uselist=False, single_parent=True)

    """
    def __repr__(self):
        return f'<Trip: {self.id} {self.date} {self.origin} {self.destination} {self.status} {self.created_at} {self.updated_at} '
    """

    def __repr__(self):
        trip_json = {
            'id': self.id,
            'date': self.date,
            'origin': self.origin,
            'destination': self.destination,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'driver_id': self.driver_id,
            'truck_id': self.truck_id,
        }
        return trip_json
    
    def to_json(self):
        trip_json = {
            'id': self.id,
            'date': str(self.date.strftime('%Y-%m-%d %H:%M:%S')),
            'origin': self.origin,
            'destination': self.destination,
            'status': self.status,
            'created_at': self.date.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.date.strftime('%Y-%m-%d %H:%M:%S'),
            'driver_id': self.driver_id,
            'truck_id': self.truck_id,
            'fleet_analyticsId': self.fleet_analyticsId
        }
        return trip_json
    
    @staticmethod
    def from_json(trip_json):
        id = trip_json.get('id')
        date = trip_json.get('date')
        origin = trip_json.get('origin')
        destination = trip_json.get('destination')
        status = trip_json.get('status')
        created_at = trip_json.get('created_at')
        updated_at = trip_json.get('updated_at')
        driver_id = trip_json.get('driver_id')
        truck_id = trip_json.get('truck_id')
        fleet_analyticsId = trip_json.get('fleet_analyticsId')
        return Trip(id=id, 
                    date=date, 
                    origin=origin, 
                    destination=destination, 
                    status=status, 
                    created_at=created_at, 
                    updated_at=updated_at, 
                    driver_id=driver_id, 
                    truck_id=truck_id, 
                    fleet_analyticsId=fleet_analyticsId
                    )