from typing import List

from application.rest_api.errors import Error


class VCFHandlerBaseError(Exception):
    message = "BaseError"
    error_type = "VCFHandlerBaseError"

    def __init__(self, message: str = None, error_type: str = None):
        if message:
            self.message = message

        if error_type:
            self.error_type = error_type

    def get_mapped_errors(self) -> List[Error]:
        """
        Map the VCFHandlerBaseError to Error. Returning a List instead of a single Error for
        handling the errors with the same logic as when we have MultipleVCFHandlerBaseErrors.

        :return: The mapped Error.
        """
        return [Error(message=self.message, error_type=self.error_type)]


class MultipleVCFHandlerBaseError(VCFHandlerBaseError):
    """
    A wrapper of VCFHandlerBaseErrors, that handles cases where we want to have more than one errors
    to be handled on the failure.
    """
    def __init__(self):
        self.errors: List[VCFHandlerBaseError] = []

    def append(self, error: VCFHandlerBaseError) -> None:
        """
        Appends a VCFHandlerBaseError into the list of errors.

        :param error: The VCFHandlerBaseError to append.
        """
        self.errors.append(error)

    def get_mapped_errors(self) -> List[Error]:
        """
        :return: The list of Error from the list of errors.
        """
        errors: List[Error] = []
        for error in self.errors:
            errors.extend(error.get_mapped_errors())

        return errors


class ArgumentError(VCFHandlerBaseError):
    message = "Argument error."
    error_type = "ArgumentError"


class InvalidArgumentError(ArgumentError):
    message = "Invalid argument error."
    error_type = "InvalidArgumentError"


class NoneArgumentError(ArgumentError):
    message = "Missing argument error."
    error_type = "MissingArgumentError"


class ValidationError(InvalidArgumentError):
    message = "Validation error."
    error_type = "ValidationError"
