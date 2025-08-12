from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from sqlalchemy import or_
from ..models import UserModel
from .. import db  # Asegúrate de importar la instancia de SQLAlchemy

def role_required(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                jwt = get_jwt()
                
                # Verificar el rol en los claims del token
                if not isinstance(roles, list):
                    roles_list = [roles]
                else:
                    roles_list = roles
                
                if 'rol' not in jwt:
                    return {"msg": "Rol no especificado en el token"}, 403
                    
                if jwt['rol'] not in roles_list:
                    return {"msg": f"Rol {jwt['rol']} no autorizado. Roles permitidos: {roles_list}"}, 403
                
                return func(*args, **kwargs)
            except Exception as e:
                return {"msg": f"Error de autenticación: {str(e)}"}, 401
        return wrapper
    return decorator
