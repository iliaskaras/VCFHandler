from types import TracebackType
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from application.infrastructure.error.errors import (
    InvalidArgumentError,
    ValidationError,
)
from application.infrastructure.sql.errors import SQLAlchemyEngineNotInitializedError


from application.infrastructure.sql.sql_base import base


class SQLAlchemyEngineWrapper:
    """
    The wrapper class that contains the SQLAlchemy Engine.

    Each instance of this class, can initialize and dispose a separate SQLAlchemy Engine.
    """

    SQL_ALCHEMY_ENGINE: Engine = None
    SQL_ALCHEMY_SESSION_MAKER: sessionmaker = None

    Base: declarative_base = base

    __instance = None

    @staticmethod
    def get_instance(
            uri: Optional[str] = None
    ) -> "SQLAlchemyEngineWrapper":
        """

        :param uri: The Database connection URI.

        :return:
        """
        if SQLAlchemyEngineWrapper.__instance is None:
            SQLAlchemyEngineWrapper(uri=uri)
        return SQLAlchemyEngineWrapper.__instance

    def __init__(self, uri: str):
        if SQLAlchemyEngineWrapper.__instance is not None:
            raise ValidationError("SQLAlchemyEngineWrapper is singleton")
        else:
            # Initialize the Alchemy Engine and sessionmaker
            self.initialize(uri=uri)
            SQLAlchemyEngineWrapper.__instance = self

    @classmethod
    def initialize(cls, uri: str) -> Engine:
        """
        Initializes the SQLAlchemy Engine.

        :param uri: The URI of the database to connect to.

        :return: The Engine instance.

        :raise InvalidArgumentError: If the URI is not provided.
        """

        if not uri:
            raise InvalidArgumentError("The uri is required.")

        if not cls.SQL_ALCHEMY_ENGINE:
            cls.SQL_ALCHEMY_ENGINE = create_engine(uri, echo=False)

        if not cls.SQL_ALCHEMY_SESSION_MAKER and cls.SQL_ALCHEMY_ENGINE:
            cls.SQL_ALCHEMY_SESSION_MAKER = sessionmaker(bind=cls.SQL_ALCHEMY_ENGINE)

        return cls.SQL_ALCHEMY_ENGINE

    @classmethod
    def get_engine(cls) -> Engine:
        """
        Returns the SQLAlchemy Engine.

        :return: The SQLAlchemy Engine instance.

        :raise SQLAlchemyEngineNotInitializedError: If the engine failed to be created at the constructor.
        """

        if not cls.SQL_ALCHEMY_ENGINE:
            raise SQLAlchemyEngineNotInitializedError(
                "SQLAlchemyEngine has not been initialized."
            )

        return cls.SQL_ALCHEMY_ENGINE

    @classmethod
    def create_session(cls) -> Session:
        """
        Initializes the SQLAlchemy Session instance.

        :return: The SQLAlchemy Session instance created.

        :raise SQLAlchemyEngineNotInitializedError: If `initialize` has not been called before calling this method.
        """

        if not cls.SQL_ALCHEMY_ENGINE or not cls.SQL_ALCHEMY_SESSION_MAKER:
            raise SQLAlchemyEngineNotInitializedError(
                "SQLAlchemyEngine has not been initialized."
            )

        # This will invoke the sessionmaker.__call__() that will create a session
        return cls.SQL_ALCHEMY_SESSION_MAKER()

    @classmethod
    def close(cls) -> None:
        """
        Closes the SQLAlchemy Engine instance.
        """

        if cls.SQL_ALCHEMY_ENGINE:
            cls.SQL_ALCHEMY_ENGINE.dispose()


class SQLAlchemySessionWrapper:
    """
    A ContextManager that provides an SQLAlchemy Session on an SQL database.
    """

    def __init__(
            self,
            sql_alchemy_engine_wrapper: SQLAlchemyEngineWrapper,
            commit_on_exit: bool = True,
    ):
        """
        ContextManager that provides an SQLAlchemy Session on an SQL database.

        :param sql_alchemy_engine_wrapper: The SQLAlchemyEngineWrapper instance to use for generating the Session.
        :param commit_on_exit: Whether to commit the session on exit.
        """

        self.sql_alchemy_engine_wrapper = sql_alchemy_engine_wrapper

        self.commit_on_exit = commit_on_exit

    def __enter__(self) -> Session:
        self.session: Session = self.sql_alchemy_engine_wrapper.create_session()

        return self.session

    def __exit__(
            self, exception_type: type, exception_value: Exception, traceback: TracebackType
    ) -> None:
        if exception_value:
            # If an exception has occurred, rollback the session.
            self.session.rollback()
        else:
            if self.commit_on_exit:
                self.session.commit()

        self.session.close()
