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
        # Construir la ruta de la base de datos correctamente
        db_path = os.getenv('DATABASE_PATH')
        db_name = os.getenv('DATABASE_NAME')
        full_db_path = os.path.join(db_path, db_name)
        
        # Crear el directorio si no existe
        os.makedirs(db_path, exist_ok=True)
        
        # Crear el archivo de base de datos si no existe (compatible con Windows)
        if not os.path.exists(full_db_path):
            try:
                with open(full_db_path, 'w') as f:
                    pass  # Crear archivo vacío
            except Exception as e:
                print(f"Error creando archivo de base de datos: {e}")

        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable the modification tracker
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath(full_db_path)
        
        # Configuración de JWT con clave secreta fija
        jwt_secret_key = os.getenv('JWT_SECRET_KEY')
        if not jwt_secret_key:
            # Si no hay clave en .env, generar una y mostrar advertencia
            import secrets
            jwt_secret_key = secrets.token_hex(32)
            print(f"⚠️  ADVERTENCIA: JWT_SECRET_KEY no configurada en .env. Usando clave generada: {jwt_secret_key}")
            print("   Para producción, configura JWT_SECRET_KEY en tu archivo .env")
        
        app.config['JWT_SECRET_KEY'] = jwt_secret_key

    db.init_app(app)

    # --- JWT ---
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))
    # Configuraciones adicionales de JWT para mayor seguridad
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
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

    # from app.resources.truck_resources import trucks  # Comentado - usando Flask-RESTX
    # app.register_blueprint(trucks)

    # from app.resources.trip_resources import trips
    # app.register_blueprint(trips)

    # from app.resources.fleetanalytics_resources import fleet  # Comentado - usando Flask-RESTX
    # app.register_blueprint(fleet)

    # from app.resources.maintenance_resources import maintenance  # Comentado - usando Flask-RESTX
    # app.register_blueprint(maintenance)

    # Configurar Flask-RESTX API
    api.init_app(app)
    
    # Registrar namespaces de autenticación
    from app.auth.restx_routes import auth_ns
    api.add_namespace(auth_ns)
    
    # Registrar namespaces de trucks
    from app.resources.truck_restx_routes import truck_ns
    api.add_namespace(truck_ns)
    
    # Registrar namespaces de trips
    from app.resources.trip_restx_routes import trip_ns
    api.add_namespace(trip_ns)
    
    # Registrar namespaces de maintenance
    from app.resources.maintenance_restx_routes import maintenance_ns
    api.add_namespace(maintenance_ns)
    
    # Registrar namespaces de fleetanalytics
    from app.resources.fleetanalytics_restx_routes import fleet_ns
    api.add_namespace(fleet_ns)

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