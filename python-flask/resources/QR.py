import base64
import io
import re

import qrcode
# noinspection PyProtectedMember
from flask_restful import request, Resource
# noinspection PyUnresolvedReferences,PyPackageRequirements
from helpers.Logger import bind_logging
# noinspection PyUnresolvedReferences,PyPackageRequirements
from helpers.RequestParser import parser


class QR(Resource):
    @staticmethod
    def post():
        log = bind_logging(request)

        args = parser.parse_args()
        shortened_url: str = args["shortenedUrl"]

        is_url = re.compile("(https?://)?[-a-zA-Z0-9@:%._+~#=]{2,256}\.[a-z]{2,6}[-a-zA-Z0-9@:%_+.~#?&/=]*")
        if shortened_url is None or not is_url.match(shortened_url):
            log.warning(
                "Required shortenedUrl parameter is missing to generate QR-Code" if shortened_url is None
                else "Given parameter: " + str(shortened_url) + " is no valid url to generate a QR-Code")
            return {
                       "message": "Required shortenedUrl parameter not set or not valid"
                   }, 400

        buffer = io.BytesIO()
        qrcode.make(shortened_url, border=0).save(buffer)
        encoded_string = base64.b64encode(buffer.getvalue())

        log.info("Successfully generated QR-Code for input: " + shortened_url)
        return {
                   "encodedImage": encoded_string.decode("utf-8"),
                   "message": "Created QR-Code"
               }, 201
