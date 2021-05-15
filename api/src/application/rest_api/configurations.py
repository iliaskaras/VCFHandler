from typing import Dict, Union, List

from flask_restplus import Api

from application.infrastructure.logging.loggers import LOGGER
from application.rest_api.errors import PublicHttpError


def configure_api_error_handling(api: Api) -> None:
    @api.errorhandler(PublicHttpError)
    def http_error_handler(error: PublicHttpError) -> Dict[str, Union[List[Dict[str, str]], int]]:
        LOGGER.exception(error)

        return {
            'errors': [_error.dump() for _error in error.errors],
            'errorCode': error.ERROR_CODE
        }
