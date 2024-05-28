from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token
from .. import db 
from ..models import UserModel, OwnerModel, DriverModel
from ..mail.functions import sendMail
#User' object has no attribute 'validate_password'
#from flask_mail import Message
#importar mailsender desde __init__.py
#from .. import mailsender
#from flask import render_template, current_app

# Define the blueprint: 'auth', set its url prefix: app.url/auth
auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
    
    user = db.session.query(UserModel).filter_by(email=data.get('email')).first()

    if not user:
        return jsonify({'message': 'Email not found'}), 404
    
    if not user.validate_password(data.get('password')):
        return jsonify({'message': 'Incorrect password'}), 401
    
    access_token = create_access_token(identity=user.id)

    response = {   
        'id': user.id,
        'email': user.email,
        'access_token': access_token
    }
    return jsonify(response), 200
    

@auth.route('/register', methods=['POST'])
def register():
    user = UserModel.from_json(request.get_json())

    existing_user = db.session.query(UserModel).filter_by(email=user.email).first()
    if existing_user:
        return jsonify({'message': 'Email already exists'}), 400
    else:
        try:
            db.session.add(user)
            db.session.commit()
            #sent = sendMail([user.email], "Welcome!", 'register', user=user)
        except Exception as error:
            db.session.rollback()
            print("haber que mierda pasa aca che",error)
            return jsonify({'message': 'Error creating user'}), 500
        
        return user.to_json(), 201
