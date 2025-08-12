from app.models import TruckModel, UserModel
from app import db


def test_get_all_trucks_empty(client, auth_headers):
    """GET /trucks debe retornar lista vacía si no hay trucks."""
    response = client.get('/trucks/all', headers=auth_headers)
    assert response.status_code == 200
    assert response.json == {'trucks': []}


def test_get_all_trucks(client, auth_headers, app):
    with app.app_context():
        # Crear driver
        driver = UserModel(
            id=1,
            name='driver',
            surname='Test',
            rol='driver',
            email='driver@test.com',
            phone='123456789',
            password='test123'
        )
        db.session.add(driver)
        db.session.commit()

        # Obtener el owner del token
        from app.models.user import User
        owner = User.query.filter_by(email='owner@test.com').first()

        # Crear truck
        truck = TruckModel(
            truck_id=1,
            plate='ABC123',
            model='Model X',
            brand='Brand Y',
            year=2020,
            mileage=10000,
            color='Red',
            status='active',
            updated_at='2023-10-01 12:00:00',
            driver_id=1,
            owner_id=owner.id
        )
        db.session.add(truck)
        db.session.commit()

    response = client.get('/trucks/all', headers=auth_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert len(data['trucks']) == 1
    assert data['trucks'][0]['plate'] == 'ABC123'


