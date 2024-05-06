import os 
from flask import Flask 
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy 
from dotenv import load_dotenv 
from flask_jwt_extended import JWTManager
from flask_mail  import Mail

# Create the SQLAlchemy object
db = SQLAlchemy()
api = Api()
jwt = JWTManager()
mailsender = Mail()

def create_app():

    app = Flask(__name__)
    load_dotenv()


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
    api.add_resource(resources.OwnerResource, '/owner/<int:id>')
    api.add_resource(resources.TripResource, '/trip/<int:id>')
    api.add_resource(resources.TripsResources, '/trips')
    api.add_resource(resources.TruckResource, '/truck/<int:id>')
    api.add_resource(resources.TrucksResources, '/trucks')
    api.add_resource(resources.UserResource, '/user/<int:id>')
    api.add_resource(resources.UsersResources, '/users')

    api.init_app(app) 

    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES')) 
    
    jwt.init_app(app)


    from app.auth import routes

    app.register_blueprint(routes.auth)

    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL')

    mailsender.init_app(app)

    return app
    