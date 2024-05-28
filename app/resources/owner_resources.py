from flask_restful import Resource
from flask import request, jsonify
from .. import db
from ..models import OwnerModel
from datetime import datetime
from flask_jwt_extended import jwt_required

class Owner(Resource):
    
    @jwt_required
    def get(self, id):
        owner = db.session.query(OwnerModel).get_or_404(id) 
        return owner.to_json()

    @jwt_required 
    def put(self, id):
        owner = db.session.query(OwnerModel).get_or_404(id)
        data = request.get_json().items()
        for key, value in data:
            setattr(owner, key, value) 
        db.session.add(owner)
        db.session.commit()
        return owner.to_json(), 201
    
    @jwt_required
    def patch(self, id):
        owner = db.session.query(OwnerModel).get_or_404(id)
        new_status = request.get_json().get('status')
        if new_status:
            owner.status = new_status
            db.session.add(owner)
            db.session.commit()
            return owner.to_json(), 200
        return {'message': 'No se proporciono un nuevo estado'}, 400
    

class Owners(Resource):

    @jwt_required
    def get(self):
        page = 1
        per_page = 10
        owners = db.session.query(OwnerModel)
        if request.get_json():
            filters = request.get_json().items()
            for key, value in filters:
                if key == 'page':
                    page = int(value)
                if key == 'per_page':
                    per_page = value
                if key == 'name':
                    owners = owners.filter(OwnerModel.name.like(f'%{value}%'))

                if key == 'sort_by':
                    if value == 'name':
                        owners = owners.order_by(OwnerModel.name)
                    if value == 'name desc':
                        owners = owners.order_by(OwnerModel.name.desc())
        
        owners = owners.paginate(page, per_page, True, 30)
        return jsonify({
            'owners': [owner.to_json() for owner in owners.items],
            'total': owners.total,
            'pages': owners.pages,
            'page': page
        })
    
    def post(self):
        owner = OwnerModel.from_json(request.get_json())
        db.session.add(owner)
        db.session.commit()
        return owner.to_json(), 201
