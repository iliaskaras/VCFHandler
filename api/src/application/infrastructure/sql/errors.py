from application.infrastructure.error.errors import VCFHandlerBaseError


class SQLError(VCFHandlerBaseError):
    message = "SQL error."
    error_type = "SQLError"


class SQLAlchemyEngineNotInitializedError(SQLError):
    message = "Not initialized SQLAlchemy Engine."
    error_type = "SQLAlchemyEngineNotInitializedError"
