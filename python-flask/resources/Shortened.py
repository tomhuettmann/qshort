import re
import string
from datetime import datetime

import bcrypt
# noinspection PyProtectedMember
from flask_restful import request, Resource
# noinspection PyUnresolvedReferences,PyPackageRequirements
from helpers.Logger import bind_logging
# noinspection PyUnresolvedReferences,PyPackageRequirements
from helpers.MongoCollection import col
# noinspection PyUnresolvedReferences,PyPackageRequirements
from helpers.RequestParser import parser
from nanoid import generate


class Shortened(Resource):
    @staticmethod
    def get():
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

    @staticmethod
    def post():
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

    @staticmethod
    def put():
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
        new_urls_with_prefix = [url if url.startswith(("http://", "https://")) else "https://" + url for url in
                                new_urls]
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

    @staticmethod
    def delete():
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
