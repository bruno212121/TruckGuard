import os 
from flask import Flask 
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy 
from dotenv import load_dotenv 
from flask_jwt_extended import JWTManager
from flask_mail  import Mail
#importar el nuevo blueprints de truck


# Create the SQLAlchemy object
db = SQLAlchemy()
api = Api()
jwt = JWTManager()
mailsender = Mail()

def create_app():

    app = Flask(__name__)
    load_dotenv()

    secret_key = os.urandom(32)

    if not os.path.exists(os.getenv('DATABASE_PATH') + os.getenv('DATABASE_NAME')): # Check if the database exists
        os.mknod(os.getenv('DATABASE_PATH') + os.getenv('DATABASE_NAME')) 
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable the modification tracker

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.getenv('DATABASE_PATH') + os.getenv('DATABASE_NAME') 
    db.init_app(app)


    import app.resources as resources



    api.add_resource(resources.DriverResource, '/driver/<int:id>')
    api.add_resource(resources.DriversResources, '/drivers')
    api.add_resource(resources.FleetAnalyticsResource, '/fleetanalytics')
    api.add_resource(resources.MaintenanceResource, '/maintenance')
    api.add_resource(resources.OwnerResource, '/owner/<int:id>') #encurso 
    api.add_resource(resources.TripResource, '/trip/<int:id>')
    api.add_resource(resources.TripsResources, '/trips')
    api.add_resource(resources.UserResource, '/user/<int:id>') #realizado
    api.add_resource(resources.UsersResources, '/users') #realizado

    api.init_app(app) 

    app.config['JWT_SECRET_KEY'] = secret_key.hex()
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES')) 
    
    jwt.init_app(app)


    from app.resources.truck_resources import trucks

    app.register_blueprint(trucks)

    from app.auth import routes

    app.register_blueprint(routes.auth)

     #Configuración de mail
    #app.config['MAIL_HOSTNAME'] = os.getenv('MAIL_HOSTNAME')
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['FLASKY_MAIL_SENDER'] = os.getenv('FLASKY_MAIL_SENDER')
    #Inicializar en app
    mailsender.init_app(app)

    return app
    