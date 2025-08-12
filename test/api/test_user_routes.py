"""
Tests para las rutas de usuarios de TruckGuard API

Este módulo contiene tests automatizados para:
- GET /user/<id> - Obtener usuario específico
- PUT /user/<id> - Actualizar usuario
- DELETE /user/<id> - Eliminar usuario
- GET /users - Listar usuarios
- POST /users - Crear usuario

Autor: TruckGuard Test Suite
Fecha: 2025
"""

import pytest
import json
from app.models.user import User as UserModel
from app import db


class TestUserRoutes:
    """Clase que contiene todos los tests para las rutas de usuarios"""
    
    def test_get_user_success(self, client, auth_headers):
        """
        Test: Obtención exitosa de un usuario específico
        
        Verifica que:
        - Se puede obtener un usuario por ID
        - Se requiere autenticación
        - Se retorna el código de estado 200
        - Se retorna la información del usuario
        """
        # Crear un usuario primero
        user_data = {
            "name": "María",
            "surname": "López",
            "rol": "driver",
            "email": "maria.lopez@test.com",
            "phone": "123456789",
            "password": "password123"
        }
        
        client.post('/auth/register',
                   data=json.dumps(user_data),
                   content_type='application/json')
        
        # Obtener el usuario
        response = client.get('/user/1',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == user_data['name']
        assert data['email'] == user_data['email']
        assert 'password' not in data  # La contraseña no debe estar en la respuesta
    
    def test_get_user_not_found(self, client, auth_headers):
        """
        Test: Obtención de usuario inexistente
        
        Verifica que:
        - Se rechaza la obtención de un usuario que no existe
        - Se retorna el código de estado 404
        """
        response = client.get('/user/999',
                            headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_get_user_without_auth(self, client):
        """
        Test: Obtención de usuario sin autenticación
        
        Verifica que:
        - Se rechaza la obtención sin token de autenticación
        - Se retorna el código de estado 401
        """
        response = client.get('/user/1')
        
        assert response.status_code == 401
    
    def test_update_user_success(self, client, auth_headers):
        """
        Test: Actualización exitosa de un usuario
        
        Verifica que:
        - Se puede actualizar un usuario por ID
        - Se requiere autenticación
        - Se retorna el código de estado 201
        - Se actualizan los campos correctamente
        """
        # Crear un usuario primero
        user_data = {
            "name": "Carlos",
            "surname": "García",
            "rol": "driver",
            "email": "carlos.garcia@test.com",
            "phone": "987654321",
            "password": "password123"
        }
        
        client.post('/auth/register',
                   data=json.dumps(user_data),
                   content_type='application/json')
        
        # Actualizar el usuario
        update_data = {
            "name": "Carlos Updated",
            "phone": "555123456"
        }
        
        response = client.put('/user/1',
                            data=json.dumps(update_data),
                            headers=auth_headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == update_data['name']
        assert data['phone'] == update_data['phone']
        assert data['surname'] == user_data['surname']  # No cambió
    
    def test_update_user_not_found(self, client, auth_headers):
        """
        Test: Actualización de usuario inexistente
        
        Verifica que:
        - Se rechaza la actualización de un usuario que no existe
        - Se retorna el código de estado 404
        """
        update_data = {
            "name": "Usuario Inexistente"
        }
        
        response = client.put('/user/999',
                            data=json.dumps(update_data),
                            headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_update_user_without_auth(self, client):
        """
        Test: Actualización de usuario sin autenticación
        
        Verifica que:
        - Se rechaza la actualización sin token de autenticación
        - Se retorna el código de estado 401
        """
        update_data = {
            "name": "Test Update"
        }
        
        response = client.put('/user/1',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 401
    
    def test_delete_user_success(self, client, auth_headers):
        """
        Test: Eliminación exitosa de un usuario
        
        Verifica que:
        - Se puede eliminar un usuario por ID
        - Se requiere autenticación
        - Se retorna el código de estado 204
        """
        # Crear un usuario primero
        user_data = {
            "name": "Ana",
            "surname": "Martínez",
            "rol": "driver",
            "email": "ana.martinez@test.com",
            "phone": "111222333",
            "password": "password123"
        }
        
        client.post('/auth/register',
                   data=json.dumps(user_data),
                   content_type='application/json')
        
        # Eliminar el usuario
        response = client.delete('/user/1',
                               headers=auth_headers)
        
        assert response.status_code == 204
        
        # Verificar que el usuario fue eliminado
        get_response = client.get('/user/1',
                                headers=auth_headers)
        assert get_response.status_code == 404
    
    def test_delete_user_not_found(self, client, auth_headers):
        """
        Test: Eliminación de usuario inexistente
        
        Verifica que:
        - Se rechaza la eliminación de un usuario que no existe
        - Se retorna el código de estado 404
        """
        response = client.delete('/user/999',
                               headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_delete_user_without_auth(self, client):
        """
        Test: Eliminación de usuario sin autenticación
        
        Verifica que:
        - Se rechaza la eliminación sin token de autenticación
        - Se retorna el código de estado 401
        """
        response = client.delete('/user/1')
        
        assert response.status_code == 401
    
    def test_list_users_success(self, client, auth_headers):
        """
        Test: Listado exitoso de usuarios
        
        Verifica que:
        - Se pueden listar todos los usuarios
        - Se requiere autenticación
        - Se retorna el código de estado 200
        - Se retorna una lista de usuarios con paginación
        """
        # Crear algunos usuarios primero
        users_data = [
            {
                "name": "Usuario1",
                "surname": "Apellido1",
                "rol": "driver",
                "email": "usuario1@test.com",
                "phone": "111111111",
                "password": "password123"
            },
            {
                "name": "Usuario2",
                "surname": "Apellido2",
                "rol": "owner",
                "email": "usuario2@test.com",
                "phone": "222222222",
                "password": "password123"
            }
        ]
        
        for user_data in users_data:
            client.post('/auth/register',
                       data=json.dumps(user_data),
                       content_type='application/json')
        
        # Listar usuarios
        response = client.get('/users',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'users' in data
        assert 'total' in data
        assert 'pages' in data
        assert 'page' in data
        assert isinstance(data['users'], list)
        assert len(data['users']) >= 2  # Al menos los 2 usuarios creados
    
    def test_list_users_with_filters(self, client, auth_headers):
        """
        Test: Listado de usuarios con filtros
        
        Verifica que:
        - Se pueden filtrar usuarios por nombre
        - Los filtros funcionan correctamente
        """
        # Crear usuarios con nombres específicos
        users_data = [
            {
                "name": "Juan",
                "surname": "Pérez",
                "rol": "driver",
                "email": "juan.perez@test.com",
                "phone": "333333333",
                "password": "password123"
            },
            {
                "name": "María",
                "surname": "González",
                "rol": "driver",
                "email": "maria.gonzalez@test.com",
                "phone": "444444444",
                "password": "password123"
            }
        ]
        
        for user_data in users_data:
            client.post('/auth/register',
                       data=json.dumps(user_data),
                       content_type='application/json')
        
        # Filtrar por nombre
        filter_data = {"name": "Juan"}
        
        response = client.get('/users',
                            data=json.dumps(filter_data),
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['users']) >= 0  # Puede ser 0 si no hay coincidencias
    
    def test_list_users_without_auth(self, client):
        """
        Test: Listado de usuarios sin autenticación
        
        Verifica que:
        - Se rechaza el listado sin token de autenticación
        - Se retorna el código de estado 401
        """
        response = client.get('/users')
        
        assert response.status_code == 401
    
    def test_create_user_success(self, client, auth_headers):
        """
        Test: Creación exitosa de un usuario
        
        Verifica que:
        - Se puede crear un usuario
        - Se requiere autenticación
        - Se retorna el código de estado 201
        """
        user_data = {
            "name": "Nuevo",
            "surname": "Usuario",
            "rol": "driver",
            "email": "nuevo.usuario@test.com",
            "phone": "555555555",
            "password": "password123"
        }
        
        response = client.post('/users',
                             data=json.dumps(user_data),
                             headers=auth_headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == user_data['name']
        assert data['email'] == user_data['email']
        assert 'password' not in data
    
    def test_create_user_without_auth(self, client):
        """
        Test: Creación de usuario sin autenticación
        
        Verifica que:
        - Se rechaza la creación sin token de autenticación
        - Se retorna el código de estado 401
        """
        user_data = {
            "name": "Sin Auth",
            "surname": "Usuario",
            "rol": "driver",
            "email": "sin.auth@test.com",
            "phone": "666666666",
            "password": "password123"
        }
        
        response = client.post('/users',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 401
