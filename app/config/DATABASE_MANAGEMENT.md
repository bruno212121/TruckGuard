# 🔧 Configuración del Pool de Conexiones y Manejo de Sesiones

## 📍 Ubicaciones de Configuración

### 1. **Configuración Principal del Pool**
**Archivo:** `app/__init__.py` (líneas 32-38)

```python
# Configuración para MySQL usando la configuración optimizada
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = get_database_config()
setup_database_events()
```

### 2. **Configuración Detallada del Pool**
**Archivo:** `app/config/database_config.py`

```python
def get_database_config():
    return {
        'pool_pre_ping': True,           # Verifica conexiones antes de usarlas
        'pool_recycle': 300,             # Recicla conexiones cada 5 minutos
        'pool_timeout': 20,              # Timeout de 20 segundos
        'pool_size': 10,                 # Tamaño del pool de conexiones
        'max_overflow': 5,               # Conexiones adicionales permitidas
        'pool_reset_on_return': 'commit', # Reset automático al devolver conexión
        'echo': False,                   # No mostrar queries SQL en logs
    }
```

### 3. **Cierre Automático de Sesiones**
**Archivo:** `app/__init__.py` (líneas 70-74)

```python
@app.teardown_appcontext
def shutdown_session(exception=None):
    """Cierra la sesión de base de datos al final de cada request"""
    db.session.remove()
```

## 🛠️ Decoradores para Manejo de Sesiones

### 1. **Decorador Básico de Sesión**
**Archivo:** `app/utils/decorators.py`

```python
from app.utils.decorators import db_session_management

@db_session_management
def mi_funcion():
    # Tu código aquí
    # La sesión se cierra automáticamente
    pass
```

### 2. **Decorador de Transacción**
```python
from app.utils.decorators import db_transaction

@db_transaction
def mi_operacion_compleja():
    # Múltiples operaciones de BD
    # Commit automático si todo sale bien
    # Rollback automático si hay error
    pass
```

## 📊 Parámetros del Pool Explicados

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `pool_size` | 10 | Número de conexiones permanentes en el pool |
| `max_overflow` | 5 | Conexiones adicionales que se pueden crear |
| `pool_timeout` | 20s | Tiempo máximo para obtener una conexión |
| `pool_recycle` | 300s | Tiempo después del cual se recicla una conexión |
| `pool_pre_ping` | True | Verifica que la conexión esté activa antes de usarla |
| `pool_reset_on_return` | 'commit' | Resetea la conexión al devolverla al pool |

## 🚀 Configuraciones por Entorno

### **Desarrollo**
- Pool más pequeño (5 conexiones)
- Logs de queries habilitados
- Timeout más corto

### **Producción**
- Pool más grande (20 conexiones)
- Logs deshabilitados
- Configuraciones optimizadas para MySQL

## ⚠️ Mejores Prácticas

### ✅ **Hacer:**
1. Usar los decoradores `@db_session_management` o `@db_transaction`
2. Dejar que SQLAlchemy maneje el pool automáticamente
3. Usar `db.session.remove()` en `@app.teardown_appcontext`

### ❌ **Evitar:**
1. Hacer `db.session.close()` manualmente en endpoints
2. Crear conexiones manualmente
3. No manejar excepciones en operaciones de BD

## 🔍 Monitoreo

### **Logs de Queries Lentas**
En desarrollo, se registran automáticamente queries que toman más de 1 segundo.

### **Eventos de Conexión**
Se configuran automáticamente parámetros específicos de MySQL al conectar.

## 🛡️ Manejo de Errores

El sistema maneja automáticamente:
- Rollback en caso de errores
- Cierre de sesiones al final de requests
- Reciclado de conexiones inactivas
- Verificación de conexiones antes de usarlas

## 📝 Ejemplo de Uso en Endpoints

```python
from app.utils.decorators import db_transaction, role_required
from flask_restx import Resource

@maintenance_ns.route('/new')
class CreateMaintenance(Resource):
    @maintenance_ns.expect(create_maintenance_model)
    @jwt_required()
    @role_required(['owner', 'driver'])
    @db_transaction  # ← Usar este decorador
    def post(self):
        # Tu código aquí
        # No necesitas manejar db.session.commit() o rollback()
        pass
```
