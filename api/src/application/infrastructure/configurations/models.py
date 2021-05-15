import os

from application.infrastructure.configurations.enums import Environment
from application.infrastructure.configurations.errors import (
    ConfigurationNotInitializedError,
)
from application.infrastructure.error.errors import InvalidArgumentError

# The Environment Variable that holds to initialize the correct Configuration Environment.
ENV_VAR_NAME = "VCF_FILES_API_ENVIRONMENT"


class Configuration:
    """
    The Application global Configuration Instance. It is used throughout the application and
    is initialized at the Application initialization.

    @:var ENVIRONMENT: Holds the Environment ENUM.
    @:var INSTANCE: Holds the initialized Configuration instance.
    """

    ENVIRONMENT: Environment = None
    INSTANCE: "Configuration" = None

    def __init__(
        self,
        salt: str,
        postgresql_connection_uri: str,
        jwt_secret_key: str,
        jwt_expiration: int = 3600,
        debug: bool = False,
    ):
        if not salt:
            raise InvalidArgumentError("The salt is required.")
        if not postgresql_connection_uri:
            raise InvalidArgumentError("The PostgreSQL connection uri is required.")
        if not jwt_secret_key:
            raise InvalidArgumentError("The jwt secret key is required.")
        if not jwt_expiration:
            raise InvalidArgumentError("The jwt expiration is required.")
        if not isinstance(debug, bool):
            raise InvalidArgumentError("The Debug flag is not a boolean.")

        self.salt = salt
        self.postgresql_connection_uri = postgresql_connection_uri
        self.jwt_secret_key = jwt_secret_key
        self.jwt_expiration = jwt_expiration
        self.debug = debug

    @classmethod
    def initialize(cls) -> "Configuration":
        """
        Initializes the Configuration on the environment specified at 'VCF_FILES_API_ENVIRONMENT' environment variable.

        @:return The Configuration instance.
        """

        environment: str = os.getenv(ENV_VAR_NAME, None)
        if environment not in Environment.values():
            raise InvalidArgumentError(
                '"Please set your environment variable {} to a correct environment among: {}'.format(
                    ENV_VAR_NAME, Environment.values()
                )
            )

        cls.ENVIRONMENT = Environment[environment]

        return cls._set_instance(cls.ENVIRONMENT)

    @staticmethod
    def _set_instance(environment: Environment) -> "Configuration":
        """
        Sets the Configuration instance.

        @:param environment: The Application environment.

        @:return: The configuration instance.
        """

        if environment == Environment.local:
            Configuration.INSTANCE = Configuration._get_local_configuration()
        elif environment == Environment.test:
            Configuration.INSTANCE = Configuration._get_test_configuration()
        elif environment == Environment.production:
            Configuration.INSTANCE = Configuration._get_production_configuration()

        return Configuration.INSTANCE

    @staticmethod
    def get_instance() -> "Configuration":
        """
        Returns the initialized configuration instance.

        @:return: The initialized configuration instance.

        @:raise ConfigurationNotInitializedError: If the configuration has not been initialized.
        """

        if not Configuration.INSTANCE:
            raise ConfigurationNotInitializedError(
                "Configuration has not been initialized."
            )

        return Configuration.INSTANCE

    @staticmethod
    def _get_local_configuration() -> "Configuration":
        """
        Initializes and returns a local configuration instance.

        :return: The local configuration instance.
        """
        return Configuration(
            postgresql_connection_uri=os.getenv("POSTGRESQL_CONNECTION_URI"),
            jwt_secret_key=os.getenv("JWT_SECRET_KEY"),
            salt=os.getenv("SALT"),
            debug=True,
        )

    @staticmethod
    def _get_test_configuration() -> "Configuration":
        """
        Initializes and returns a test configuration instance.

        :return: The test configuration instance.
        """
        return Configuration(
            postgresql_connection_uri=os.getenv("POSTGRESQL_CONNECTION_URI"),
            jwt_secret_key=os.getenv("JWT_SECRET_KEY"),
            salt="test",
            debug=True,
        )

    @staticmethod
    def _get_production_configuration() -> "Configuration":
        """
        Initializes and returns a production configuration instance.

        :return: The production configuration instance.
        """
        return Configuration(
            postgresql_connection_uri=os.getenv("POSTGRESQL_CONNECTION_URI"),
            jwt_secret_key=os.getenv("JWT_SECRET_KEY"),
            salt=os.getenv("SALT"),
            debug=False,
        )
