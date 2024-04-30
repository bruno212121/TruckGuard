from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token
from .. import db 
from ..models import UserModel

# Define the blueprint: 'auth', set its url prefix: app.url/auth
auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = db.session.query(UserModel).filter_by(email=data.get('email')).first()

    if user and user.validate_password(data.get('password')):
        
        access_token = create_access_token(identity=user.id)

        response = {
            'id': str(user.id),
            'email': user.email,
            'access_token': access_token
        }
        return jsonify(response), 200
    else:
        return jsonify({'message': 'Incorrect email or password'}), 401
    

@auth.route('/register', methods=['POST'])
def register():
    user_data = request.get_json()
    user = UserModel.from_json()
    existing_user = db.session.query(UserModel).filter_by(email=user.email).first()
    if existing_user:
        return jsonify({'message': 'Email already exists'}), 400
    else:
        try:
            db.session.add(user)
            db.session.commit()
        #    sent =  # realizar funcion de mail para enviar mail 
            return jsonify(user.to_json()), 201
        except Exception as e:
            db.session.rollback() 
            return jsonify({'message': 'Error while registering user', 'error': str(e)}), 500
    