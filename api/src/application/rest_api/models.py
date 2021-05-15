from attr import attrs, attrib

from application.infrastructure.error.errors import VCFHandlerBaseError
from application.rest_api.errors import PublicHttpError


@attrs
class BaseToHttpErrorPair:
    vcf_handler_base_error = attrib(type=VCFHandlerBaseError)
    public_error = attrib(type=PublicHttpError)
