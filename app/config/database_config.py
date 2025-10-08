"""
Configuración específica para la base de datos y manejo de conexiones
"""
import os
import time
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Configurar logging para la base de datos
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

def get_database_config():
    """
    Retorna la configuración optimizada para la base de datos
    """
    # Configuración base del pool de conexiones
    base_config = {
        'pool_pre_ping': True,           # Verifica conexiones antes de usarlas
        'pool_recycle': 300,             # Recicla conexiones cada 5 minutos
        'pool_timeout': 20,              # Timeout de 20 segundos
        'pool_size': 10,                 # Tamaño del pool de conexiones
        'max_overflow': 5,               # Conexiones adicionales permitidas
        'pool_reset_on_return': 'commit', # Reset automático al devolver conexión
        'echo': False,                   # No mostrar queries SQL en logs
        'connect_args': {
            'charset': 'utf8mb4',
            'autocommit': False,
            'sql_mode': 'TRADITIONAL'
        }
    }
    
    # Configuración específica para entorno de producción
    if os.getenv('FLASK_ENV') == 'production':
        base_config.update({
            'pool_size': 20,             # Pool más grande para producción
            'max_overflow': 10,          # Más conexiones adicionales
            'pool_recycle': 1800,        # Reciclar cada 30 minutos
        })
    
    # Configuración para desarrollo
    elif os.getenv('FLASK_ENV') == 'development':
        base_config.update({
            'pool_size': 5,              # Pool más pequeño para desarrollo
            'max_overflow': 2,           # Menos conexiones adicionales
            'echo': True,                # Mostrar queries en desarrollo
        })
    
    return base_config


def setup_database_events():
    """
    Configura eventos de SQLAlchemy para monitoreo y optimización
    """
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """
        Configura parámetros específicos para la conexión
        """
        if 'mysql' in str(dbapi_connection):
            # Configuraciones específicas para MySQL
            cursor = dbapi_connection.cursor()
            cursor.execute("SET SESSION sql_mode = 'TRADITIONAL'")
            cursor.execute("SET SESSION innodb_lock_wait_timeout = 50")
            cursor.close()
    
    @event.listens_for(Engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """
        Log de queries lentas (opcional, para debugging)
        """
        # Solo en desarrollo, log queries que tomen más de 1 segundo
        if os.getenv('FLASK_ENV') == 'development':
            context._query_start_time = time.time()
    
    @event.listens_for(Engine, "after_cursor_execute")
    def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """
        Log de queries lentas (opcional, para debugging)
        """
        if os.getenv('FLASK_ENV') == 'development' and hasattr(context, '_query_start_time'):
            total = time.time() - context._query_start_time
            if total > 1.0:  # Queries que toman más de 1 segundo
                logging.warning(f"SLOW QUERY ({total:.2f}s): {statement[:100]}...")


def get_database_uri():
    """
    Construye la URI de la base de datos con configuración optimizada
    """
    mysql_uri = os.getenv('DATABASE_URL', 'mysql://root:uCjcqBcpUrryejQBqQsTXjHjtgBtGFXx@gondola.proxy.rlwy.net:49855/railway')
    
    # Si la URL de MySQL no tiene el formato correcto, construirla
    if not mysql_uri.startswith('mysql://'):
        mysql_uri = 'mysql://root:uCjcqBcpUrryejQBqQsTXjHjtgBtGFXx@gondola.proxy.rlwy.net:49855/railway'
    
    # Forzar el uso de PyMySQL en lugar de MySQLdb
    if mysql_uri.startswith('mysql://'):
        mysql_uri = mysql_uri.replace('mysql://', 'mysql+pymysql://', 1)
    
    # Agregar parámetros de conexión optimizados
    if '?' not in mysql_uri:
        mysql_uri += '?charset=utf8mb4&autocommit=false'
    else:
        mysql_uri += '&charset=utf8mb4&autocommit=false'
    
    return mysql_uri
