from attr import attrs, attrib
from bson import ObjectId


@attrs
class JwtIdentity:
    user_id = attrib(type=str, default=None)
    user_permission = attrib(type=str, default=None)


@attrs
class JwtIdentityUser:
    id = attrib(type=ObjectId, default=None)
    permission = attrib(type=str, default=None)


@attrs
class Jwt:
    access_token = attrib(type=str)
