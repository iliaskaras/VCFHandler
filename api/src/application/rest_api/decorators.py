import json
from typing import Any, Callable, List

import flask
from flask import Response, make_response, request
from flask_jwt_extended.exceptions import NoAuthorizationError
from json2xml.utils import readfromstring
from marshmallow import Schema
from webargs.flaskparser import use_kwargs
from werkzeug.exceptions import UnprocessableEntity

from application.authentication.errors import AuthorizationError, AuthenticationError
from application.infrastructure.error.errors import VCFHandlerBaseError, MultipleVCFHandlerBaseError, ArgumentError
from application.rest_api.enums import AcceptHeader
from application.rest_api.errors import NotFoundHttpError, BadRequestHttpError, \
    AuthenticationHttpError, InternalServerHttpError, Error, AuthorizationHttpError
from application.rest_api.models import BaseToHttpErrorPair
from json2xml import json2xml

from application.rest_api.utils import ETagManager
from application.vcf_files.errors import VcfRowsByIdNotExistError, VcfDataAppendError, VcfNoDataDeletedError, \
    VcfDataDeleteError


def map_request(schema: Schema) -> Callable:
    """
    Parses the request body by a provided Marshmallow Schema.

    :param schema: The Marshmallow Schema to check the validity of the request provided attributes.
    """

    def decorator(func: Callable) -> Callable:
        # Validates the provided by client request body to the Marshmallow Schema.
        @use_kwargs(schema)
        def wrapper(*args: Any, **kwargs: Any) -> Response:
            # In case the request body passed the Marshmallow validation, but a field is not provided.
            # In that case we set it to None and let Service handle the InvalidArgumentError.
            for expected_field in schema.fields:
                if expected_field not in kwargs:
                    kwargs[expected_field] = None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def check_etag() -> Callable:
    """
    Checks the ETag header of the request.
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Response:

            etag = ETagManager.generate_etag(with_quotes=True, **kwargs)

            if_none_match = request.headers.get('If-None-Match')

            if etag == if_none_match:

                response = make_response()
                response.status_code = 304

                return response

            return func(*args, **kwargs)

        return wrapper

    return decorator


def add_etag(
        add_etag: bool = False
) -> Callable:
    """
    Adds an ETag Header of the request parameters to the response.

    :param add_etag: If we want to add an Etag. If so, we are adding the request parameters.

    :return: The Response with the ETag added.
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Response:
            response: Response = func(*args, **kwargs)

            if add_etag:
                etag = ETagManager.generate_etag(with_quotes=False, **kwargs)

                response.set_etag(etag)

            return response.make_conditional(request)

        return wrapper

    return decorator


def map_response(
        schema: Schema = None,
        entity_name: str = None,
        status_code: int = 200,
) -> Callable:
    """
    Maps the Service response using a provided Marshmallow Schema, and finally create and returns
    the final Envelope Response.

    The Envelope Response format defaults to JSON, but if the use use 'application/xml' Accept header, then
    the json envelope response will be mapped to its xml version.

    The Envelope Response has the following format:
    {
        <entity-name>: <result>.
        status: 200
    }

    :param schema: The Marshmallow Schema to map the returned service result.
    :param entity_name: The entity name (optional) to map the mapped result into the endpoint return envelope.
    :param status_code: The status code, defaults to 200.

    :return: The Envelope Response.
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Response:
            result = func(*args, **kwargs)

            response_type = flask.request.headers.environ['HTTP_ACCEPT']

            if schema:
                result = schema.dump(result)

            if entity_name:
                response_body = {entity_name: result}
            else:
                response_body = result

            enveloped_response = {"status": status_code, "data": response_body}

            if response_type == AcceptHeader.xml.value:
                json_object: str = json.dumps(enveloped_response)
                enveloped_response = json2xml.Json2xml(readfromstring(json_object)).to_xml()
            # The enveloped_response is passed through the flask.jsonify method automatically by Flask.
            response = make_response(enveloped_response, status_code)

            return response

        return wrapper

    return decorator


def map_errors() -> Callable:
    return map_base_errors_to_public(
        base_to_public_error_maps=[
            BaseToHttpErrorPair(
                vcf_handler_base_error=VcfRowsByIdNotExistError(),
                public_error=NotFoundHttpError(),
            ),
            BaseToHttpErrorPair(
                vcf_handler_base_error=AuthorizationError(),
                public_error=AuthorizationHttpError(),
            ),
            BaseToHttpErrorPair(
                vcf_handler_base_error=VcfDataAppendError(),
                public_error=BadRequestHttpError(),
            ),
            BaseToHttpErrorPair(
                vcf_handler_base_error=VcfDataDeleteError(),
                public_error=BadRequestHttpError(),
            ),
            BaseToHttpErrorPair(
                vcf_handler_base_error=VcfNoDataDeletedError(),
                public_error=NotFoundHttpError(),
            ),
        ],
    )


def map_base_errors_to_public(
        base_to_public_error_maps: List[BaseToHttpErrorPair] = None,
) -> Callable:
    """
    A decorator to be used to a Controller.

    It maps the internal application errors (e.g. UserError) to HttpErrors. The HttpErrors are then handled by Flask.

    Note: This decorator should be the first to be applied on a Controller.
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Response:

            try:
                return func(*args, **kwargs)

            # werkzeug.exceptions.UnprocessableEntity raised when Marshmallow raises Validation errors.
            except UnprocessableEntity as ex:
                if hasattr(ex, 'exc'):
                    errors: List[Error] = [
                        Error(
                            message='{0}: {1}'.format(error_attribute, error_message),
                            error_type=ex.name
                        )
                        for error_attribute, error_message in ex.exc.messages.items()
                    ]
                    raise BadRequestHttpError(
                        errors=errors
                    )
                else:
                    raise BadRequestHttpError()
            except VCFHandlerBaseError as ex:

                if base_to_public_error_maps:
                    for base_to_public_error in base_to_public_error_maps:
                        if isinstance(ex, type(base_to_public_error.vcf_handler_base_error)):
                            public_error = base_to_public_error.public_error
                            public_error.errors = ex.get_mapped_errors()
                            raise public_error

                if isinstance(ex, AuthorizationError):
                    raise NotFoundHttpError(errors=ex.get_mapped_errors())
                if isinstance(ex, AuthenticationError):
                    raise AuthenticationHttpError(errors=ex.get_mapped_errors())
                if isinstance(ex, ArgumentError):
                    raise BadRequestHttpError(errors=ex.get_mapped_errors())
                if isinstance(ex, MultipleVCFHandlerBaseError):
                    raise BadRequestHttpError(errors=ex.get_mapped_errors())

                # In case we haven't mapped the Base Exception to any Public Error.
                raise InternalServerHttpError()
            except NoAuthorizationError as ex:
                raise AuthorizationHttpError([Error(message=str(ex.args[0]), error_type=403)])
            except Exception:
                raise InternalServerHttpError()

        return wrapper

    return decorator
