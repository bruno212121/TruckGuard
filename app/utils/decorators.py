from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def owner_required(fn):
    @wraps(fn) # This is used to preserve the original function name
    def wrapper(*args, **kwargs):
        # Check if the user is the owner of the resource
        verify_jwt_in_request()
        # Get the claims of the JWT
        claims = get_jwt()
        if claims['rol'] == 'owner':
            return fn(*args, **kwargs)
        else:
            return 'Only admins can access', 403
    return wrapper








