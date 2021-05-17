from application.infrastructure.error.errors import ValidationError


class VcfRowsByIdNotExistError(ValidationError):
    message = "Vcf Rows By Id Not Exist Error."
    error_type = "VcfRowsByIdNotExistError"


class VcfDataAppendError(ValidationError):
    message = "Vcf Data Append Error."
    error_type = "VcfDataAppendError"


class VcfDataDeleteError(ValidationError):
    message = "Vcf Data Delete Error."
    error_type = "VcfDataDeleteError"


class VcfNoDataDeletedError(ValidationError):
    message = "Vcf Data Delete Error."
    error_type = "VcfDataDeleteError"
