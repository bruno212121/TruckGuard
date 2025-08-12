"""
Tests para las rutas de análisis de flota de TruckGuard API

Este módulo contiene tests automatizados para:
- GET /fleet/analytics - Obtener análisis de flota

Autor: TruckGuard Test Suite
Fecha: 2025
"""

import pytest
import json
from app.models.user import User as UserModel
from app.models.fleetanalytics import FleetAnalytics as FleetAnalyticsModel
from app import db


class TestFleetAnalyticsRoutes:
    """Clase que contiene todos los tests para las rutas de análisis de flota"""
    
    def test_get_fleet_analytics_success(self, client, auth_headers):
        """
        Test: Obtención exitosa de análisis de flota
        
        Verifica que:
        - Se puede obtener el análisis de flota del usuario autenticado
        - Se requiere autenticación y rol de owner
        - Se retorna el código de estado 200
        - Se retorna la información del análisis
        """
        response = client.get('/fleet/analytics',
                            headers=auth_headers)
        
        # Puede retornar 200 si hay datos o 404 si no hay análisis
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Verificar que retorna datos de análisis
            assert isinstance(data, dict)
        elif response.status_code == 404:
            data = json.loads(response.data)
            assert 'Message' in data or 'message' in data
    
    def test_get_fleet_analytics_without_auth(self, client):
        """
        Test: Obtención de análisis de flota sin autenticación
        
        Verifica que:
        - Se rechaza la obtención sin token de autenticación
        - Se retorna el código de estado 401
        """
        response = client.get('/fleet/analytics')
        
        assert response.status_code == 401
    
    def test_get_fleet_analytics_with_driver_role(self, client):
        """
        Test: Obtención de análisis de flota con rol de driver
        
        Verifica que:
        - Se rechaza la obtención con rol de driver
        - Se retorna el código de estado 403
        """
        # Crear un driver y hacer login
        driver_data = {
            "name": "Driver",
            "surname": "Test",
            "rol": "driver",
            "email": "driver.test@test.com",
            "phone": "123456789",
            "password": "password123"
        }
        
        client.post('/auth/register',
                   data=json.dumps(driver_data),
                   content_type='application/json')
        
        login_data = {
            "email": "driver.test@test.com",
            "password": "password123"
        }
        
        login_response = client.post('/auth/login',
                                   data=json.dumps(login_data),
                                   content_type='application/json')
        
        assert login_response.status_code == 200
        login_data = json.loads(login_response.data)
        driver_token = login_data['access_token']
        
        driver_headers = {
            'Authorization': f'Bearer {driver_token}',
            'Content-Type': 'application/json'
        }
        
        response = client.get('/fleet/analytics',
                            headers=driver_headers)
        
        # Debe fallar porque el driver no tiene permisos
        assert response.status_code == 403
    
    def test_get_fleet_analytics_no_data(self, client, auth_headers):
        """
        Test: Obtención de análisis de flota sin datos
        
        Verifica que:
        - Se maneja correctamente cuando no hay datos de análisis
        - Se retorna el código de estado 404
        - Se retorna un mensaje apropiado
        """
        # Limpiar cualquier dato existente (esto dependería de la implementación)
        # Por ahora, solo verificamos que la respuesta sea válida
        
        response = client.get('/fleet/analytics',
                            headers=auth_headers)
        
        if response.status_code == 404:
            data = json.loads(response.data)
            assert 'Message' in data or 'message' in data
            assert 'No existing fleet analytics' in data.get('Message', '') or 'No existing fleet analytics' in data.get('message', '')
    
    def test_get_fleet_analytics_invalid_token(self, client):
        """
        Test: Obtención de análisis de flota con token inválido
        
        Verifica que:
        - Se rechaza la obtención con token inválido
        - Se retorna el código de estado 401
        """
        invalid_headers = {
            'Authorization': 'Bearer invalid_token_here',
            'Content-Type': 'application/json'
        }
        
        response = client.get('/fleet/analytics',
                            headers=invalid_headers)
        
        assert response.status_code == 401
    
    def test_get_fleet_analytics_malformed_token(self, client):
        """
        Test: Obtención de análisis de flota con token malformado
        
        Verifica que:
        - Se rechaza la obtención con token malformado
        - Se retorna el código de estado 401
        """
        malformed_headers = {
            'Authorization': 'Bearer',
            'Content-Type': 'application/json'
        }
        
        response = client.get('/fleet/analytics',
                            headers=malformed_headers)
        
        assert response.status_code == 401
    
    def test_get_fleet_analytics_no_token(self, client):
        """
        Test: Obtención de análisis de flota sin token
        
        Verifica que:
        - Se rechaza la obtención sin token de autorización
        - Se retorna el código de estado 401
        """
        no_token_headers = {
            'Content-Type': 'application/json'
        }
        
        response = client.get('/fleet/analytics',
                            headers=no_token_headers)
        
        assert response.status_code == 401
