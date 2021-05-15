from application.infrastructure.error.errors import VCFHandlerBaseError


class AuthenticationError(VCFHandlerBaseError):
    message = 'Authentication Error.'
    error_type = 'AuthenticationError'


class AuthorizationError(VCFHandlerBaseError):
    message = 'Authorization error.'
    error_type = 'AuthorizationError'
