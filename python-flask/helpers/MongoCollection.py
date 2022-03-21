from pymongo import MongoClient

# MongoDB Database and Collection for storing and accessing shortened Urls
db = MongoClient(host="mongo")["qshort"]
col = db["shortenedUrls"]
