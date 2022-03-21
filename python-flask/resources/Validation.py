import bcrypt
from flask_apispec import MethodResource, doc, use_kwargs, marshal_with
from flask_restful import request
# noinspection PyUnresolvedReferences,PyPackageRequirements
from helpers.Logger import bind_logging
# noinspection PyUnresolvedReferences,PyPackageRequirements
from helpers.MongoCollection import col
# noinspection PyUnresolvedReferences,PyPackageRequirements
from helpers.RequestParser import parser

# noinspection PyMethodMayBeStatic
from marshmallow import fields, Schema


# noinspection PyUnusedLocal
class Validation(MethodResource):
    @doc(description="Post endpoint for validating path with password or master key", tags=["validation"])
    @use_kwargs(
        {
            "path": fields.Str(description="The shortened path which should be validated. "
                                           "Example: 9adu2"),
            "password": fields.Str(description="The password to validate the path. "
                                               "Example: test123"),
            "master_key": fields.Str(description="The master key to validate the path. "
                                                 "Example: 1yYLJutiadpgLkVuT6yysMfSxg7NigTY")
        },
        location="query")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="Verified")
        }
    ), code=200, description="The given path successfully validated with given password or master key")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="Required path parameter is not given")
        }
    ), code=400, description="The required path parameter is missing")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="Path and password and master key doesn't match")
        }
    ), code=401, description="The given path is not validated with given password or master key")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="No link found for path")
        }
    ), code=404, description="There is no link stored matching the given path")
    def post(self, **kwargs):
        log = bind_logging(request)

        args = parser.parse_args()
        path: str = args["path"]
        password: str = args["password"]
        master_key: str = args["masterKey"]

        if not path:
            log.warning("Required parameter path is missing")
            return {
                       "message": "Required path parameter is not given"
                   }, 400

        entry = col.find_one({"path": path})
        if not entry:
            log.warning("No entry found for given path: " + path)
            return {
                       "message": "No link found for path"
                   }, 404

        if entry:
            if password and not master_key and bcrypt.checkpw(str.encode(password), entry["password"]):
                log.info("Successfully verified path: " + path + " with the password")
                return {
                           "message": "Verified"
                       }, 200

            if master_key and not password and bcrypt.checkpw(str.encode(master_key), entry["masterKey"]):
                log.info("Successfully verified path: " + path + " with the master key")
                return {
                           "message": "Verified"
                       }, 200

            if master_key and password and bcrypt.checkpw(str.encode(password), entry["password"]) and bcrypt.checkpw(
                    str.encode(master_key), entry["masterKey"]):
                log.info("Successfully verified path: " + path + " with password and master key")
                return {
                           "message": "Verified"
                       }, 200

        if password and master_key:
            log.warning("Verification of path: " + path + " with master key and password failed")
            return {
                       "message": "Path and password and master key doesn't match"
                   }, 401

        if password:
            log.warning("Verification of path: " + path + " with password failed")
            return {
                       "message": "Password doesn't match with path"
                   }, 401

        if master_key:
            log.warning("Verification of path: " + path + " with master key failed")
            return {
                       "message": "Master key doesn't match with path"
                   }, 401

        log.warning("Verification of path: " + path + " failed because of missing password or master key")
        return {
                   "message": "Password or master key is missing for verification with path"
               }, 401
