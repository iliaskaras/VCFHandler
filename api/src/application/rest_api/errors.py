from typing import List, Dict

from attr import attrs, attrib


@attrs
class Error:
    message = attrib(type=str, default=None)
    error_type = attrib(type=str, default=None)

    def dump(self) -> Dict[str, str]:
        return {
            'message': self.message,
            'errorType': self.error_type
        }


class PublicHttpError(Exception):
    ERROR_CODE = None

    def __init__(self, errors: List[Error] = None):
        if errors:
            self.errors = errors
        else:
            self.errors: List[Error] = []


class BadRequestHttpError(PublicHttpError):
    ERROR_CODE = 400


class AuthenticationHttpError(PublicHttpError):
    ERROR_CODE = 401


class AuthorizationHttpError(PublicHttpError):
    ERROR_CODE = 403


class InternalServerHttpError(PublicHttpError):
    ERROR_CODE = 500
