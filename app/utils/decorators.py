from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from ..models import UserModel


# def owner_required(fn):
#     @wraps(fn) # This is used to preserve the original function name
#     def owner_required_wrapper(*args, **kwargs):
#         # Check if the user is the owner of the resource
#         verify_jwt_in_request()
#         # Get the claims of the JWT
#         claims = get_jwt()
#         if claims['rol'] == 'owner':
#             return fn(*args, **kwargs)
#         else:
#             return 'Only admins can access', 403
#     return owner_required_wrapper




# def driver_required(fn):
#     @wraps(fn)
#     def driver_required_wrapper(*args, **kwargs):
       
#        user_id = get_jwt_identity()
#        #obtener el ID de truck 
#        truck_id = kwargs.get('id')
#        driver = DriverModel.query.filter_by(user_id=user_id, truck_id=truck_id).first()
       
#        if driver:
#            return fn(*args, **kwargs)
#        else:
#            return {'message': 'You do not have permission to modify this truck'}, 403
#     return driver_required_wrapper



def role_required(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            current_user = UserModel.query.get(current_user_id)
            if current_user.rol not in roles:
                return {'message': 'You do not have permission'}, 403
            return func(*args, **kwargs)
        return wrapper
    return decorator
