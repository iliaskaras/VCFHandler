from application.authentication.errors import AuthorizationError
from application.authentication.models import JwtIdentity, Jwt
from application.authentication.services import GetAccessTokenService
from application.infrastructure.error.errors import InvalidArgumentError
from application.user.repositories import UserRepository


class LoginUserService:
    def __init__(
            self,
            create_access_token_service: GetAccessTokenService,
            user_repository: UserRepository,
    ) -> None:
        self.create_access_token_service = create_access_token_service
        self.user_repository = user_repository

    def apply(self, email: str = None, password: str = None) -> Jwt:
        """
        Login Service handles the client authentication and returns the Jwt
        in case of success.

        :param email: The User email.
        :param password: The User password.

        :return: The Jwt with the access token.

        :raise InvalidArgumentError: If either the email or password is not provided.
        """
        if email is None:
            raise InvalidArgumentError("User email is required.")
        if password is None:
            raise InvalidArgumentError("User password is required.")

        user = self.user_repository.get_by_email(email)

        if user is None:
            raise AuthorizationError("User does not exist.")

        return Jwt(
            access_token=self.create_access_token_service.apply(
                JwtIdentity(
                    user_id=str(user.id),
                    user_permission=user.permission.value
                )
            )
        )
