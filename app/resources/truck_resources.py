from flask_restful import Resource
from flask import request, jsonify
from .. import db
from ..models import TruckModel, OwnerModel
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..utils.decorators import owner_required, driver_required


class Truck(Resource):


    @jwt_required
    @owner_required
    def get(self, id):
        truck = db.session.query(TruckModel).get_or_404(id)
        return truck.to_json(), 200

    @jwt_required
    @driver_required
    def get_driver_truck(self, id):
        truck = db.session.query(TruckModel).get_or_404(id)
        driver_id = get_jwt_identity()
        if truck.driver_id == driver_id:
            return truck.to_json(), 200
        return {'message': 'You do not have permission to view this truck'}, 403

    @jwt_required
    @owner_required
    def put(self, id):
        truck = db.session.query(TruckModel).get_or_404(id)
        data = request.get_json()
        owner = db.session.query(OwnerModel).filter_by(user_id=get_jwt_identity()).first()
        if owner:
            for key, value in data.items():
                setattr(truck, key, value)
            db.session.add(truck)
            db.session.commit()
            return truck.to_json(), 200
        return {'message': 'You do not have permission to modify this truck'}, 403

    @jwt_required
    @driver_required
    def put_driver_truck(self, id):
        truck = db.session.query(TruckModel).get_or_404(id)
        data = request.get_json()
        user_id = get_jwt_identity()
        if truck.driver_id == user_id:
            for key, value in data.items():
                setattr(truck, key, value)
            db.session.add(truck)
            db.session.commit()
            return truck.to_json(), 200
        return {'message': 'You do not have permission to modify this truck'}, 403

    @jwt_required
    @owner_required
    def patch(self, id):
        truck = db.session.query(TruckModel).get_or_404(id)
        new_status = request.get_json().get('status')
        owner = db.session.query(OwnerModel).filter_by(user_id=get_jwt_identity).first()
        if owner:
            if new_status:
                truck.status = new_status
                db.session.add(truck)
                db.session.commit()
                return truck.to_json(), 200
            return {'message': 'status is required'}, 400
        return {'message': 'You do not have permission to modify this truck'}, 403


class Trucks(Resource):

    @jwt_required
    @owner_required
    def get(self):
        page = 1
        per_page = 10
        trucks = db.session.query(TruckModel)
        if request.get_json():
            filters = request.get_json().items()
            for key, value in filters:
                if key == 'page':
                    page = int(value)
                if key == 'per_page':
                    per_page = value
                if key == 'plate':
                    trucks = trucks.filter(TruckModel.plate.like(f'%{value}%'))
                if key == 'model':
                    trucks = trucks.filter(TruckModel.model.like(f'%{value}%'))
                if key == 'brand':
                    trucks = trucks.filter(TruckModel.brand.like(f'%{value}%'))
                if key == 'year':
                    trucks = trucks.filter(TruckModel.year.like(f'%{value}%'))
                if key == 'color':
                    trucks = trucks.filter(TruckModel.color.like(f'%{value}%'))
                if key == 'status':
                    trucks = trucks.filter(TruckModel.status.like(f'%{value}%'))

                if key == 'sort_by':
                    if value == 'plate':
                        trucks = trucks.order_by(TruckModel.plate)
                    if value == 'plate desc':
                        trucks = trucks.order_by(TruckModel.plate.desc())
                    if value == 'model':
                        trucks = trucks.order_by(TruckModel.model)
                    if value == 'model desc':
                        trucks = trucks.order_by(TruckModel.model.desc())
                    if value == 'brand':
                        trucks = trucks.order_by(TruckModel.brand)
                    if value == 'brand desc':
                        trucks = trucks.order_by(TruckModel.brand.desc())
                    if value == 'year':
                        trucks = trucks.order_by(TruckModel.year)
                    if value == 'year desc':
                        trucks = trucks.order_by(TruckModel.year.desc())
                    if value == 'color':
                        trucks = trucks.order_by(TruckModel.color)
                    if value == 'color desc':
                        trucks = trucks.order_by(TruckModel.color.desc())
                    if value == 'status':
                        trucks = trucks.order_by(TruckModel.status)
                    if value == 'status desc':
                        trucks = trucks.order_by(TruckModel.status.desc())
        
        trucks = trucks.paginate(page, per_page, True, 30)
        return jsonify({
            'trucks': [truck.to_json() for truck in trucks.items],
            'total': trucks.total,
            'pages': trucks.pages,
            'page': page
        })

    @jwt_required
    @owner_required
    def post(self):
        data = request.get_json()
        owner = db.session.query(OwnerModel).filter_by(user_id=get_jwt_identity()).first()
        if owner:
            truck = TruckModel.from_json(data)
            db.session.add(truck)
            db.session.commit()
            return truck.to_json(), 201
        return {'message': 'You do not have permission to create a truck'}, 403
    