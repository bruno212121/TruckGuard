from flask_restful import Resource
from flask import request, jsonify
from .. import db
from ..models import DriverModel
from flask_jwt_extended import jwt_required

class Driver(Resource):

    @jwt_required
    def get(self, id):
        driver = db.session.query(DriverModel).get_or_404(id)
        return driver.to_json().items()
    

    @jwt_required
    def put(self,id):
        driver = db.session.query(DriverModel).get_or_404(id)
        data = request.get_json().items()
        for key, value in data:
            setattr(score, key, value)
            db.session.add(id)
            db.session.commit()
        return driver.to_json(), 201
    
    @jwt_required
    def delete(self, id):
        driver = db.session.query(DriverModel).get_or_404(id)
        db.session.delete(driver)
        db.session.commit()
        return '', 204
    
    @jwt_required
    def patch(self,id):
        driver = db.session.query(DriverModel).get_or_404(id)
        new_status = request.get_json().get('status')
        if new_status:
            driver.status = new_status
            db.session.add(driver)
            db.session.commit()
            return driver.to_json(), 200
        return {'message': 'No se proporciono un nuevo estado'}, 400

class Drivers(Resource):

    @jwt_required
    def get(self):
        page = 1
        per_page = 10
        drivers = db.session.query(DriverModel)
        if request.get_json():
            filters = request.get_json().items()
            for key, value in filters:
                if key == 'page':
                    page = int(value)
                if key == 'per_page':
                    per_page = value
                if key == 'name':
                    drivers = drivers.filter(DriverModel.name.like(f'%{value}'))

                if key == 'sort_by':
                    if value == 'name':
                        drivers = drivers.order_by(DriverModel.name)
                    if value == 'name desc':
                        drivers = drivers.order_by(DriverModel.name.desc())

        drivers = drivers.paginate(page, per_page, True, 30)
        return jsonify({
            'drivers': [driver.to_json() for driver in drivers.items],
            'total': drivers.total,
            'pages': drivers.pages,
            'page': page
        })


    def post(self):
        driver = DriverModel.from_json(request.get_json())
        db.session.add(driver)
        db.session.commit()
        return driver.to_json(), 201
