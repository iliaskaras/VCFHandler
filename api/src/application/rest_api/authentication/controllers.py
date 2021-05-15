from flask_restplus import Resource

from application.rest_api.authentication.schemas import (
    UserCredentialsRequestSchema,
    AccessTokenResponseSchema,
)
from application.rest_api.decorators import map_request, map_response, map_errors
from application.rest_api.rest_plus import api
from application.user.factories import login_user_service

ns = api.namespace(
    "authentication", description="Access and security related endpoints."
)


@ns.route("/login")
class UserLogin(Resource):
    @map_errors()
    @map_request(UserCredentialsRequestSchema())
    @map_response(schema=AccessTokenResponseSchema(), entity_name="jwt")
    def post(self, email: str, password: str):
        """
        Controller for handling client requests for the Login operation.

        :param email: The User email.
        :param password: The User password.

        :return: The Jwt that contains the access token.
        """
        jwt = login_user_service().apply(email=email, password=password)
        return jwt
