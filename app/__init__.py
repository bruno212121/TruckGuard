import os
from flask import Flask, Blueprint, request, has_request_context
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_mail import Mail

# Create the SQLAlchemy object
db = SQLAlchemy()
jwt = JWTManager()
mailsender = Mail()

# Create the Flask-RESTX API object
from app.config.api_config import api

def create_app():
    app = Flask(__name__)

    load_dotenv()

    # Configuración específica para pruebas
    if app.config.get('TESTING') or os.environ.get('TESTING'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        # Usar clave fija para tests
        app.config['JWT_SECRET_KEY'] = 'testing-secret-key-for-tests-only'
    else:
        if not os.path.exists(os.getenv('DATABASE_PATH') + os.getenv('DATABASE_NAME')):  # Check if the database exists
            os.mknod(os.getenv('DATABASE_PATH') + os.getenv('DATABASE_NAME'))

        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable the modification tracker
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.getenv('DATABASE_PATH') + os.getenv('DATABASE_NAME')
        # Usar clave aleatoria para producción
        secret_key = os.urandom(32)
        app.config['JWT_SECRET_KEY'] = secret_key.hex()

    db.init_app(app)

    # --- JWT ---
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
    # from app.auth import routes as auth_routes  # Comentado - usando Flask-RESTX
    # app.register_blueprint(auth_routes.auth)

    from app.resources.truck_resources import trucks
    app.register_blueprint(trucks)

    from app.resources.trip_resources import trips
    app.register_blueprint(trips)

    from app.resources.fleetanalytics_resources import fleet
    app.register_blueprint(fleet)

    from app.resources.maintenance_resources import maintenance
    app.register_blueprint(maintenance)

    # Configurar Flask-RESTX API
    api.init_app(app)
    
    # Registrar namespaces de autenticación
    from app.auth.restx_routes import auth_ns
    api.add_namespace(auth_ns)

    # ===== BEFORE_REQUEST: asegurar mapeo de endpoints de auth en caliente =====
    # Comentado - usando Flask-RESTX que maneja esto automáticamente
    # @app.before_request
    # def _ensure_auth_endpoints():
    #     if request.path.startswith('/auth/'):
    #         # Traemos las funciones reales del blueprint (no crea rutas nuevas)
    #         try:
    #             from app.auth.routes import register as reg_fn, login as log_fn
    #         except Exception:
    #             reg_fn = log_fn = None

    #         if reg_fn and 'auth.register' not in app.view_functions:
    #             app.view_functions['auth.register'] = reg_fn

    #         if log_fn and 'auth.login' not in app.view_functions:
    #             app.view_functions['auth.login'] = log_fn

    # # Estas asserts validan en setup (crear app). Si te molestan, podés comentarlas.
    # assert 'auth.register' in app.view_functions, f"Falta endpoint 'auth.register'."
    # assert 'auth.login' in app.view_functions, f"Falta endpoint 'auth.login'."

    # ===== BEFORE_REQUEST: asegurar mapeo de endpoints de trucks =====
    @app.before_request
    def _ensure_trucks_endpoints():
    # Este guard evita "Working outside of request context"
        if not has_request_context():
            return

    # si no es una ruta de /trucks, no hacemos nada
        if not request.path.startswith('/trucks/'):
            return

    # Evita UnboundLocalError si falla el import
        _create_truck = _list_trucks = _view_truck = None
        _edit_truck = _delete_truck = _assign_truck = _drivers_wo_truck = None

        try:
            from app.resources.truck_resources import (
                create_truck as _create_truck,
                list_trucks as _list_trucks,
                view_truck as _view_truck,
                edit_truck as _edit_truck,
                delete_truck as _delete_truck,
                assign_truck as _assign_truck,
                get_drivers_without_truck as _drivers_wo_truck,
            )
        except Exception as _e:
            return  # abortamos el reenganche en esta request

    # Reenganche sin crear rutas nuevas
        mapping = {
            'trucks.create_truck': _create_truck,
            'trucks.list_trucks': _list_trucks,
            'trucks.view_truck': _view_truck,
            'trucks.edit_truck': _edit_truck,
            'trucks.delete_truck': _delete_truck,
            'trucks.assign_truck': _assign_truck,
            'trucks.get_drivers_without_truck': _drivers_wo_truck,
        }
        for ep, fn in mapping.items():
            if ep not in app.view_functions and fn is not None:
                app.view_functions[ep] = fn

    return app