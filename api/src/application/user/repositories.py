from typing import Optional

from application.infrastructure.error.errors import InvalidArgumentError
from application.infrastructure.sql.sqlalchemy import (
    SQLAlchemySessionWrapper,
    SQLAlchemyEngineWrapper,
)
from application.user.models import User


class UserRepository:
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieves a User that belongs to the specified User by email.

        :param email: The email of the User.

        :return: The User or None if the User does not exist.

        :raise InvalidArgumentError: If email is None.
        """

        if not email:
            raise InvalidArgumentError("The email is required.")

        with SQLAlchemySessionWrapper(
            commit_on_exit=False,
            sql_alchemy_engine_wrapper=SQLAlchemyEngineWrapper.get_instance(),
        ) as session:
            return session.query(User).filter(User.email == email).first()
