import os
from flask import Flask, Blueprint, request
from flask_restx import Api  # (no usado con RESTX desactivado, podés quitarlo si querés)
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_mail import Mail

# Create the SQLAlchemy object
db = SQLAlchemy()
jwt = JWTManager()
mailsender = Mail()

def create_app():
    app = Flask(__name__)
    load_dotenv()

    # Configuración específica para pruebas
    if app.config.get('TESTING') or os.environ.get('TESTING'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    else:
        if not os.path.exists(os.getenv('DATABASE_PATH') + os.getenv('DATABASE_NAME')):  # Check if the database exists
            os.mknod(os.getenv('DATABASE_PATH') + os.getenv('DATABASE_NAME'))

        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable the modification tracker
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.getenv('DATABASE_PATH') + os.getenv('DATABASE_NAME')

    db.init_app(app)

    # --- JWT ---
    secret_key = os.urandom(32)
    app.config['JWT_SECRET_KEY'] = secret_key.hex()
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))
    jwt.init_app(app)

    # --- MAIL ---
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['FLASKY_MAIL_SENDER'] = os.getenv('FLASKY_MAIL_SENDER')
    mailsender.init_app(app)

    # Blueprints clasicos (truck, trip, fleetanalytics, maintenance)
    from app.auth import routes as auth_routes
    app.register_blueprint(auth_routes.auth)

    from app.resources.truck_resources import trucks
    app.register_blueprint(trucks)

    from app.resources.trip_resources import trips
    app.register_blueprint(trips)

    from app.resources.fleetanalytics_resources import fleet
    app.register_blueprint(fleet)

    from app.resources.maintenance_resources import maintenance
    app.register_blueprint(maintenance)

    print("auth.register in view_functions?", 'auth.register' in app.view_functions)
    print("auth.login in view_functions?", 'auth.login' in app.view_functions)

    # --- RESTX DESACTIVADO TEMPORALMENTE PARA AISLAR TESTS DE AUTH ---
    # from flask_restx import Api
    # api_bp = Blueprint('api', __name__)
    # api = Api(api_bp, doc='/docs', title='TruckGuard API')
    # from app.resources.user_resources import User, Users
    # api.add_resource(User, '/user/<int:id>', endpoint='user_detail')
    # api.add_resource(Users, '/users', endpoint='user_list')
    # app.register_blueprint(api_bp)

    # ===== BEFORE_REQUEST: asegurar mapeo de endpoints de auth en caliente =====
    @app.before_request
    def _ensure_auth_endpoints():
        if request.path.startswith('/auth/'):
            # Traemos las funciones reales del blueprint (no crea rutas nuevas)
            try:
                from app.auth.routes import register as reg_fn, login as log_fn
            except Exception:
                reg_fn = log_fn = None

            if reg_fn and 'auth.register' not in app.view_functions:
                app.view_functions['auth.register'] = reg_fn
                print("[ensure] reattached auth.register")

            if log_fn and 'auth.login' not in app.view_functions:
                app.view_functions['auth.login'] = log_fn
                print("[ensure] reattached auth.login")

            print(f"[debug] path={request.path} endpoint={getattr(request, 'endpoint', None)} "
                  f"has_auth.register={'auth.register' in app.view_functions} "
                  f"has_auth.login={'auth.login' in app.view_functions}")

    # Estas asserts validan en setup (crear app). Si te molestan, podés comentarlas.
    assert 'auth.register' in app.view_functions, f"Falta endpoint 'auth.register'."
    assert 'auth.login' in app.view_functions, f"Falta endpoint 'auth.login'."

    return app