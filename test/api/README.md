# 🚛 TruckGuard API Test Suite

Este directorio contiene una suite completa de tests automatizados para la API de TruckGuard. Los tests están organizados por módulos y cubren todas las funcionalidades principales de la aplicación.

## 📁 Estructura del Proyecto

```
test/api/
├── __init__.py                           # Módulo de tests de API
├── README.md                             # Este archivo
├── run_tests.py                          # Script para ejecutar tests
├── test_auth_routes.py                   # Tests de autenticación
├── test_truck_routes.py                  # Tests de gestión de camiones
├── test_trip_routes.py                   # Tests de gestión de viajes
├── test_maintenance_routes.py            # Tests de mantenimiento
├── test_user_routes.py                   # Tests de gestión de usuarios
└── test_fleet_analytics_routes.py        # Tests de análisis de flota
```

## 🚀 Cómo Ejecutar los Tests

### Ejecutar Todos los Tests

```bash
# Desde el directorio raíz del proyecto
python test/api/run_tests.py

# Con output detallado
python test/api/run_tests.py --verbose

# Con reporte de cobertura
python test/api/run_tests.py --coverage
```

### Ejecutar Tests Específicos

```bash
# Solo tests de autenticación
python test/api/run_tests.py --module auth

# Solo tests de camiones
python test/api/run_tests.py --module truck

# Solo tests de viajes
python test/api/run_tests.py --module trip

# Solo tests de mantenimiento
python test/api/run_tests.py --module maintenance

# Solo tests de usuarios
python test/api/run_tests.py --module user

# Solo tests de análisis de flota
python test/api/run_tests.py --module fleet
```

### Ver Resumen de Tests

```bash
python test/api/run_tests.py --summary
```

### Ejecutar con Pytest Directamente

```bash
# Todos los tests
pytest test/api/

# Tests específicos
pytest test/api/test_auth_routes.py
pytest test/api/test_truck_routes.py

# Con output detallado
pytest -v test/api/

# Con cobertura
pytest --cov=app test/api/
```

## 📊 Estadísticas de Tests

| Módulo | Tests | Descripción |
|--------|-------|-------------|
| `test_auth_routes.py` | 8 | Autenticación (login/register) |
| `test_truck_routes.py` | 8 | Gestión de camiones |
| `test_trip_routes.py` | 8 | Gestión de viajes |
| `test_maintenance_routes.py` | 6 | Mantenimiento |
| `test_user_routes.py` | 10 | Gestión de usuarios |
| `test_fleet_analytics_routes.py` | 6 | Análisis de flota |

**Total: 46 tests**

## 🔧 Configuración de Tests

### Fixtures Disponibles

Los tests utilizan fixtures definidas en `test/conftest.py`:

- `app`: Instancia de la aplicación Flask configurada para testing
- `client`: Cliente de testing para hacer peticiones HTTP
- `auth_headers`: Headers de autenticación con token JWT válido

### Base de Datos de Testing

Los tests utilizan una base de datos SQLite en memoria que se crea y destruye para cada test, asegurando que cada test sea independiente.

## 📋 Descripción de los Tests

### 🔐 Tests de Autenticación (`test_auth_routes.py`)

**Endpoints probados:**
- `POST /auth/register` - Registro de usuarios
- `POST /auth/login` - Inicio de sesión

**Casos de prueba:**
- ✅ Registro exitoso de usuario
- ❌ Registro con campos faltantes
- ❌ Registro con email duplicado
- ✅ Login exitoso
- ❌ Login con email inexistente
- ❌ Login con contraseña incorrecta
- ❌ Login con campos faltantes

### 🚛 Tests de Camiones (`test_truck_routes.py`)

**Endpoints probados:**
- `POST /trucks/new` - Crear camión
- `GET /trucks/all` - Listar camiones
- `GET /trucks/<id>` - Ver camión específico

**Casos de prueba:**
- ✅ Creación exitosa de camión
- ❌ Creación sin autenticación
- ❌ Creación con driver inválido
- ✅ Listado de camiones
- ❌ Listado sin autenticación
- ✅ Visualización de camión específico
- ❌ Visualización de camión inexistente
- ❌ Creación sin driver_id

### 🛣️ Tests de Viajes (`test_trip_routes.py`)

**Endpoints probados:**
- `POST /trips/new` - Crear viaje
- `GET /trips/all` - Listar viajes
- `GET /trips/<id>` - Ver viaje específico

**Casos de prueba:**
- ✅ Creación exitosa de viaje
- ❌ Creación sin autenticación
- ❌ Creación con camión inexistente
- ❌ Creación con driver inexistente
- ✅ Listado de viajes
- ✅ Listado con filtros
- ❌ Listado sin autenticación
- ✅ Visualización de viaje específico
- ❌ Visualización de viaje inexistente

### 🔧 Tests de Mantenimiento (`test_maintenance_routes.py`)

**Endpoints probados:**
- `POST /maintenance/new` - Crear mantenimiento

**Casos de prueba:**
- ✅ Creación exitosa de mantenimiento
- ❌ Creación sin autenticación
- ❌ Creación con camión inexistente
- ✅ Creación con datos mínimos
- ✅ Creación con rol de driver
- ❌ Creación con errores de validación

### 👥 Tests de Usuarios (`test_user_routes.py`)

**Endpoints probados:**
- `GET /user/<id>` - Obtener usuario
- `PUT /user/<id>` - Actualizar usuario
- `DELETE /user/<id>` - Eliminar usuario
- `GET /users` - Listar usuarios
- `POST /users` - Crear usuario

**Casos de prueba:**
- ✅ Obtención de usuario específico
- ❌ Obtención de usuario inexistente
- ❌ Obtención sin autenticación
- ✅ Actualización de usuario
- ❌ Actualización de usuario inexistente
- ❌ Actualización sin autenticación
- ✅ Eliminación de usuario
- ❌ Eliminación de usuario inexistente
- ❌ Eliminación sin autenticación
- ✅ Listado de usuarios
- ✅ Listado con filtros
- ❌ Listado sin autenticación
- ✅ Creación de usuario
- ❌ Creación sin autenticación

### 📈 Tests de Análisis de Flota (`test_fleet_analytics_routes.py`)

**Endpoints probados:**
- `GET /fleet/analytics` - Obtener análisis de flota

**Casos de prueba:**
- ✅ Obtención exitosa de análisis
- ❌ Obtención sin autenticación
- ❌ Obtención con rol de driver
- ❌ Obtención sin datos
- ❌ Obtención con token inválido
- ❌ Obtención con token malformado
- ❌ Obtención sin token

## 🛡️ Validaciones Implementadas

### Autenticación y Autorización
- ✅ Verificación de tokens JWT
- ✅ Validación de roles (owner, driver)
- ✅ Manejo de tokens inválidos o expirados

### Validación de Datos
- ✅ Campos obligatorios
- ✅ Tipos de datos correctos
- ✅ Validación de emails únicos
- ✅ Validación de relaciones entre entidades

### Manejo de Errores
- ✅ Códigos de estado HTTP apropiados
- ✅ Mensajes de error descriptivos
- ✅ Manejo de recursos inexistentes
- ✅ Validación de permisos

## 📝 Convenciones de Nomenclatura

### Nombres de Tests
- `test_[funcionalidad]_success` - Casos exitosos
- `test_[funcionalidad]_without_auth` - Sin autenticación
- `test_[funcionalidad]_invalid_[campo]` - Datos inválidos
- `test_[funcionalidad]_not_found` - Recursos inexistentes

### Estructura de Tests
```python
def test_nombre_del_test(self, client, auth_headers):
    """
    Test: Descripción breve del test
    
    Verifica que:
    - Punto 1
    - Punto 2
    - Punto 3
    """
    # Setup
    # Action
    # Assert
```

## 🔍 Debugging de Tests

### Ver Output Detallado
```bash
pytest -v -s test/api/
```

### Ejecutar Test Específico
```bash
pytest test/api/test_auth_routes.py::TestAuthRoutes::test_login_success -v
```

### Ver Cobertura Detallada
```bash
pytest --cov=app --cov-report=html test/api/
# Abrir htmlcov/index.html en el navegador
```

## 🚨 Troubleshooting

### Error: "Module not found"
```bash
# Asegúrate de estar en el directorio raíz del proyecto
cd /path/to/TruckGuard
python test/api/run_tests.py
```

### Error: "Database connection failed"
- Verifica que el archivo `.env` esté configurado correctamente
- Los tests usan base de datos en memoria, no debería ser un problema

### Error: "JWT token invalid"
- Los tests crean tokens automáticamente
- Verifica que `JWT_SECRET_KEY` esté configurado en el entorno de testing

## 📚 Recursos Adicionales

- [Documentación de Pytest](https://docs.pytest.org/)
- [Documentación de Flask Testing](https://flask.palletsprojects.com/en/2.3.x/testing/)
- [Documentación de Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)

## 🤝 Contribución

Para agregar nuevos tests:

1. Crea un nuevo archivo `test_[modulo]_routes.py`
2. Sigue las convenciones de nomenclatura
3. Documenta cada test con docstrings
4. Ejecuta todos los tests para verificar que no rompas nada
5. Actualiza este README con la nueva información

---

**Autor:** TruckGuard Test Suite  
**Fecha:** 2025  
**Versión:** 1.0.0
