from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument("urls", type=str, action="append")
parser.add_argument("password", type=str)
parser.add_argument("endDurationDate", type=str)
parser.add_argument("wish", type=str)
parser.add_argument("length", type=int)
parser.add_argument("clickLimit", type=int)
parser.add_argument("shortenedUrl", type=str)
parser.add_argument("path", type=str)
parser.add_argument("masterKey", type=str)
parser.add_argument("newPath", type=str)
parser.add_argument("passwordPlaceholder", type=str)
