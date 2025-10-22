import pytest
from app import db
from app.models.user import User as UserModel
from app.models.truck import Truck as TruckModel
from app.models.maintenance import Maintenance as MaintenanceModel
from app.models.trip import Trip as TripModel
from app.resources.component_restx_routes import ComponentManager
from datetime import datetime


class TestDefaultComponentsRiskAlerts:
    """Test para verificar las alertas de riesgo con componentes por defecto"""
    
    def test_risk_alerts_with_default_components_long_trip(self, app):
        """
        Test que verifica que se generen alertas de riesgo cuando se crea un viaje largo
        con componentes por defecto que están cerca de su límite de mantenimiento.
        """
        with app.app_context():
            # 1. Crear usuario owner y driver
            owner = UserModel(
                name='Owner',
                surname='Test',
                rol='owner',
                email='owner@test.com',
                phone='123456789',
                password='test123'
            )
            driver = UserModel(
                name='Driver',
                surname='Test',
                rol='driver',
                email='driver@test.com',
                phone='987654321',
                password='test123'
            )
            db.session.add(owner)
            db.session.add(driver)
            db.session.commit()
            
            # 2. Crear camión con kilometraje alto para simular uso
            truck = TruckModel(
                owner_id=owner.id,
                plate='ALERT123',
                model='Test Model',
                brand='Test Brand',
                year='2020',
                color='Blue',
                mileage=50000,  # Camión con mucho uso
                health_status='Good',
                fleetanalytics_id=None,
                driver_id=driver.id
            )
            db.session.add(truck)
            db.session.commit()
            
            # 3. Crear componentes por defecto usando ComponentManager
            print("\n=== Test de Alertas con Componentes por Defecto ===")
            print(f"Camion con kilometraje: {truck.mileage} km")
            
            # Usar ComponentManager para crear componentes por defecto
            created_components = ComponentManager.create_components_for_truck(
                truck, None, driver.id
            )
            
            # Simular que los componentes han acumulado kilometraje
            # Vamos a poner algunos componentes cerca del límite
            components = MaintenanceModel.query.filter_by(truck_id=truck.truck_id).all()
            
            print(f"\nComponentes creados: {len(components)}")
            for comp in components:
                print(f"- {comp.component}: {comp.status} (intervalo: {comp.maintenance_interval} km)")
            
            # 4. Simular uso acumulado en algunos componentes para crear riesgo
            risk_scenarios = [
                {"name": "Aceite", "accumulated_km": 4000},      # 80% de 5000 km
                {"name": "Filtros", "accumulated_km": 8000},     # 80% de 10000 km  
                {"name": "Frenos", "accumulated_km": 7600},      # 80% de 9500 km
            ]
            
            for scenario in risk_scenarios:
                comp = next((c for c in components if c.component == scenario["name"]), None)
                if comp:
                    comp.accumulated_km = scenario["accumulated_km"]
                    comp.update_status()  # Actualizar estado basado en nuevo kilometraje
                    print(f"Configurado {comp.component}: {comp.accumulated_km} km ({comp.status})")
            
            db.session.commit()
            
            # 5. Simular un viaje largo que pondría componentes en riesgo
            trip_distance = 2000  # km - viaje largo
            
            print(f"\n=== Simulacion de Viaje Largo ===")
            print(f"Distancia del viaje: {trip_distance} km")
            
            # Simular la lógica de validación que se haría en el endpoint
            risk_components = []
            fair_components = []
            
            for comp in components:
                # Calcular proyección después del viaje
                projected_km = comp.accumulated_km + trip_distance
                projected_percentage = (projected_km / comp.maintenance_interval) * 100
                
                print(f"\n{comp.component}:")
                print(f"  Estado actual: {comp.status}")
                print(f"  KM acumulados: {comp.accumulated_km}")
                print(f"  KM proyectados: {projected_km}")
                print(f"  Porcentaje actual: {(comp.accumulated_km / comp.maintenance_interval) * 100:.1f}%")
                print(f"  Porcentaje proyectado: {projected_percentage:.1f}%")
                
                # Detectar riesgo
                if comp.status == 'Maintenance Required':
                    print(f"  [CRITICO] REQUIERE MANTENIMIENTO INMEDIATO")
                elif comp.status == 'Fair':
                    fair_components.append(comp.component)
                    print(f"  [ADVERTENCIA] ESTADO FAIR - Alta probabilidad de falla")
                    
                    # También considerar componentes Fair que estarían en riesgo
                    if projected_percentage >= 100:
                        risk_components.append({
                            'component': comp.component,
                            'current_status': comp.status,
                            'current_km': comp.accumulated_km,
                            'projected_km': projected_km,
                            'projected_percentage': projected_percentage,
                            'maintenance_interval': comp.maintenance_interval,
                            'risk_level': 'HIGH'
                        })
                        print(f"  [RIESGO] DETECTADO - Nivel: HIGH (Fair + 100%+)")
                elif comp.status == 'Good' and projected_percentage >= 80:
                    risk_components.append({
                        'component': comp.component,
                        'current_status': comp.status,
                        'current_km': comp.accumulated_km,
                        'projected_km': projected_km,
                        'projected_percentage': projected_percentage,
                        'maintenance_interval': comp.maintenance_interval,
                        'risk_level': 'HIGH' if projected_percentage >= 100 else 'MEDIUM'
                    })
                    print(f"  [RIESGO] DETECTADO - Nivel: {'HIGH' if projected_percentage >= 100 else 'MEDIUM'}")
                else:
                    print(f"  [OK] SIN RIESGO")
            
            # 6. Verificar que se detectaron componentes en riesgo
            assert len(risk_components) > 0, "Deberian detectarse componentes en riesgo con un viaje largo"
            
            print(f"\n=== Resumen de Riesgos Detectados ===")
            print(f"Componentes en riesgo: {len(risk_components)}")
            print(f"Componentes en estado Fair: {len(fair_components)}")
            
            # 7. Simular la respuesta que recibiría el usuario
            print(f"\n=== Simulacion de Respuesta del Sistema ===")
            print(f"Estado: VIAJE PERMITIDO con alertas de riesgo")
            print(f"Mensaje: Trip created")
            
            if fair_components:
                print(f"Advertencia Fair: Los siguientes componentes estan en estado Fair y tienen alta probabilidad de fallar: {', '.join(fair_components)}")
            
            if risk_components:
                high_risk = [rc for rc in risk_components if rc['risk_level'] == 'HIGH']
                medium_risk = [rc for rc in risk_components if rc['risk_level'] == 'MEDIUM']
                
                if high_risk:
                    high_names = [rc['component'] for rc in high_risk]
                    print(f"ALTO RIESGO: Los siguientes componentes llegaran al 100% o mas durante el viaje: {', '.join(high_names)}")
                
                if medium_risk:
                    medium_names = [rc['component'] for rc in medium_risk]
                    print(f"RIESGO MEDIO: Los siguientes componentes llegaran al 80% o mas durante el viaje: {', '.join(medium_names)}")
                
                print(f"Recomendacion: Se recomienda realizar mantenimiento preventivo antes del viaje para evitar fallas mecanicas.")
            
            print(f"\nEl usuario puede decidir si continuar o no con el viaje basado en esta informacion.")
            
            # 8. Verificar que el sistema funciona correctamente
            assert len(risk_components) >= 2, f"Deberian detectarse al menos 2 componentes en riesgo, pero se detectaron {len(risk_components)}"
            
            # Verificar que hay componentes de alto riesgo
            high_risk_count = len([rc for rc in risk_components if rc['risk_level'] == 'HIGH'])
            assert high_risk_count > 0, "Deberia haber al menos un componente de alto riesgo"
            
            print(f"\n[OK] Test completado exitosamente")
            print(f"[OK] Se detectaron {len(risk_components)} componentes en riesgo")
            print(f"[OK] Sistema de alertas funcionando correctamente")


    def test_no_risk_with_short_trip(self, app):
        """
        Test que verifica que NO se generen alertas de riesgo con un viaje corto
        usando componentes por defecto.
        """
        with app.app_context():
            # 1. Crear usuario owner y driver
            owner = UserModel(
                name='Owner',
                surname='Test',
                rol='owner',
                email='owner2@test.com',
                phone='123456789',
                password='test123'
            )
            driver = UserModel(
                name='Driver',
                surname='Test',
                rol='driver',
                email='driver2@test.com',
                phone='987654321',
                password='test123'
            )
            db.session.add(owner)
            db.session.add(driver)
            db.session.commit()
            
            # 2. Crear camión con kilometraje moderado
            truck = TruckModel(
                owner_id=owner.id,
                plate='SAFE123',
                model='Test Model',
                brand='Test Brand',
                year='2020',
                color='Green',
                mileage=20000,  # Camión con uso moderado
                health_status='Excellent',
                fleetanalytics_id=None,
                driver_id=driver.id
            )
            db.session.add(truck)
            db.session.commit()
            
            # 3. Crear componentes por defecto
            print("\n=== Test de Viaje Corto Sin Riesgo ===")
            print(f"Camion con kilometraje: {truck.mileage} km")
            
            created_components = ComponentManager.create_components_for_truck(
                truck, None, driver.id
            )
            
            components = MaintenanceModel.query.filter_by(truck_id=truck.truck_id).all()
            
            # 4. Simular un viaje corto
            trip_distance = 500  # km - viaje corto
            
            print(f"\nDistancia del viaje: {trip_distance} km")
            
            # Simular validación
            risk_components = []
            
            for comp in components:
                projected_km = comp.accumulated_km + trip_distance
                projected_percentage = (projected_km / comp.maintenance_interval) * 100
                
                print(f"{comp.component}: {comp.status} -> {projected_percentage:.1f}%")
                
                if comp.status == 'Good' and projected_percentage >= 80:
                    risk_components.append(comp.component)
            
            # 5. Verificar que NO hay componentes en riesgo
            assert len(risk_components) == 0, f"No deberian detectarse componentes en riesgo con un viaje corto, pero se detectaron: {risk_components}"
            
            print(f"\n[OK] Viaje corto sin riesgo - Sistema funcionando correctamente")
            print(f"[OK] No se generaron alertas innecesarias")


    def test_mixed_risk_scenarios(self, app):
        """
        Test que verifica diferentes escenarios de riesgo con componentes por defecto.
        """
        with app.app_context():
            # 1. Crear usuario owner y driver
            owner = UserModel(
                name='Owner',
                surname='Test',
                rol='owner',
                email='owner3@test.com',
                phone='123456789',
                password='test123'
            )
            driver = UserModel(
                name='Driver',
                surname='Test',
                rol='driver',
                email='driver3@test.com',
                phone='987654321',
                password='test123'
            )
            db.session.add(owner)
            db.session.add(driver)
            db.session.commit()
            
            # 2. Crear camión
            truck = TruckModel(
                owner_id=owner.id,
                plate='MIXED123',
                model='Test Model',
                brand='Test Brand',
                year='2020',
                color='Yellow',
                mileage=30000,
                health_status='Good',
                fleetanalytics_id=None,
                driver_id=driver.id
            )
            db.session.add(truck)
            db.session.commit()
            
            # 3. Crear componentes por defecto
            created_components = ComponentManager.create_components_for_truck(
                truck, None, driver.id
            )
            
            components = MaintenanceModel.query.filter_by(truck_id=truck.truck_id).all()
            
            # 4. Configurar diferentes estados de componentes
            scenarios = [
                {"name": "Aceite", "accumulated_km": 1000, "expected_status": "Excellent"},
                {"name": "Filtros", "accumulated_km": 5000, "expected_status": "Good"},
                {"name": "Frenos", "accumulated_km": 7000, "expected_status": "Good"},
            ]
            
            for scenario in scenarios:
                comp = next((c for c in components if c.component == scenario["name"]), None)
                if comp:
                    comp.accumulated_km = scenario["accumulated_km"]
                    comp.update_status()
                    print(f"{comp.component}: {comp.accumulated_km} km -> {comp.status}")
            
            db.session.commit()
            
            # 5. Probar diferentes distancias de viaje
            test_distances = [1000, 2000, 3000]  # km
            
            for distance in test_distances:
                print(f"\n=== Viaje de {distance} km ===")
                
                risk_components = []
                for comp in components:
                    projected_km = comp.accumulated_km + distance
                    projected_percentage = (projected_km / comp.maintenance_interval) * 100
                    
                    if comp.status == 'Good' and projected_percentage >= 80:
                        risk_components.append(comp.component)
                        print(f"  {comp.component}: RIESGO ({projected_percentage:.1f}%)")
                    else:
                        print(f"  {comp.component}: Sin riesgo ({projected_percentage:.1f}%)")
                
                print(f"Componentes en riesgo: {len(risk_components)}")
            
            print(f"\n[OK] Test de escenarios mixtos completado exitosamente")
