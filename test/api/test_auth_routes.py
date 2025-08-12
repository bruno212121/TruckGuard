"""
Tests para las rutas de autenticación de TruckGuard API

Este módulo contiene tests automatizados para:
- POST /auth/login - Inicio de sesión de usuarios
- POST /auth/register - Registro de nuevos usuarios

Autor: TruckGuard Test Suite
Fecha: 2025
"""

import pytest
import json
from app.models.user import User as UserModel
from app import db


class TestAuthRoutes:
    """Clase que contiene todos los tests para las rutas de autenticación"""
    
    def test_register_success(self, client):
        """
        Test: Registro exitoso de un nuevo usuario
        
        Verifica que:
        - Se puede registrar un usuario con datos válidos
        - Se retorna el código de estado 201
        - Se retorna la información del usuario creado
        """
        user_data = {
            "name": "Juan",
            "surname": "Pérez",
            "rol": "driver",
            "email": "juan.perez@test.com",
            "phone": "123456789",
            "password": "password123"
        }
        
        response = client.post('/auth/register', 
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == user_data['name']
        assert data['email'] == user_data['email']
        assert 'id' in data
        assert 'password' not in data  # La contraseña no debe estar en la respuesta
    
    def test_register_missing_fields(self, client):
        """
        Test: Registro fallido por campos faltantes
        
        Verifica que:
        - Se rechaza el registro si faltan campos obligatorios
        - Se retorna el código de estado 500
        - Se retorna un mensaje de error apropiado
        """
        incomplete_data = {
            "name": "Juan",
            "email": "juan@test.com"
            # Faltan campos obligatorios
        }
        
        response = client.post('/auth/register',
                             data=json.dumps(incomplete_data),
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_register_duplicate_email(self, client):
        """
        Test: Registro fallido por email duplicado
        
        Verifica que:
        - Se rechaza el registro si el email ya existe
        - Se retorna el código de estado 400
        - Se retorna un mensaje de error apropiado
        """
        user_data = {
            "name": "María",
            "surname": "García",
            "rol": "owner",
            "email": "maria.garcia@test.com",
            "phone": "987654321",
            "password": "password123"
        }
        
        # Primer registro (debe ser exitoso)
        response1 = client.post('/auth/register',
                              data=json.dumps(user_data),
                              content_type='application/json')
        assert response1.status_code == 201
        
        # Segundo registro con el mismo email (debe fallar)
        response2 = client.post('/auth/register',
                              data=json.dumps(user_data),
                              content_type='application/json')
        
        assert response2.status_code == 400
        data = json.loads(response2.data)
        assert data['message'] == 'Email already exists'
    
    def test_login_success(self, client):
        """
        Test: Login exitoso
        
        Verifica que:
        - Se puede hacer login con credenciales válidas
        - Se retorna el código de estado 200
        - Se retorna un token de acceso
        - Se retorna la información del usuario
        """
        # Primero crear un usuario
        user_data = {
            "name": "Carlos",
            "surname": "López",
            "rol": "driver",
            "email": "carlos.lopez@test.com",
            "phone": "555123456",
            "password": "password123"
        }
        
        client.post('/auth/register',
                   data=json.dumps(user_data),
                   content_type='application/json')
        
        # Intentar hacer login
        login_data = {
            "email": "carlos.lopez@test.com",
            "password": "password123"
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert data['email'] == login_data['email']
        assert 'id' in data
    
    def test_login_invalid_email(self, client):
        """
        Test: Login fallido con email inexistente
        
        Verifica que:
        - Se rechaza el login con un email que no existe
        - Se retorna el código de estado 404
        - Se retorna un mensaje de error apropiado
        """
        login_data = {
            "email": "usuario.inexistente@test.com",
            "password": "password123"
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['message'] == 'Email not found'
    
    def test_login_invalid_password(self, client):
        """
        Test: Login fallido con contraseña incorrecta
        
        Verifica que:
        - Se rechaza el login con contraseña incorrecta
        - Se retorna el código de estado 401
        - Se retorna un mensaje de error apropiado
        """
        # Primero crear un usuario
        user_data = {
            "name": "Ana",
            "surname": "Martínez",
            "rol": "owner",
            "email": "ana.martinez@test.com",
            "phone": "111222333",
            "password": "password123"
        }
        
        client.post('/auth/register',
                   data=json.dumps(user_data),
                   content_type='application/json')
        
        # Intentar hacer login con contraseña incorrecta
        login_data = {
            "email": "ana.martinez@test.com",
            "password": "password_incorrecta"
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['message'] == 'Incorrect password'
    
    def test_login_missing_fields(self, client):
        """
        Test: Login fallido por campos faltantes
        
        Verifica que:
        - Se rechaza el login si faltan email o password
        - Se retorna el código de estado 400
        - Se retorna un mensaje de error apropiado
        """
        # Test sin email
        login_data_no_email = {
            "password": "password123"
        }
        
        response1 = client.post('/auth/login',
                              data=json.dumps(login_data_no_email),
                              content_type='application/json')
        
        assert response1.status_code == 400
        data1 = json.loads(response1.data)
        assert data1['message'] == 'Missing email or password'
        
        # Test sin password
        login_data_no_password = {
            "email": "test@test.com"
        }
        
        response2 = client.post('/auth/login',
                              data=json.dumps(login_data_no_password),
                              content_type='application/json')
        
        assert response2.status_code == 400
        data2 = json.loads(response2.data)
        assert data2['message'] == 'Missing email or password'
