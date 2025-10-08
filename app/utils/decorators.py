from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_restx import abort
from ..models import UserModel
from .. import db

def role_required(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Verificar JWT
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                
                # Convertir a entero si es string
                if isinstance(current_user_id, str):
                    current_user_id = int(current_user_id)
                
                # Obtener usuario
                user = UserModel.query.get(current_user_id)
                if not user:
                    abort(404, message="Usuario no encontrado")
                
                # Verificar roles
                if not isinstance(roles, list):
                    roles_list = [roles]
                else:
                    roles_list = roles
                
                if user.rol not in roles_list:
                    abort(403, message=f"Rol {user.rol} no autorizado. Roles permitidos: {roles_list}")
                
                # Si todo está bien, ejecutar la función
                return func(*args, **kwargs)
                
            except Exception as e:
                # Solo capturar excepciones específicas, no todas
                if "JWT" in str(e) or "token" in str(e).lower():
                    abort(401, message=f"Error de autenticación: {str(e)}")
                else:
                    # Re-lanzar otras excepciones para que se manejen apropiadamente
                    raise e
                
        return wrapper
    return decorator


def db_session_management(func):
    """
    Decorador para manejo automático de sesiones de base de datos.
    Asegura que las sesiones se cierren correctamente después de cada operación.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Ejecutar la función
            result = func(*args, **kwargs)
            
            # Si todo salió bien, hacer commit
            db.session.commit()
            return result
            
        except Exception as e:
            # En caso de error, hacer rollback
            db.session.rollback()
            raise e
            
        finally:
            # Siempre cerrar la sesión para liberar la conexión del pool
            db.session.remove()
            
    return wrapper


def db_transaction(func):
    """
    Decorador para manejo de transacciones de base de datos.
    Útil para operaciones que requieren múltiples cambios atómicos.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Ejecutar la función dentro de una transacción
            result = func(*args, **kwargs)
            
            # Si todo salió bien, hacer commit
            db.session.commit()
            return result
            
        except Exception as e:
            # En caso de error, hacer rollback
            db.session.rollback()
            # Re-lanzar la excepción para que se maneje en el endpoint
            raise e
            
        finally:
            # Siempre cerrar la sesión para liberar la conexión del pool
            db.session.remove()
            
    return wrapper
