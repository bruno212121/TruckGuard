from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from sqlalchemy import or_
from ..models import UserModel
from .. import db
from werkzeug.exceptions import HTTPException

def role_required(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                
                # Convertir la identidad a entero si es string
                if isinstance(current_user_id, str):
                    current_user_id = int(current_user_id)
                
                # Obtener el usuario de la base de datos
                user = UserModel.query.get(current_user_id)
                if not user:
                    return {"msg": "Usuario no encontrado"}, 404
                
                # Verificar el rol del usuario
                if not isinstance(roles, list):
                    roles_list = [roles]
                else:
                    roles_list = roles
                
                if user.rol not in roles_list:
                    return {"msg": f"Rol {user.rol} no autorizado. Roles permitidos: {roles_list}"}, 403
                
                return func(*args, **kwargs)
            except HTTPException:
                # Re-lanzar excepciones HTTP (como 404) sin modificarlas
                raise
            except Exception as e:
                return {"msg": f"Error de autenticación: {str(e)}"}, 401
        return wrapper
    return decorator
