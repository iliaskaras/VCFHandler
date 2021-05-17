from application.infrastructure.error.errors import InvalidArgumentError


class VcfRowsByIdNotExistError(InvalidArgumentError):
    message = "Vcf Rows By Id Not Exist Error."
    error_type = "VcfRowsByIdNotExistError"
