from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from application.infrastructure.sql.sql_base import base
from application.user.enums import Permission


class User(base):
    # Named Users because Postgresql does not allow us to create a Table named User
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    permission = Column(Enum(Permission, name='Permission', validate_strings=True), nullable=False)
