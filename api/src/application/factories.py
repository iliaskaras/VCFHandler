from flask import Blueprint, Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from application.authentication.configurations import configure_jwt_manager
from application.infrastructure.configurations.models import Configuration
from application.infrastructure.error.errors import InvalidArgumentError
from application.infrastructure.logging.loggers import LOGGER
from application.rest_api.configurations import configure_api_error_handling
from application.rest_api.authentication.controllers import (
    ns as authentication_namespace,
)

from application.infrastructure.sql.sqlalchemy import SQLAlchemyEngineWrapper
from application.rest_api.rest_plus import api


def vcf_handler_api(name: str, configuration: Configuration) -> Flask:
    """
    The Flask Application Factory for the VCF Handler API.
    Initializes and returns the VCF Handler Flask application.

    @:param name: The name of the Flask application.
    @:param configuration: The configuration of the Flask application.

    @return: The VCF Handler Flask application.
    """
    if not configuration:
        raise InvalidArgumentError("The application configuration is required.")

    if not name:
        raise InvalidArgumentError("The application name is required.")

    # Initialize the SQLAlchemyEngineWrapper. It is a Singleton object and can be referenced
    # from the rest of the application when needed by using its get_instance method.
    SQLAlchemyEngineWrapper(uri=configuration.postgresql_connection_uri)

    # Initialize the Flask application.
    flask_application = Flask(name)

    # Disable Flask application error message handling, all the handling will be done from the endpoints.
    flask_application.config["ERROR_INCLUDE_MESSAGE"] = False

    # Set the JWT_SECRET_KEY for the symmetric algorithm "HS256"
    flask_application.config["JWT_SECRET_KEY"] = configuration.jwt_secret_key
    # flask_application.config["DEBUG"] = configuration.debug

    CORS(
        app=flask_application,
        origins="*",
        allow_headers=[
            "Content-Type",
            "Authorization"
        ],
    )

    # Configuration the JWT.
    jwt = JWTManager()
    jwt.init_app(flask_application)
    # Set a callback to be called when a client accessing a protected endpoint.
    configure_jwt_manager(jwt)

    # Configure the REST API endpoints.
    blueprint = Blueprint("api", name, url_prefix="/api/v1")

    api.add_namespace(authentication_namespace)
    configure_api_error_handling(api)
    api.init_app(blueprint)

    flask_application.register_blueprint(blueprint)

    LOGGER.info("VCF Handler REST API started.")

    return flask_application
