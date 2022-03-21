import base64
import io
import re

import qrcode
from flask_apispec import MethodResource, doc, use_kwargs, marshal_with
from flask_restful import request
# noinspection PyUnresolvedReferences,PyPackageRequirements
from helpers.Logger import bind_logging
# noinspection PyUnresolvedReferences,PyPackageRequirements
from helpers.RequestParser import parser
from marshmallow import fields, Schema


# noinspection PyUnusedLocal
class QR(MethodResource):
    @doc(description="Post endpoint for generating QR-Codes from given shortenedUrl", tags=["qr-code"])
    @use_kwargs(
        {
            "shortenedUrl": fields.Str(description="The shortened url from which a QR-Code should be generated. "
                                                   "Example: google.de")
        },
        location="query")
    @marshal_with(Schema().from_dict(
        {
            "encodedImage": fields.Str(
                example="iVBORw0KGgoAAAANSUhEUgAAANIAAADSAQAAAAAX4qPvAAABL0lEQVR4nO2YMW7EIBRE3w+WUmIpB8hR8NVyM3yUPcBKUK"
                        "7EalKAd50ibUBhpzFmmpE1/8//hgan+gzpuOGN3/HfOQiSpOREUEFKTpKksXR24LKZbYC+VrANMLOlj5ZhuOV5tJDuiNxN"
                        "y0jc6buIvHbVMhjnJUWAfW11JKn00TIM94ATITm98qhi0fntbuCPm30knR1yOoEiICUgJCdFP3sdHX3XJwyA/fNm4J1sKJ"
                        "0d+osv8Jh3pXQ4ZyidnfpuUEHRF+qsG/3s8+7PPUBHKKmgOJLOXnnkC+zrddG+OiB/TO+XhuaSahpwmtsv5zrCqyHC5HV0"
                        "3qd1WbAtm1HjaTCdf8qd92n8zUR2BfzVNJTOnly4vMu2ep7dL6f+ooiro8vrf90TbX5pw12aPY++AWyxtvegEaI2AAAAAE"
                        "lFTkSuQmCC"),
            "message": fields.Str(example="Created QR-Code")
        }
    ), code=201, description="Successful created a QR-Code from the given shortenedUrl")
    @marshal_with(Schema().from_dict(
        {
            "message": fields.Str(example="Required shortenedUrl parameter not set or not valid")
        }
    ), code=400, description="Required shortenedUrl was not set or does not conform an url")
    def post(self, **kwargs):
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
