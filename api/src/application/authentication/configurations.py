from typing import Any, Dict

from flask_jwt_extended import JWTManager

from application.authentication.models import JwtIdentityUser
from application.infrastructure.error.errors import ValidationError


def configure_jwt_manager(jwt: JWTManager) -> None:
    @jwt.user_loader_callback_loader
    def get_jwt_user_from_jwt_identity(identity_jwt: Dict[str, Any]) -> JwtIdentityUser:
        """
        Maps and returns the JwtUser automatically when a client tries to access a protected endpoint.

        :param identity_jwt: The dictionary that represents the Identity JWT.

        :return: The mapped JwtUser.

        :raise ValidationError: When the identity do not include the user_id.
        """
        if not identity_jwt.get("user_id"):
            raise ValidationError("User id in jwt is required.")
        if not identity_jwt.get("user_permission"):
            raise ValidationError("User permission in jwt is required.")

        return JwtIdentityUser(
            id=identity_jwt["user_id"],
            permission=identity_jwt["user_permission"]
        )
