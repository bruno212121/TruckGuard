def create_app(config_name=None):
    app = Flask(__name__)
    
    # Configuración básica
    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # Inicializa extensiones
    db.init_app(app)
    
    # Registra blueprints PRIMERO
    from app.resources.truck_resources import trucks as truck_blueprint
    app.register_blueprint(truck_blueprint)
    
    # Luego inicializa Flask-RESTful
    api.init_app(app)
    
    return app