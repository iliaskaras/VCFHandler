from datetime import timedelta

from flask_jwt_extended import create_access_token

from application.authentication.models import JwtIdentity
from application.authentication.validators import JwtIdentityValidator
from application.infrastructure.configurations.models import Configuration
from application.infrastructure.error.errors import InvalidArgumentError


class GetAccessTokenService:
    def __init__(
            self,
            jwt_identity_validator: JwtIdentityValidator,
            configuration: Configuration
    ) -> None:
        self.jwt_identity_validator = jwt_identity_validator
        self.configuration = configuration

    def apply(self, jwt_identity: JwtIdentity) -> str:
        """
        Validates the correctness of the JwtIdentity and creates, returns an Access Token.

        :param jwt_identity: The JWT Identity object which contains all the JWT attributes.

        :return: The access token.

        :raise InvalidArgumentError: If the jwt identity is not provided.
        """
        if jwt_identity is None:
            raise InvalidArgumentError("The jwt identity is required.")

        self.jwt_identity_validator.validate(jwt_identity)

        return create_access_token(
            identity=jwt_identity.__dict__,
            expires_delta=timedelta(
                seconds=self.configuration.jwt_expiration
            ),
            # Due to authentication, we return a fresh access token.
            fresh=True,
        )
