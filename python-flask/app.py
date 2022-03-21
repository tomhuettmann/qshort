import json
from datetime import datetime

import bcrypt
from flask import Flask, request, render_template, redirect
from flask_restful import Api
from pymongo import DESCENDING
from werkzeug.exceptions import NotFound

from helpers.Logger import bind_logging
from helpers.MongoCollection import col
from resources.QR import QR
from resources.Shortened import Shortened
from resources.Validation import Validation

app = Flask(__name__)
api = Api(app, prefix="/api")
api.add_resource(Shortened, "/url")
api.add_resource(QR, "/qr")
api.add_resource(Validation, "/validate")


@app.route("/")
def index():
    log = bind_logging(request)

    log.info("Successfully opened index")
    return render_template("index.html")


@app.route("/<url_path>")
def redirect_endpoint(url_path):
    log = bind_logging(request)

    entry = col.find_one({"path": url_path})
    if not entry:
        log.info("Tried to access non existing path: " + str(url_path))
        return render_template("sorry.html",
                               message="No entry found. You either have a typo or someone deleted this link.",
                               code=404)

    end_duration_date = entry["date"]
    if end_duration_date and end_duration_date < datetime.now():
        log.info("Tried to access expired path: " + str(url_path))
        return render_template("sorry.html",
                               message="The link already expired " + datetime.strftime(end_duration_date,
                                                                                       "%d.%m.%y at %H:%M") + ".",
                               code=403)

    click_limit = entry["clickLimit"]
    if click_limit and entry["clicks"] >= click_limit:
        log.info("Tried to access click limit reached path: " + str(url_path))
        return render_template("sorry.html",
                               message="The click limit of the link is reached.",
                               code=403)

    stored_password: str = json.loads(request.cookies.get("storedPasswords")).get(url_path) if request.cookies.get(
        "storedPasswords") else None
    if stored_password and entry["password"] and not bcrypt.checkpw(str.encode(stored_password), entry["password"]):
        log.warning("Tried to access password protected path: " + str(url_path) + " with wrong password")
        return render_template("password.html",
                               url_path=url_path,
                               wrong_password=True)

    if not stored_password and entry["password"]:
        log.info("Access password protected path: " + str(url_path))
        return render_template("password.html",
                               url_path=url_path,
                               wrong_password=False)

    col.update_one({"path": url_path}, {"$set": {"clicks": entry["clicks"] + 1}})
    urls = entry["urls"]
    log.info("Successfully resolved path: " + str(url_path))
    if len(urls) == 1:
        redirected_url = urls[0]
        log.info("Successfully redirected to " + redirected_url)
        return redirect(redirected_url, code=302)
    else:
        log.info("Successfully show urls " + str(urls))
        return render_template("urls.html",
                               url_path=url_path,
                               urls=urls)


@app.route("/myLinks")
def my_links():
    log = bind_logging(request)

    stored_master_keys_cookie = request.cookies.get("storedMasterKeys")
    stored_master_keys_dict: {} = json.loads(stored_master_keys_cookie) if stored_master_keys_cookie else {}

    col_entries_matching_stored_my_links_paths = list(
        col.find({"$or": [{"path": e} for e in stored_master_keys_dict.keys()]})) if stored_master_keys_dict else []
    entries_matching_stored_master_key = list(filter(
        lambda entry: bcrypt.checkpw(str.encode(stored_master_keys_dict[entry["path"]]), entry["masterKey"]),
        col_entries_matching_stored_my_links_paths))

    matching_paths = list(map(lambda e: e["path"], entries_matching_stored_master_key))
    log.info("Successfully show own matching paths " + str(matching_paths))
    return render_template("my_links.html",
                           links=matching_paths)


@app.route("/view/<url_path>")
def view_link(url_path):
    log = bind_logging(request)

    stored_master_key_cookie = request.cookies.get("storedMasterKeys")
    stored_master_key_for_path = json.loads(stored_master_key_cookie).get(url_path) if stored_master_key_cookie else {}
    entry = col.find_one({"path": url_path})

    if not stored_master_key_for_path or not bcrypt.checkpw(str.encode(stored_master_key_for_path),
                                                            entry["masterKey"]):
        log.warning("Tried to access view of path: " + str(url_path) + " with non matching master key")
        return render_template("sorry.html",
                               message="The stored master key does not match. "
                                       "Therefore you have no access rights for this.",
                               code=401)

    if entry:
        log.info("Successfully show view of path: " + str(url_path))
        return render_template("view_link.html",
                               link=url_path,
                               targets=entry["urls"],
                               clicks=entry["clicks"],
                               click_limit=entry["clickLimit"],
                               has_password=entry["password"] is not None,
                               end_duration=datetime.strftime(entry["date"], "%d.%m.%y at %H:%M (UTC+1h)") if entry[
                                   "date"] else None,
                               created=datetime.strftime(entry["created"], "%d.%m.%y at %H:%M (UTC+1h)") if entry[
                                   "created"] else None,
                               edited=datetime.strftime(entry["edited"], "%d.%m.%y at %H:%M (UTC+1h)") if entry[
                                   "edited"] else None)
    else:
        log.info("Tried to access view of non existing path: " + str(url_path))
        return render_template("sorry.html",
                               message="No entry found. You either have a typo or someone deleted this link.",
                               code=404)


@app.route("/edit/<url_path>")
def edit_link(url_path):
    log = bind_logging(request)

    stored_master_key_cookie = request.cookies.get("storedMasterKeys")
    stored_master_key_for_path = json.loads(stored_master_key_cookie).get(url_path) if stored_master_key_cookie else {}
    entry = col.find_one({"path": url_path})

    if not stored_master_key_for_path or not bcrypt.checkpw(str.encode(stored_master_key_for_path),
                                                            entry["masterKey"]):
        log.warning("Tried to access edit of path: " + str(url_path) + " with non matching master key")
        return render_template("sorry.html",
                               message="The stored master key does not match. "
                                       "Therefore you have no access rights for this.",
                               code=401)

    if entry:
        log.info("Successfully show edit of path: " + str(url_path))
        return render_template("edit_link.html",
                               link=url_path,
                               hashed_password=entry["password"].decode("utf-8") if entry["password"] else "",
                               target="\n".join(entry["urls"]),
                               end_duration=datetime.strftime(entry["date"], "%Y-%m-%dT%H:%M") if entry["date"] else "",
                               click_limit=entry["clickLimit"])
    else:
        log.info("Tried to access edit of non existing path: " + str(url_path))
        return render_template("sorry.html",
                               message="No entry found. You either have a typo or someone deleted this link.",
                               code=404)


@app.route("/recentLinks")
def recent_links():
    log = bind_logging(request)

    entries = col.find({
        "password": None,
        "$and": [
            {"$or": [
                {"date": None},
                {"date": {"$gt": datetime.now()}}
            ]},
            {"$or": [
                {"clickLimit": None},
                {"$expr": {"$lt": ["$clicks", "$clickLimit"]}}
            ]}
        ]
    }).sort("created", DESCENDING).limit(100)

    url_targets_of_entries = [e.get("urls") for e in entries]
    log.info(
        "Successfully show recent " + str(len(url_targets_of_entries)) + " url targets: " + str(url_targets_of_entries))
    return render_template("recent_links.html",
                           url_amount=sum(map(lambda ts: len(ts), url_targets_of_entries)),
                           targets=url_targets_of_entries)


@app.errorhandler(NotFound)
def not_found(ex):
    log = bind_logging(request)

    log.warning("Not found", error=str(ex))
    return render_template("sorry.html",
                           message="Path not found.",
                           code=404)


app.run(host="0.0.0.0", port=5000)
