import pytest
from app import create_app, db
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token
from app.models.user import User as UserModel
import os



@pytest.fixture
def app():
    # Configurar variables de entorno para pruebas
    os.environ['TESTING'] = 'True'
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'testing-secret-key',
    })
    
    # Limpiar endpoints existentes para evitar conflictos
    if hasattr(app, 'view_functions'):
        app.view_functions.clear()
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove() # Limpiar la sesión después de cada prueba
        db.drop_all() # Limpiar la base de datos después de cada prueba

"# Criente de prueba para peticiones http"
@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    with app.app_context():
        # Crear usuario owner
        owner = UserModel(
            id=1,
            name='owner',
            surname='Test',
            rol='owner',
            email='owner@test.com',
            phone='123456789',
            password='test123'
        )
        db.session.add(owner)
        db.session.commit()

        # Crear token usando el email como identidad
        access_token = create_access_token(
            identity=owner.email,
            additional_claims={'rol': 'owner'}
        )
        
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
