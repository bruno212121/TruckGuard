"""
Rutas de autenticación usando Flask-RESTX
"""
from flask import request
from flask_restx import Resource
from flask_jwt_extended import create_access_token
from .. import db
from ..models.user import User as UserModel
from .models import auth_ns, login_model, register_model, login_response_model, user_model, error_model


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(200, 'Login exitoso', login_response_model)
    @auth_ns.response(400, 'Datos faltantes', error_model)
    @auth_ns.response(401, 'Contraseña incorrecta', error_model)
    @auth_ns.response(404, 'Email no encontrado', error_model)
    def post(self):
        """Iniciar sesión de usuario"""
        data = request.get_json()

        if not data.get('email') or not data.get('password'):
            auth_ns.abort(400, message='Missing email or password')
        
        user = db.session.query(UserModel).filter_by(email=data.get('email')).first()

        if not user:
            auth_ns.abort(404, message='Email not found')
        
        if not user.validate_password(data.get('password')):
            auth_ns.abort(401, message='Incorrect password')
        
        access_token = create_access_token(identity=user.id)

        response = {   
            'id': user.id,
            'email': user.email,
            'access_token': access_token
        }
        return response, 200


@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    @auth_ns.response(201, 'Usuario creado exitosamente', user_model)
    @auth_ns.response(400, 'Email ya existe', error_model)
    @auth_ns.response(500, 'Error interno del servidor', error_model)
    def post(self):
        """Registrar nuevo usuario. El primer usuario será 'owner', los demás 'driver'"""
        try:
            data = request.get_json()
            
            # Verificar si es el primer usuario registrado
            total_users = db.session.query(UserModel).count()
            
            # Si es el primer usuario, asignar rol 'owner', sino 'driver'
            if total_users == 0:
                data['rol'] = 'owner'
            else:
                data['rol'] = 'driver'
            
            # Normalizar el rol antes de crear el usuario
            if 'role' in data:
                data['role'] = data['role'].lower().strip()
            elif 'rol' in data:
                data['rol'] = data['rol'].lower().strip()
            
            user = UserModel.from_json(data)

            existing_user = db.session.query(UserModel).filter_by(email=user.email).first()
            if existing_user:
                auth_ns.abort(400, message='Email already exists')
            else:
                try:
                    db.session.add(user)
                    db.session.commit()
                    #sent = sendMail([user.email], "Welcome!", 'register', user=user)
                except Exception as error:
                    db.session.rollback()
                    auth_ns.abort(500, message='Error creating user', error=str(error))
                
                return user.to_json(), 201
        except Exception as error:
            auth_ns.abort(500, message='Error creating user', error=str(error))
