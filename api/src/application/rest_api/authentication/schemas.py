from marshmallow import fields
from marshmallow.schema import BaseSchema


class UserCredentialsRequestSchema(BaseSchema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)


class AccessTokenResponseSchema(BaseSchema):
    access_token = fields.Str(dump_to="accessToken")
