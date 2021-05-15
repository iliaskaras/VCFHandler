from application.authentication.models import JwtIdentity
from application.infrastructure.error.errors import NoneArgumentError, ValidationError


class JwtIdentityValidator:
    def validate(self, jwt_identity: JwtIdentity) -> None:
        """
        Jwt Identity validator that verifies the correctness of the provided JwtIdentity.

        :param jwt_identity: The JwtIdentity.

        :raise NoneArgumentError: If the JwtIdentity is not provided.
               ValidationError: If the User Id is not included in the JwtIdentity.
        """
        if jwt_identity is None:
            raise NoneArgumentError("A JWT identity is required.")

        if not jwt_identity.user_id:
            raise ValidationError("User id for the JWT identity is required.")

        if not jwt_identity.user_permission:
            raise ValidationError("User role for the JWT identity is required.")
