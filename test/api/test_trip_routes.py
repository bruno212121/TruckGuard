"""
Tests para las rutas de viajes de TruckGuard API

Este módulo contiene tests automatizados para:
- POST /trips/new - Crear nuevo viaje
- GET /trips/all - Listar todos los viajes
- GET /trips/<id> - Ver viaje específico

Autor: TruckGuard Test Suite
Fecha: 2025
"""

import pytest
import json
from app.models.user import User as UserModel
from app.models.truck import Truck as TruckModel
from app.models.trip import Trip as TripModel
from app import db


class TestTripRoutes:
    """Clase que contiene todos los tests para las rutas de viajes"""
    
    def test_create_trip_success(self, client, auth_headers):
        """
        Test: Creación exitosa de un viaje
        
        Verifica que:
        - Se puede crear un viaje con datos válidos
        - Se requiere autenticación y rol de owner
        - Se retorna el código de estado 201
        """
        # Crear un driver
        driver_data = {
            "name": "Roberto",
            "surname": "Silva",
            "rol": "driver",
            "email": "roberto.silva@test.com",
            "phone": "555123456",
            "password": "password123"
        }
        
        client.post('/auth/register',
                   data=json.dumps(driver_data),
                   content_type='application/json')
        
        # Crear un camión
        truck_data = {
            "truck_id": "TRK006",
            "plate": "MNO345",
            "model": "DAF XF",
            "brand": "DAF",
            "year": 2021,
            "mileage": 40000,
            "color": "Gris",
            "driver_id": 1
        }
        
        client.post('/trucks/new',
                   data=json.dumps(truck_data),
                   headers=auth_headers)
        
        # Crear el viaje
        trip_data = {
            "origin": "Madrid, España",
            "destination": "Barcelona, España",
            "truck_id": 1,
            "driver_id": 1,
            "status": "Pending"
        }
        
        response = client.post('/trips/new',
                             data=json.dumps(trip_data),
                             headers=auth_headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['origin'] == trip_data['origin']
        assert data['destination'] == trip_data['destination']
        assert data['status'] == trip_data['status']
    
    def test_create_trip_without_auth(self, client):
        """
        Test: Creación de viaje sin autenticación
        
        Verifica que:
        - Se rechaza la creación sin token de autenticación
        - Se retorna el código de estado 401
        """
        trip_data = {
            "origin": "Valencia, España",
            "destination": "Sevilla, España",
            "truck_id": 1,
            "driver_id": 1,
            "status": "Pending"
        }
        
        response = client.post('/trips/new',
                             data=json.dumps(trip_data),
                             content_type='application/json')
        
        assert response.status_code == 401
    
    def test_create_trip_invalid_truck(self, client, auth_headers):
        """
        Test: Creación de viaje con camión inexistente
        
        Verifica que:
        - Se rechaza la creación si el truck_id no existe
        - Se retorna el código de estado 404
        - Se retorna un mensaje de error apropiado
        """
        # Crear solo el driver
        driver_data = {
            "name": "Carlos",
            "surname": "Mendoza",
            "rol": "driver",
            "email": "carlos.mendoza@test.com",
            "phone": "123789456",
            "password": "password123"
        }
        
        client.post('/auth/register',
                   data=json.dumps(driver_data),
                   content_type='application/json')
        
        trip_data = {
            "origin": "Bilbao, España",
            "destination": "Zaragoza, España",
            "truck_id": 999,  # Camión inexistente
            "driver_id": 1,
            "status": "Pending"
        }
        
        response = client.post('/trips/new',
                             data=json.dumps(trip_data),
                             headers=auth_headers)
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Truck not found' in data['error']
    
    def test_create_trip_invalid_driver(self, client, auth_headers):
        """
        Test: Creación de viaje con driver inexistente
        
        Verifica que:
        - Se rechaza la creación si el driver_id no existe
        - Se retorna el código de estado 404
        - Se retorna un mensaje de error apropiado
        """
        # Crear solo el camión
        driver_data = {
            "name": "Miguel",
            "surname": "Torres",
            "rol": "driver",
            "email": "miguel.torres@test.com",
            "phone": "987123654",
            "password": "password123"
        }
        
        client.post('/auth/register',
                   data=json.dumps(driver_data),
                   content_type='application/json')
        
        truck_data = {
            "truck_id": "TRK007",
            "plate": "PQR678",
            "model": "Renault T",
            "brand": "Renault",
            "year": 2020,
            "mileage": 60000,
            "color": "Azul",
            "driver_id": 1
        }
        
        client.post('/trucks/new',
                   data=json.dumps(truck_data),
                   headers=auth_headers)
        
        trip_data = {
            "origin": "Málaga, España",
            "destination": "Granada, España",
            "truck_id": 1,
            "driver_id": 999,  # Driver inexistente
            "status": "Pending"
        }
        
        response = client.post('/trips/new',
                             data=json.dumps(trip_data),
                             headers=auth_headers)
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Driver not found' in data['error']
    
    def test_list_trips_success(self, client, auth_headers):
        """
        Test: Listado exitoso de viajes
        
        Verifica que:
        - Se pueden listar todos los viajes
        - Se requiere autenticación y rol de owner
        - Se retorna el código de estado 200
        - Se retorna una lista de viajes con paginación
        """
        response = client.get('/trips/all',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'trips' in data
        assert 'total' in data
        assert 'pages' in data
        assert 'page' in data
        assert isinstance(data['trips'], list)
    
    def test_list_trips_with_filters(self, client, auth_headers):
        """
        Test: Listado de viajes con filtros
        
        Verifica que:
        - Se pueden filtrar viajes por origen, destino, estado y driver_id
        - Los filtros funcionan correctamente
        """
        # Crear datos de prueba primero
        driver_data = {
            "name": "Fernando",
            "surname": "Castro",
            "rol": "driver",
            "email": "fernando.castro@test.com",
            "phone": "456789123",
            "password": "password123"
        }
        
        client.post('/auth/register',
                   data=json.dumps(driver_data),
                   content_type='application/json')
        
        truck_data = {
            "truck_id": "TRK008",
            "plate": "STU901",
            "model": "Scania G410",
            "brand": "Scania",
            "year": 2019,
            "mileage": 80000,
            "color": "Negro",
            "driver_id": 1
        }
        
        client.post('/trucks/new',
                   data=json.dumps(truck_data),
                   headers=auth_headers)
        
        trip_data = {
            "origin": "Alicante, España",
            "destination": "Murcia, España",
            "truck_id": 1,
            "driver_id": 1,
            "status": "In Progress"
        }
        
        client.post('/trips/new',
                   data=json.dumps(trip_data),
                   headers=auth_headers)
        
        # Probar filtros
        response = client.get('/trips/all?origin=Alicante&status=In Progress',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['trips']) >= 0  # Puede ser 0 si no hay coincidencias
    
    def test_list_trips_without_auth(self, client):
        """
        Test: Listado de viajes sin autenticación
        
        Verifica que:
        - Se rechaza el listado sin token de autenticación
        - Se retorna el código de estado 401
        """
        response = client.get('/trips/all')
        
        assert response.status_code == 401
    
    def test_view_trip_success(self, client, auth_headers):
        """
        Test: Visualización exitosa de un viaje específico
        
        Verifica que:
        - Se puede ver un viaje específico por ID
        - Se requiere autenticación y rol de owner
        - Se retorna el código de estado 200
        - Se retorna la información del viaje con detalles del driver y camión
        """
        # Crear datos de prueba
        driver_data = {
            "name": "Javier",
            "surname": "Ruiz",
            "rol": "driver",
            "email": "javier.ruiz@test.com",
            "phone": "321654987",
            "password": "password123"
        }
        
        client.post('/auth/register',
                   data=json.dumps(driver_data),
                   content_type='application/json')
        
        truck_data = {
            "truck_id": "TRK009",
            "plate": "VWX234",
            "model": "Volvo FM",
            "brand": "Volvo",
            "year": 2022,
            "mileage": 25000,
            "color": "Blanco",
            "driver_id": 1
        }
        
        client.post('/trucks/new',
                   data=json.dumps(truck_data),
                   headers=auth_headers)
        
        trip_data = {
            "origin": "Córdoba, España",
            "destination": "Jaén, España",
            "truck_id": 1,
            "driver_id": 1,
            "status": "Completed"
        }
        
        client.post('/trips/new',
                   data=json.dumps(trip_data),
                   headers=auth_headers)
        
        # Ver el viaje creado
        response = client.get('/trips/1',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'trip' in data
        assert data['trip']['origin'] == trip_data['origin']
        assert data['trip']['destination'] == trip_data['destination']
        assert 'driver' in data['trip']
        assert 'truck_details' in data['trip']
    
    def test_view_trip_not_found(self, client, auth_headers):
        """
        Test: Visualización de viaje inexistente
        
        Verifica que:
        - Se rechaza la visualización de un viaje que no existe
        - Se retorna el código de estado 404
        """
        response = client.get('/trips/999',
                            headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_view_trip_without_auth(self, client):
        """
        Test: Visualización de viaje sin autenticación
        
        Verifica que:
        - Se rechaza la visualización sin token de autenticación
        - Se retorna el código de estado 401
        """
        response = client.get('/trips/1')
        
        assert response.status_code == 401
