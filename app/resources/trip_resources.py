from flask_restful import Resource
from flask import request, jsonify
from .. import db
from ..models import TripModel
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


class Trip(Resource):

    @jwt_required
    def get(selfi, id):
        trip = db.session.query(TripModel).get_or_404(id)
        return trip.to_json()
    
    #realizar decadador, si el usuario es owner o driver
    def put(self, id):
        pass


    #realizar decadador, si el usuario es owner o driver
    def patch(self, id):
        pass




class Trips(Resource):

    #realizar decorador para acceso owner
    def get(self):
        page = 1
        per_page = 10
        trips = db.session.query(TripModel)
        if request.get_json():
            filters = request.get_json().items()
            for key, value in filters:
                if key == 'page':
                    page = int(value)
                if key == 'per_page':
                    per_page = value
                if key == 'status':
                    trips = trips.filter(TripModel.status == value)
                if key == 'origin':
                    trips = trips.filter(TripModel.origin == value)
                if key == 'destination':
                    trips = trips.filter(TripModel.destination == value)
                if key == 'date':
                    trips = trips.filter(TripModel.date == value)
                if key == 'driver_id':
                    trips = trips.filter(TripModel.driver_id == value)
                if key == 'truck_id':
                    trips = trips.filter(TripModel.truck_id == value)

                if key == 'sort_by':
                    if value == 'date':
                        trips = trips.order_by(TripModel.date)
                    if value == 'date desc':
                        trips = trips.order_by(TripModel.date.desc())
                    if value == 'status':
                        trips = trips.order_by(TripModel.status)
                    if value == 'status desc':
                        trips = trips.order_by(TripModel.status.desc())
                    if value == 'origin':
                        trips = trips.order_by(TripModel.origin)
                    if value == 'origin desc':
                        trips = trips.order_by(TripModel.origin.desc())
                    if value == 'destination':
                        trips = trips.order_by(TripModel.destination)
                    if value == 'destination desc':
                        trips = trips.order_by(TripModel.destination.desc())
                    if value == 'driver_id':
                        trips = trips.order_by(TripModel.driver_id)
                    if value == 'driver_id desc':
                        trips = trips.order_by(TripModel.driver_id.desc())
                    if value == 'truck_id':
                        trips = trips.order_by(TripModel.truck_id)
                    if value == 'truck_id desc':
                        trips = trips.order_by(TripModel.truck_id.desc())
        
        trips = trips.paginate(page, per_page, True, 30)
        return jsonify({
            'trips': [trip.to_json() for trip in trips.items],
            'total': trips.total,
            'pages': trips.pages,
        })
    
    #realizar decorador para acceso owner y driver
    def post(self):
        pass
    