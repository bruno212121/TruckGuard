"""
Tests para las rutas de camiones de TruckGuard API

Este módulo contiene tests automatizados para:
- POST /trucks/new - Crear nuevo camión
- GET /trucks/all - Listar todos los camiones
- GET /trucks/<id> - Ver camión específico

Autor: TruckGuard Test Suite
Fecha: 2025
"""

import pytest
import json
from app.models.user import User as UserModel
from app.models.truck import Truck as TruckModel
from app import db


class TestTruckRoutes:
    """Clase que contiene todos los tests para las rutas de camiones"""
    
    def test_create_truck_success(self, client, auth_headers):
        """
        Test: Creación exitosa de un camión
        
        Verifica que:
        - Se puede crear un camión con datos válidos
        - Se requiere autenticación y rol de owner
        - Se retorna el código de estado 201
        """
        # Primero crear un driver
        driver_data = {
            "name": "Pedro",
            "surname": "González",
            "rol": "driver",
            "email": "pedro.gonzalez@test.com",
            "phone": "123456789",
            "password": "password123"
        }
        
        driver_response = client.post('/auth/register',
               data=json.dumps(driver_data),
               content_type='application/json')
        
        # Verificar que el driver se creó correctamente
        assert driver_response.status_code == 201
        
        # Obtener el ID del driver creado
        driver_info = json.loads(driver_response.data)
        driver_id = driver_info['id']
        
        # Crear el camión con todos los campos requeridos
        truck_data = {
            "truck_id": "TRK001",
            "plate": "ABC123",
            "model": "Volvo FH16",
            "brand": "Volvo",
            "year": 2020,
            "mileage": 50000,
            "color": "Blanco",
            "health_status": "Good",
            "fleetanalytics_id": None,
            "driver_id": driver_id
        }
        
        response = client.post('/trucks/new',
                             data=json.dumps(truck_data),
                             headers=auth_headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Truck created'
        assert 'truck' in data
    
    def test_create_truck_without_auth(self, client):
        """
        Test: Creación de camión sin autenticación
        
        Verifica que:
        - Se rechaza la creación sin token de autenticación
        - Se retorna el código de estado 401
        """
        truck_data = {
            "truck_id": "TRK002",
            "plate": "XYZ789",
            "model": "Scania R500",
            "brand": "Scania",
            "year": 2021,
            "mileage": 30000,
            "color": "Azul",
            "driver_id": 1
        }
        
        response = client.post('/trucks/new',
                             data=json.dumps(truck_data),
                             content_type='application/json')
        
        assert response.status_code == 401
    
    def test_create_truck_invalid_driver(self, client, auth_headers):
        """
        Test: Creación de camión con driver inválido
        
        Verifica que:
        - Se rechaza la creación si el driver_id no existe
        - Se retorna el código de estado 400
        - Se retorna un mensaje de error apropiado
        """
        truck_data = {
            "truck_id": "TRK003",
            "plate": "DEF456",
            "model": "Mercedes Actros",
            "brand": "Mercedes",
            "year": 2019,
            "mileage": 75000,
            "color": "Negro",
            "health_status": "Good",  # Agregar campo requerido
            "fleetanalytics_id": None,  # Agregar campo requerido
            "driver_id": 999  # Driver inexistente (usar un ID alto)
        }
        
        response = client.post('/trucks/new',
                             data=json.dumps(truck_data),
                             headers=auth_headers)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid driver id' in data['message']
    
    def test_list_trucks_success(self, client, auth_headers):
        """
        Test: Listado exitoso de camiones
        
        Verifica que:
        - Se pueden listar todos los camiones
        - Se requiere autenticación y rol de owner
        - Se retorna el código de estado 200
        - Se retorna una lista de camiones
        """
        response = client.get('/trucks/all',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'trucks' in data
        assert isinstance(data['trucks'], list)
    
    def test_list_trucks_without_auth(self, client):
        """
        Test: Listado de camiones sin autenticación
        
        Verifica que:
        - Se rechaza el listado sin token de autenticación
        - Se retorna el código de estado 401
        """
        response = client.get('/trucks/all')
        
        assert response.status_code == 401
    
    def test_view_truck_success(self, client, auth_headers):
        """
        Test: Visualización exitosa de un camión específico
        
        Verifica que:
        - Se puede ver un camión específico por ID
        - Se requiere autenticación y rol de owner
        - Se retorna el código de estado 200
        - Se retorna la información del camión
        """
        # Primero crear un driver
        driver_data = {
            "name": "Luis",
            "surname": "Hernández",
            "rol": "driver",
            "email": "luis.hernandez@test.com",
            "phone": "987654321",
            "password": "password123"
        }
        
        driver_response = client.post('/auth/register',
               data=json.dumps(driver_data),
               content_type='application/json')
        
        # Verificar que el driver se creó correctamente
        assert driver_response.status_code == 201
        
        # Obtener el ID del driver creado
        driver_info = json.loads(driver_response.data)
        driver_id = driver_info['id']
        
        truck_data = {
            "truck_id": "TRK004",
            "plate": "GHI789",
            "model": "Iveco Stralis",
            "brand": "Iveco",
            "year": 2018,
            "mileage": 100000,
            "color": "Rojo",
            "health_status": "Good",  # Agregar campo requerido
            "fleetanalytics_id": None,  # Agregar campo requerido
            "driver_id": driver_id  # Usar el ID correcto del driver
        }
        
        create_response = client.post('/trucks/new',
                   data=json.dumps(truck_data),
                   headers=auth_headers)
        
        # Verificar que el camión se creó correctamente
        assert create_response.status_code == 201
        
        # Obtener el ID del camión creado
        truck_info = json.loads(create_response.data)
        truck_id = truck_info.get('truck', 1)
        
        # Ver el camión creado
        response = client.get(f'/trucks/{truck_id}',
                        headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'truck' in data
        assert data['truck']['plate'] == truck_data['plate']
    
    def test_view_truck_not_found(self, client, auth_headers):
        """
        Test: Visualización de camión inexistente
        
        Verifica que:
        - Se rechaza la visualización de un camión que no existe
        - Se retorna el código de estado 404
        """
        response = client.get('/trucks/999',
                            headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_view_truck_without_auth(self, client):
        """
        Test: Visualización de camión sin autenticación
        
        Verifica que:
        - Se rechaza la visualización sin token de autenticación
        - Se retorna el código de estado 401
        """
        response = client.get('/trucks/1')
        
        assert response.status_code == 401
    
    def test_create_truck_missing_driver_id(self, client, auth_headers):
        """
        Test: Creación de camión sin driver_id
        
        Verifica que:
        - Se rechaza la creación si no se proporciona driver_id
        - Se retorna el código de estado 400
        - Se retorna un mensaje de error apropiado
        """
        truck_data = {
            "truck_id": "TRK005",
            "plate": "JKL012",
            "model": "MAN TGX",
            "brand": "MAN",
            "year": 2022,
            "mileage": 15000,
            "color": "Verde",
            "health_status": "Good",  # Agregar campo requerido
            "fleetanalytics_id": None  # Agregar campo requerido
            # Falta driver_id
        }
        
        response = client.post('/trucks/new',
                             data=json.dumps(truck_data),
                             headers=auth_headers)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Driver id is required' in data['message']
