import re
import string
from datetime import datetime

import bcrypt
from flask_apispec import MethodResource, doc, use_kwargs, marshal_with
from flask_restful import request
# noinspection PyUnresolvedReferences,PyPackageRequirements
from helpers.Logger import bind_logging
# noinspection PyUnresolvedReferences,PyPackageRequirements
from helpers.MongoCollection import col
# noinspection PyUnresolvedReferences,PyPackageRequirements
from helpers.RequestParser import parser
from marshmallow import fields, Schema
from nanoid import generate


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Shortened(MethodResource):
    @doc(description="Get endpoint for resolving data from path", tags=["url-shortening"])
    @use_kwargs(
        {
            "path": fields.Str(description="The shortened path which should be resolved. "
                                           "Example: 9adu2"),
            "password": fields.Str(description="The password to resolve protected paths. "
                                               "Example: test123")
        },
        location="query")
    @marshal_with(Schema().from_dict(
        {
            "path": fields.Str(example="9adu2"),
            "clicks": fields.Int(example="10"),
            "clickLimit": fields.Int(example="100"),
            "urls": fields.List(fields.Str(), example=["https://google.de, google.de"]),
            "date": fields.Str(example="None"),
            "created": fields.Str(example="2022-03-07 14:36:46.364000"),
            "edited": fields.Str(example="None"),
            "message": fields.Str(example="Got shortened url")
        }
    ), code=200, description="The given path and optional password successfully make resolving data possible")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="Required path parameter not set")
        }
    ), code=400, description="The required path parameter is missing")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="Password does not match")
        }
    ), code=401, description="The given password parameter does not enable authorization for the protected path to "
                             "resolve the data")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="No link found for path")
        }
    ), code=404, description="There is no link stored matching the given path")
    def get(self, **kwargs):
        log = bind_logging(request)
        args = parser.parse_args()
        path: str = args["path"]
        password: str = args["password"]

        if path is None:
            log.warning("Required path parameter is missing to get link")
            return {
                       "message": "Required path parameter not set"
                   }, 400

        entry = col.find_one({"path": path})
        if entry:
            if entry["password"]:
                if password is None:
                    log.warning("Required password parameter is missing to get path: " + path)
                    return {
                               "message": "Required password parameter not set"
                           }, 400
                elif not bcrypt.checkpw(str.encode(password), entry["password"]):
                    log.warning("Verification with password failed for path: " + path)
                    return {
                               "message": "Password does not match"
                           }, 401

            log.info("Successfully resolved path: " + path)
            return {
                       "path": entry["path"],
                       "clicks": entry["clicks"],
                       "clickLimit": entry["clickLimit"],
                       "urls": entry["urls"],
                       "date": str(entry["date"]),
                       "created": str(entry["created"]),
                       "edited": str(entry["created"]),
                       "message": "Got shortened url"
                   }, 200

        log.info("No link found for path: " + path)
        return {
                   "message": "No link found for path"
               }, 404

    @doc(description="Post endpoint for creating shortened link", tags=["url-shortening"])
    @use_kwargs(
        {
            "urls": fields.List(fields.Str(), description="The target urls of the shortened url. "
                                                          'Example: ["google.de", "https://google.de"]'),
            "password": fields.Str(description="The password to protect the shortened url. "
                                               "Example: test123"),
            "endDurationDate": fields.Str(description="The end duration until shortened url is valid. "
                                                      "Example: 22-01-01T13:37"),
            "wish": fields.Str(description="The desired path of the shortened url. "
                                           "Example: myFavoritePath"),
            "length": fields.Int(description="The desired length of the shortened url path. "
                                             "Example: 15"),
            "clickLimit": fields.Int(description="The amount of clicks until the shortened url is valid. "
                                                 "Example: 100")
        }, location="query")
    @marshal_with(Schema().from_dict(
        {
            "path": fields.Str(example="9adu2"),
            "urls": fields.List(fields.Str(), example=["https://google.de, google.de"]),
            "password": fields.Str(example="test123"),
            "date": fields.Str(example="25-12-31T13:37"),
            "masterKey": fields.Str(example="1yYLJutiadpgLkVuT6yysMfSxg7NigTY"),
            "message": fields.Str(example="Created shortened url")
        }
    ), code=201, description="There was successfully created a shortened url by the given parameters")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="Required urls parameter not set or not valid")
        }
    ), code=400, description="The required urls parameter is missing or does not contain valid urls")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="Wish already taken")
        }
    ), code=409, description="There exists already a shortened url with the same path as the desired given by wish "
                             "parameter")
    def post(self, **kwargs):
        log = bind_logging(request)

        args = parser.parse_args()
        urls: [str] = args["urls"]
        password: str = args["password"]
        date: str = args["endDurationDate"]
        wish: str = args["wish"]
        length: int = args["length"]
        size: int = length if length is not None else 5
        click_limit: int = args["clickLimit"]

        is_url = re.compile("(https?://)?[-a-zA-Z0-9@:%._+~#=]{2,256}\.[a-z]{2,6}[-a-zA-Z0-9@:%_+.~#?&/=]*")
        if urls is None or not all(list(map(lambda u: bool(is_url.match(u)), urls))):
            log.warning("Required urls parameter is missing to create link" if urls is None
                        else "Given parameter: " + str(urls) + " is no valid urls to create link")
            return {
                       "message": "Required urls parameter not set or not valid"
                   }, 400

        if wish is not None and len(wish) > 2048:
            log.info("Given wish parameter too long: " + wish)
            return {
                       "message": "Wish is too long"
                   }, 400

        if length is not None and (not (5 <= length <= 2048)):
            log.info("Given length parameter: " + str(length) + " not in desired range")
            return {
                       "message": "Length is not valid"
                   }, 400

        if click_limit is not None and (not (0 <= click_limit <= 2000000000)):
            log.info("Given clickLimit parameter: " + str(click_limit) + " not in desired range")
            return {
                       "message": "Click limit is not valid"
                   }, 400

        attempts: int = 10
        path: str = ""
        alphabet: str = string.ascii_lowercase + string.ascii_uppercase + string.digits
        while attempts > 0:
            path = wish if wish is not None else generate(alphabet, size=size)
            if not col.find_one({"path": path}):
                break
            elif wish:
                log.info("Wish: " + wish + " is already taken")
                return {
                           "message": "Wish already taken"
                       }, 409
            attempts -= 1
        if attempts == 0:
            log.info("No free path could be created with length: " + str(size))
            return {
                       "message": "No free path available, try higher length"
                   }, 409

        parsed_date: any = datetime.strptime(date, "%Y-%m-%dT%H:%M") if date else None
        master_key: str = generate(alphabet, size=32)
        # noinspection HttpUrlsUsage
        urls_with_prefix = [url if url.startswith(("http://", "https://")) else "https://" + url for url in urls]
        new_entry: {str: any} = {
            "path": path,
            "clicks": 0,
            "clickLimit": click_limit,
            "urls": urls_with_prefix,
            "password": bcrypt.hashpw(str.encode(password), bcrypt.gensalt(rounds=4)) if password else None,
            "date": parsed_date,
            "masterKey": bcrypt.hashpw(str.encode(master_key), bcrypt.gensalt(rounds=4)),
            "created": datetime.now(),
            "edited": None
        }

        col.insert_one(new_entry)
        log.info("Successfully created path: " + path + " with target: " + str(urls))
        return {
                   "path": path,
                   "urls": urls,
                   "password": password,
                   "date": datetime.strftime(parsed_date, "%d.%m.%y at %H:%M") if date else None,
                   "masterKey": master_key,
                   "message": "Created shortened url"
               }, 201

    @doc(description="Post endpoint for changing shortened link", tags=["url-shortening"])
    @use_kwargs(
        {
            "path": fields.Str(description="The old shortened path which should be updated. "
                                           "Example: 9adu2"),
            "newPath": fields.Str(description="The new shortened path after the update. "
                                              "Example: myNewPath123"),
            "passwordPlaceholder": fields.Str(description="A value to transmit, to keep the old password. "
                                                          "Example: keepOldPassword"),
            "password": fields.Str(description="The new password to protect the shortened url. "
                                               "Example: 123456"),
            "urls": fields.List(fields.Str(), description="The new target urls of the shortened url. "
                                                          'Example: ["https://otto.de"]'),
            "endDurationDate": fields.Str(description="The new end duration until shortened url is valid. "
                                                      "Example: 25-12-31T13:37"),
            "clickLimit": fields.Int(description="The new amount of clicks until the shortened url is valid. "
                                                 "Example: 200"),
            "masterKey": fields.String(description="The master key to authorize for updating the path. "
                                                   "Example: 1yYLJutiadpgLkVuT6yysMfSxg7NigTY")
        }, location="query")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="Successfully updated link")
        }
    ), code=200, description="The given path was successfully updated with the new values")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="Required path parameter is missing")
        }
    ), code=400, description="The required path parameter is missing to update a shortened url")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="Master key does not match")
        }
    ), code=401, description="The given master key parameter does not enable authorization for the protected path to "
                             "update it")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="No link found for path")
        }
    ), code=404, description="There is no link stored matching the given path")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="New path already taken")
        }
    ), code=409, description="There exists already a shortened url with the same path as the desired new path")
    def put(self, **kwargs):
        log = bind_logging(request)

        args = parser.parse_args()
        path: str = args["path"]
        new_path: str = args["newPath"]
        password_placeholder: str = args["passwordPlaceholder"]
        new_password: str = args["password"]
        new_urls: [str] = args["urls"]
        new_end_duration_date: any = args["endDurationDate"]
        new_parsed_date: any = datetime.strptime(new_end_duration_date,
                                                 "%Y-%m-%dT%H:%M") if new_end_duration_date else None
        new_click_limit: int = args["clickLimit"]
        master_key: str = args["masterKey"]

        if not path:
            log.warning("Required path parameter is missing to update something")
            return {
                       "message": "Required path parameter is missing"
                   }, 400

        entry = col.find_one({"path": path})
        if not entry:
            log.warning("No entry found for given path: " + path)
            return {
                       "message": "No link found for path"
                   }, 404

        if not master_key or not bcrypt.checkpw(str.encode(master_key), entry.get("masterKey")):
            log.warning("Verification of path: " + path + " with stored master key failed")
            return {
                       "message": "Master key does not match"
                   }, 401

        if col.find_one({"path": new_path}) and new_path != path:
            log.info("New path: " + new_path + " is already taken")
            return {
                       "message": "New path already taken"
                   }, 409

        # noinspection HttpUrlsUsage
        new_urls_with_prefix = [url if url.startswith(("http://", "https://")) else "https://" + url for url in new_urls]
        new_entry: {str: any} = {
            "path": new_path,
            "urls": new_urls_with_prefix,
            "clickLimit": new_click_limit,
            "date": new_parsed_date,
            "edited": datetime.now()
        }

        if password_placeholder == "":
            new_entry["password"] = bcrypt.hashpw(str.encode(new_password),
                                                  bcrypt.gensalt(rounds=4)) if new_password else None

        col.update_one({"path": path}, {"$set": new_entry})

        log.info("Successfully updated new path: " + new_path)
        return {
                   "message": "Successfully updated link"
               }, 200

    @doc(description="Delete endpoint for deleting shortened link", tags=["url-shortening"])
    @use_kwargs(
        {
            "path": fields.Str(description="The shortened path which should be deleted. "
                                           "Example: 9adu2"),
            "master_key": fields.Str(description="The master key to authorize for deleting the path. "
                                                 "Example: 1yYLJutiadpgLkVuT6yysMfSxg7NigTY")
        }, location="query")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="Successfully deleted")
        }
    ), code=200, description="The given path was successfully deleted")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="Required path parameter is missing")
        }
    ), code=400, description="The required path parameter is missing to delete a shortened url")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="Entry not found or master key does not match")
        }
    ), code=401, description="The given master key parameter does not enable authorization for the protected path to "
                             "delete it or there exist no shortened url for the given path parameter")
    def delete(self, **kwargs):
        log = bind_logging(request)

        args = parser.parse_args()
        path: str = args["path"]
        master_key: str = args["masterKey"]

        if not path:
            log.warning("Required path parameter is missing to delete something")
            return {
                       "message": "Required path parameter is missing"
                   }, 400

        if not master_key:
            log.warning("Required masterKey parameter is missing to delete something")
            return {
                       "message": "Required masterKey parameter is missing"
                   }, 400

        entry = col.find_one({"path": path})
        if entry and bcrypt.checkpw(str.encode(master_key), entry["masterKey"]):
            col.delete_one(entry)
            log.info("Successfully deleted path:" + path)
            return {
                       "message": "Successfully deleted"
                   }, 200

        log.warning("Cant delete non existing path: " + path if not entry
                    else "Cant delete path " + path + ", master key does not match")
        return {
                   "message": "Entry not found or master key does not match"
               }, 401  # Unauthorized
