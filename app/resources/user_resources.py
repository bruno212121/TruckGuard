from flask_restful import Resource 
from flask import request, jsonify
from .. import db
from ..models import UserModel
from flask_jwt_extended import jwt_required, get_jwt_identity



class User(Resource):
    

    @jwt_required()
    def get(self, id):
        user = db.session.query(UserModel).get_or_404(id) 
        return user.to_json()
    

    @jwt_required()
    def put(self, id):
        user = db.session.query(UserModel).get_or_404(id)
        data = request.get_json().items()
        for key, value in data:
            setattr(user, key, value) 
            db.session.add(user)
            db.session.commit()
        return user.to_json(), 201

    @jwt_required()
    def delete(self, id):
        user = db.session.query(UserModel).get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return '', 204


class Users(Resource):

    @jwt_required()
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        
        # Calcular el índice de inicio y fin para la selección de la página
        start = (page - 1) * per_page
        end = start + per_page
        
        # Realizar la consulta filtrada
        users_query = UserModel.query
        
        if request.get_json():
            filters = request.get_json().items()
            for key, value in filters:
                if key == 'name':
                    users_query = users_query.filter(UserModel.name.like(f'%{value}%'))
        
        # Seleccionar solo los usuarios correspondientes a la página actual
        users = users_query.slice(start, end).all()
        
        # Contar el total de usuarios (sin aplicar paginación)
        total_users = users_query.count()
        
        # Calcular el número total de páginas
        total_pages = (total_users - 1) // per_page + 1
        
        return jsonify({
            'users': [user.to_json() for user in users],
            'total': total_users,
            'pages': total_pages,
            'page': page
        })     
        
    

    def post(self):
        users = UserModel.from_json(request.get_json())
        db.session.add(users)
        db.session.commit()
        return users.to_json(), 201
    