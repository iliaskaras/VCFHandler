from application.authentication.services import GetAccessTokenService
from application.authentication.validators import JwtIdentityValidator
from application.infrastructure.configurations.models import Configuration


def get_access_token_service() -> GetAccessTokenService:
    return GetAccessTokenService(
        jwt_identity_validator=jwt_identity_validator(),
        configuration=Configuration.get_instance()
    )


def jwt_identity_validator() -> JwtIdentityValidator:
    return JwtIdentityValidator()
