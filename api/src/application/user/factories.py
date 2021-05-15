from application.authentication.factories import get_access_token_service
from application.user.repositories import UserRepository
from application.user.services import LoginUserService


def login_user_service() -> LoginUserService:
    return LoginUserService(
        user_repository=UserRepository(),
        create_access_token_service=get_access_token_service(),
    )
