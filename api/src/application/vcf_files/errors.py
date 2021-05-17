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


class VcfDataUpdateError(ValidationError):
    message = "Vcf Data Update Error."
    error_type = "VcfDataUpdateError"


class VcfNoDataDeletedError(ValidationError):
    message = "Vcf Data Delete Error."
    error_type = "VcfDataDeleteError"
