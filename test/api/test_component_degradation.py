import pytest
from app import db
from app.models.user import User as UserModel
from app.models.truck import Truck as TruckModel
from app.models.maintenance import Maintenance as MaintenanceModel
from app.models.trip import Trip as TripModel
from datetime import datetime


class TestComponentDegradation:
    """Test para verificar la degradación gradual de componentes"""
    
    def test_component_degradation_progression(self, app):
        """
        Test que verifica que los componentes se degraden gradualmente
        sin saltarse estados intermedios cuando se completan viajes.
        
        Estados esperados en orden:
        Excellent -> Very Good -> Good -> Fair -> Maintenance Required
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
            
            # 2. Crear camión con kilometraje inicial en 0
            truck = TruckModel(
                owner_id=owner.id,
                plate='ABC123',
                model='Test Model',
                brand='Test Brand',
                year='2020',
                color='Blue',
                mileage=0,
                health_status='Excellent',
                fleetanalytics_id=None,
                driver_id=driver.id
            )
            db.session.add(truck)
            db.session.commit()
            
            # 3. Crear componentes por defecto manualmente
            # Usaremos intervalos cortos para poder probar la degradación
            components_config = [
                {"name": "Aceite", "interval": 1000},  # Intervalo de 1000 km
            ]
            
            for comp in components_config:
                maintenance = MaintenanceModel(
                    description=f"Mantenimiento de {comp['name']}",
                    status='Excellent',
                    component=comp['name'],
                    cost=0,
                    mileage_interval=comp['interval'],
                    last_maintenance_mileage=0,
                    next_maintenance_mileage=comp['interval'],
                    truck_id=truck.truck_id,
                    driver_id=driver.id,
                    maintenance_interval=comp['interval']
                )
                db.session.add(maintenance)
            
            db.session.commit()
            
            # 4. Verificar estado inicial
            component = MaintenanceModel.query.filter_by(
                truck_id=truck.truck_id,
                component="Aceite"
            ).first()
            
            assert component is not None, "El componente debe existir"
            assert component.status == 'Excellent', f"Estado inicial debe ser Excellent, pero es {component.status}"
            assert component.accumulated_km == 0, f"KM acumulado inicial debe ser 0, pero es {component.accumulated_km}"
            
            print("\n=== Test de Degradación de Componentes ===")
            print(f"Estado inicial: {component.status} (0% - 0/{component.maintenance_interval} km)")
            
            # 5. Lista para rastrear todos los estados por los que pasa
            states_progression = [component.status]
            
            # 6. Simular viajes incrementales y verificar degradación
            test_distances = [
                (100, "10%"),    # 0-19%: Excellent
                (100, "20%"),    # 20-39%: Debería pasar a siguiente estado
                (100, "30%"),    
                (100, "40%"),    # 40-59%: Debería pasar a Very Good
                (100, "50%"),    
                (100, "60%"),    # 60-79%: Debería pasar a Good
                (100, "70%"),    
                (100, "80%"),    # 80-99%: Debería pasar a Fair
                (100, "90%"),    
                (100, "100%"),   # 100%+: Maintenance Required
                (100, "110%"),   
            ]
            
            for distance, percentage_label in test_distances:
                # Crear viaje
                trip = TripModel(
                    date=datetime.now(),
                    origin='Origin',
                    destination='Destination',
                    status='Pending',
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    driver_id=driver.id,
                    truck_id=truck.truck_id,
                    distance=0
                )
                db.session.add(trip)
                db.session.commit()
                
                # Cambiar estado a In Course
                trip.status = 'In Course'
                db.session.commit()
                
                # Completar viaje
                trip.complete_trip(distance)
                
                # Refrescar componente
                db.session.refresh(component)
                
                # Calcular porcentaje real
                percentage = (component.accumulated_km / component.maintenance_interval) * 100
                
                print(f"\nDespués de {component.accumulated_km} km ({percentage:.1f}%): {component.status}")
                
                # Agregar estado a la lista si cambió
                if component.status != states_progression[-1]:
                    states_progression.append(component.status)
                    print(f"  >> CAMBIO DE ESTADO: {states_progression[-2]} -> {component.status}")
            
            # 7. Verificar la progresión de estados
            print(f"\n=== Progresión de Estados ===")
            print(f"Estados por los que pasó: {' -> '.join(states_progression)}")
            
            # Estados esperados en orden correcto (sin saltarse ninguno)
            # Basado en la lógica actual, esperamos:
            # Excellent (0-19%) -> Good (20-59%) -> Very Good (40-59%) -> Good (60-79%) -> Fair (80-99%) -> Maintenance Required (100%+)
            
            # Pero esto no tiene sentido porque Good aparece dos veces
            # La secuencia lógica debería ser:
            # Excellent -> Very Good -> Good -> Fair -> Maintenance Required
            
            # Verificar que pasó por Excellent
            assert 'Excellent' in states_progression, "Debe pasar por el estado Excellent"
            
            # Verificar que llegó a Maintenance Required
            assert component.status == 'Maintenance Required', \
                f"Estado final debe ser 'Maintenance Required', pero es '{component.status}'"
            
            # Verificar que no se saltó estados importantes
            # Si la degradación es correcta, debería pasar por estados intermedios
            assert len(states_progression) > 2, \
                f"La degradación debe pasar por múltiples estados, pero solo pasó por {len(states_progression)}: {states_progression}"
            
            # Verificar que los estados están en orden lógico (de mejor a peor)
            state_order = {
                'Excellent': 0,
                'Very Good': 1,
                'Good': 2,
                'Fair': 3,
                'Maintenance Required': 4
            }
            
            print(f"\n=== Verificación de Orden ===")
            previous_order = -1
            for state in states_progression:
                current_order = state_order.get(state, -1)
                print(f"{state}: orden {current_order}")
                
                # Verificar que el orden es creciente (degradación)
                assert current_order > previous_order, \
                    f"La degradación debe ser progresiva. Estado '{state}' (orden {current_order}) " \
                    f"apareció después de un estado con orden {previous_order}. " \
                    f"Progresión completa: {' -> '.join(states_progression)}"
                
                previous_order = current_order
            
            print("\n[OK] Test completado exitosamente")
            print(f"[OK] La degradacion fue progresiva: {' -> '.join(states_progression)}")


    def test_component_degradation_with_multiple_components(self, app):
        """
        Test que verifica que múltiples componentes se degraden correctamente
        con diferentes intervalos de mantenimiento.
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
            
            # 2. Crear camión
            truck = TruckModel(
                owner_id=owner.id,
                plate='XYZ789',
                model='Test Model',
                brand='Test Brand',
                year='2020',
                color='Red',
                mileage=0,
                health_status='Excellent',
                fleetanalytics_id=None,
                driver_id=driver.id
            )
            db.session.add(truck)
            db.session.commit()
            
            # 3. Crear componentes con diferentes intervalos
            components_config = [
                {"name": "Aceite", "interval": 500},     # Se degrada rápido
                {"name": "Filtros", "interval": 1000},   # Degradación media
                {"name": "Frenos", "interval": 1500},    # Degradación lenta
            ]
            
            for comp in components_config:
                maintenance = MaintenanceModel(
                    description=f"Mantenimiento de {comp['name']}",
                    status='Excellent',
                    component=comp['name'],
                    cost=0,
                    mileage_interval=comp['interval'],
                    last_maintenance_mileage=0,
                    next_maintenance_mileage=comp['interval'],
                    truck_id=truck.truck_id,
                    driver_id=driver.id,
                    maintenance_interval=comp['interval']
                )
                db.session.add(maintenance)
            
            db.session.commit()
            
            print("\n=== Test de Múltiples Componentes ===")
            
            # 4. Simular varios viajes
            for i in range(10):
                distance = 100
                
                trip = TripModel(
                    date=datetime.now(),
                    origin='Origin',
                    destination='Destination',
                    status='Pending',
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    driver_id=driver.id,
                    truck_id=truck.truck_id,
                    distance=0
                )
                db.session.add(trip)
                db.session.commit()
                
                trip.status = 'In Course'
                db.session.commit()
                
                trip.complete_trip(distance)
                
                # Verificar cada componente
                components = MaintenanceModel.query.filter_by(truck_id=truck.truck_id).all()
                
                print(f"\nDespués de viaje {i+1} ({(i+1)*distance} km totales):")
                for comp in components:
                    percentage = (comp.accumulated_km / comp.maintenance_interval) * 100
                    print(f"  {comp.component}: {comp.status} ({percentage:.1f}%)")
                
                # Verificar que todos los componentes tienen un estado válido
                for comp in components:
                    assert comp.status in ['Excellent', 'Very Good', 'Good', 'Fair', 'Maintenance Required'], \
                        f"Componente {comp.component} tiene un estado inválido: {comp.status}"
            
            print("\n[OK] Test de multiples componentes completado")

