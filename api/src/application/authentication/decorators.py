from typing import Callable, Any

from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from application.authentication.errors import AuthorizationError
from application.authentication.models import JwtIdentity
from application.user.enums import Permission


def guard(permission: Permission = None) -> Callable:
    """
    A guard decorator to filter requests from unauthorized clients.

    @:param permission: The permission that guard the endpoint.
    """
    def decorator(func: Callable) -> Callable:

        def wrapper(*args: Any, **kwargs: Any) -> Callable:
            """
            Verifies the jwt identity in the request, using our custom jwt identity verification
            process: configure_jwt_manager callback.

            Verifies if the client user have the correct permission to proceed.
            """
            verify_jwt_in_request()

            jwt_identity: JwtIdentity = JwtIdentity(**get_jwt_identity())

            if permission.value != jwt_identity.user_permission:
                raise AuthorizationError('Permission denied.')

            return func(*args, **kwargs)

        return wrapper

    return decorator
