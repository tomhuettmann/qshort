import bcrypt
# noinspection PyProtectedMember
from flask_restful import request, Resource
# noinspection PyUnresolvedReferences,PyPackageRequirements
from helpers.Logger import bind_logging
# noinspection PyUnresolvedReferences,PyPackageRequirements
from helpers.MongoCollection import col
# noinspection PyUnresolvedReferences,PyPackageRequirements
from helpers.RequestParser import parser


class Validation(Resource):
    @staticmethod
    def post():
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
