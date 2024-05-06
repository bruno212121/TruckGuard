from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token
from .. import db 
from ..models import UserModel
from ..mail.functions import send_email

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
    user = UserModel.from_json(user_data)
    existing_user = db.session.query(UserModel).filter_by(email=user.email).first()
    if existing_user:
        return jsonify({'message': 'Email already exists'}), 400
    else:
        try:
            db.session.add(user)
            db.session.commit()
            success =  send_email(user.email, 'Welcome to the TruckGuard', 'welcome', user=user) 
            if success:
                return jsonify({'message': 'User created successfully'}), 201
            else:
                return jsonify({'message': 'User created successfully but could not send email'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Error creating user', 'error': str(e)}), 500

    